from django.contrib.auth.models import User
from django.db import models
import json
from django.core.files.storage import FileSystemStorage


logo_fs = FileSystemStorage(location='media/logos', base_url="/media/logos")
lesson_fs = FileSystemStorage(location='media/lessons', base_url="/media/lessons")

# Create your models here.
class Platform(models.Model):
    name = models.CharField(max_length = 3000)
    users = models.ManyToManyField(User)
    logo = models.ImageField(storage=logo_fs, blank=True, null=True)

class Course(models.Model):
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
    platform = models.ForeignKey(Platform, on_delete = models.CASCADE, blank=True, null=True)

class StudentGroup(models.Model):
    name = models.CharField(max_length = 100)
    platform = models.ForeignKey(Platform, on_delete = models.CASCADE, blank=True, null=True)
    students = models.ManyToManyField(User)
    courses = models.ManyToManyField(Course)

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete = models.CASCADE)
    topic = models.CharField(max_length=100)
    material = models.FileField(storage=lesson_fs)

    def delete(self, *args, **kwargs):
        self.material.delete(self.material.name)
        super().delete(*args,**kwargs)

class Result(models.Model):
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
    text = models.CharField(max_length = 1000)
    answer1 = models.CharField(max_length = 200)
    answer2 = models.CharField(max_length = 200)
    answer3 = models.CharField(max_length = 200, blank = True, null = True)
    answer4 = models.CharField(max_length = 200, blank = True, null = True)
    answer5 = models.CharField(max_length = 200, blank = True, null = True)
    correct_answers = models.CharField(max_length = 50)
    course = models.ForeignKey(Course, on_delete = models.CASCADE, blank = True, null = True)

class Term(models.Model):
    course = models.ForeignKey(Course, on_delete = models.CASCADE)
    group = models.ForeignKey(StudentGroup, on_delete = models.CASCADE)
    time = models.DateTimeField(null=True)