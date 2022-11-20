from django.contrib import admin

from .models import Course, Question, Result, Lesson, Platform, StudentGroup
# Register your models here.
admin.site.register(Course)
admin.site.register(Question)
admin.site.register(Result)
admin.site.register(Lesson)
admin.site.register(Platform)
admin.site.register(StudentGroup)