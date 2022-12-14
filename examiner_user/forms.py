from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.forms.widgets import ClearableFileInput
from django.core.exceptions import ValidationError

from exam.models import Course, Question, Lesson

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name","category", "platform"]
    name = forms.CharField(label=_("Course name"), widget=forms.TextInput(attrs={"class":"form-control"}))
    category = forms.CharField(required=False, label=_("Category (optional)"), widget=forms.TextInput(attrs={"class":"form-control"}))

class CourseEditForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "category", "time","question_amount", "attempt_amount", "test_ready", "passing_score", "platform"]
    name = forms.CharField(label=_("Course name"), widget=forms.TextInput(attrs={"class":"form-control"}))
    category = forms.CharField(required=False, label=_("Category (optional)"), widget=forms.TextInput(attrs={"class":"form-control"}))

class RadioForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["multiple_answer_questions"]
    multiple_answer_questions = forms.BooleanField(required=False, label=_("Multiple choice questions"))

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text","answer1","answer2","answer3","answer4","answer5","correct_answers", "course"]

    text = forms.CharField(label = "", widget=forms.Textarea(attrs={'name':'text', 'rows':4, 'cols':170}))
    answer1 = forms.CharField(label = _("Answer nr.1"), widget=forms.TextInput(attrs={"class":"form-control"}))
    answer2 = forms.CharField(label = _("Answer nr.2"), widget=forms.TextInput(attrs={"class":"form-control"}))
    answer3 = forms.CharField(required=False, label = _("Answer nr.3"), widget=forms.TextInput(attrs={"class":"form-control"}))
    answer4 = forms.CharField(required=False, label = _("Answer nr.4"), widget=forms.TextInput(attrs={"class":"form-control"}))
    answer5 = forms.CharField(required=False, label = _("Answer nr.5"), widget=forms.TextInput(attrs={"class":"form-control"}))
    correct_answers = forms.ChoiceField(required=False, label = "", choices=[('1',''),('2',''),("3",""),("4",""), ("5","")])
    course = forms.ModelChoiceField(queryset=Course.objects.all())

    def clean(self):
        cleaned_data = super().clean()
        correct_answers = cleaned_data.get("correct_answers")
        for n in range(3,6):
            if f"{n}" in correct_answers:
                if not cleaned_data.get(f"answer{n}"):
                    raise ValidationError(
                    _("Correct answer was incorrectly marked")
                )

class QuestionFormMultiple(QuestionForm):
    correct_answers = forms.CharField(label = "")

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["material","topic","course"]
    topic = forms.CharField( widget=forms.TextInput(attrs={"class":"form-control"}))

class NoCurrentFileInput(ClearableFileInput):
    initial_text = _('Present')
    input_text = _('New')

class LessonEditForm(LessonForm):
    material = forms.FileField(widget=NoCurrentFileInput)

class AttachStudentForm(forms.Form):
    student = forms.ModelChoiceField(queryset=User.objects.filter(groups = 2))
    course = forms.ModelChoiceField(queryset=Course.objects.all())

class AttachStudentTextForm(AttachStudentForm):
    student = forms.CharField(label=_("Student username"), widget=forms.TextInput(attrs={"class":"form-control"}))

class AttachStudentTextForm(forms.Form):
    student = forms.ModelChoiceField(queryset=User.objects.filter(groups = 2))
    group =  forms.CharField(label=_("Group name"), widget=forms.TextInput(attrs={"class":"form-control"}))

class LessonRenameForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["topic", "course"]
    topic = forms.CharField( widget=forms.TextInput(attrs={"class":"form-control"}))

class AttachCourseToGroupForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all())
    group =  forms.CharField(label=_("Group name"), widget=forms.TextInput(attrs={"class":"form-control"}))
    deadline = forms.DateTimeField(label=_("Deadline"), widget=forms.TextInput(attrs={"class":"form-control"}))