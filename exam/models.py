from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
import os
import json
import uuid
from django.core.files.storage import FileSystemStorage


logo_fs = FileSystemStorage(location='media/logos', base_url="/media/logos")
lesson_fs = FileSystemStorage(location='media/lessons', base_url="/media/lessons")

# Create your models here.
class Platform(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length = 3000)
    users = models.ManyToManyField(User)
    logo = models.ImageField(storage=logo_fs, blank=True, null=True)
    inactive = models.BooleanField(default = False)
    student_limit = models.PositiveSmallIntegerField(default=0)
    course_limit = models.PositiveSmallIntegerField(default=0)
    group_limit = models.PositiveSmallIntegerField(default=0)
    student_per_group_limit = models.PositiveSmallIntegerField(default=0)
    course_per_group_limit = models.PositiveSmallIntegerField(default=0)
    lesson_per_course_limit = models.PositiveSmallIntegerField(default=0)
    changable_logo = models.BooleanField(default = True)

class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    students = models.ManyToManyField(User)
    name = models.CharField(max_length = 100)
    multiple_answer_questions = models.BooleanField(default=False)
    time = models.PositiveSmallIntegerField(default=0)
    question_amount = models.PositiveSmallIntegerField(default=0)
    lesson_amount = models.PositiveSmallIntegerField(default=0)
    attempt_amount = models.PositiveSmallIntegerField(default=3)
    test_ready = models.BooleanField(default=False)
    passing_score = models.PositiveSmallIntegerField(default=0)
    category = models.CharField(max_length=100, default="")
    platform = models.ForeignKey(Platform, on_delete = models.CASCADE)

class StudentGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length = 100)
    platform = models.ForeignKey(Platform, on_delete = models.CASCADE)
    students = models.ManyToManyField(User)
    courses = models.ManyToManyField(Course)

class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete = models.CASCADE)
    topic = models.CharField(max_length=100)
    material = models.FileField(storage=lesson_fs)

    def delete(self, *args, **kwargs):
        self.material.delete(self.material.name)
        super().delete(*args,**kwargs)

class Grade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length = 100)
    bar = models.PositiveSmallIntegerField()
    platform = models.ForeignKey(Platform, on_delete = models.CASCADE)

class Result(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete = models.CASCADE)
    student = models.ForeignKey(User, on_delete = models.CASCADE)
    finished = models.BooleanField(default = False)
    current_score = models.PositiveSmallIntegerField(default = False)
    current_question = models.PositiveSmallIntegerField(default = 1)
    question_order = models.CharField(max_length=2000, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    passed = models.BooleanField(default = False)

    def set_order(self, x):
        self.question_order = json.dumps(x)

    def get_order(self):
        return json.loads(self.question_order)

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length = 1000)
    answer1 = models.CharField(max_length = 200)
    answer2 = models.CharField(max_length = 200)
    answer3 = models.CharField(max_length = 200, blank = True, null = True)
    answer4 = models.CharField(max_length = 200, blank = True, null = True)
    answer5 = models.CharField(max_length = 200, blank = True, null = True)
    correct_answers = models.CharField(max_length = 50)
    course = models.ForeignKey(Course, on_delete = models.CASCADE, blank = True, null = True)

class Deadline(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete = models.CASCADE)
    group = models.ForeignKey(StudentGroup, on_delete = models.CASCADE)
    time = models.DateTimeField(null=True)

class Activity(models.Model):
    kind = models.CharField(max_length = 50)
    time = models.DateTimeField(auto_now_add=True)

@receiver(models.signals.post_delete, sender=Lesson)
def auto_delete_material_on_delete(sender, instance, **kwargs):
    """Deletes file when lesson is deleted"""
    if instance.material:
        if os.path.isfile(instance.material.path):
            os.remove(instance.material.path)

@receiver(models.signals.pre_save, sender=Lesson)
def auto_delete_material_on_change(sender, instance, **kwargs):
    """Deletes old file when new lesson material is uploaded"""
    if not instance.pk:
        return False

    try:
        old_file = Lesson.objects.get(pk=instance.pk).material
    except Lesson.DoesNotExist:
        return False

    new_file = instance.material
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

@receiver(models.signals.post_delete, sender=Platform)
def auto_delete_logo_on_delete(sender, instance, **kwargs):
    """Deletes logo when platform is deleted"""
    if instance.logo:
        if os.path.isfile(instance.logo.path):
            os.remove(instance.logo.path)

@receiver(models.signals.pre_save, sender=Platform)
def auto_delete_logo_on_change(sender, instance, **kwargs):
    """Deletes old logo when new one is uploaded"""
    if not instance.pk:
        return False

    try:
        try:
            old_file = Platform.objects.get(pk=instance.pk).logo
        except Platform.DoesNotExist:
            return False

        new_file = instance.logo
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except:
        pass