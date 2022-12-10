from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

from exam.models import StudentGroup, Platform, Term
class UserNameChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ["username"]
    username = forms.CharField(label="", widget=forms.TextInput(attrs={"class":"form-control"}))

class StudentGroupForm(forms.ModelForm):
    class Meta:
        model = StudentGroup
        fields = ["name"]
    name = forms.CharField(label="Nazwa grupy", widget=forms.TextInput(attrs={"class":"form-control"}))

class AttachStudentForm(forms.Form):
    student = forms.CharField(label="Nazwa użytkownika studenta", widget=forms.TextInput(attrs={"class":"form-control"}))
    group = forms.ModelChoiceField(queryset=StudentGroup.objects.all())

class ReverseAttachStudentForm(forms.Form):
    group = forms.CharField(label="Nazwa grupy", widget=forms.TextInput(attrs={"class":"form-control"}))

class AttachCourseForm(forms.Form):
    course = forms.CharField(label="Nazwa kursu", widget=forms.TextInput(attrs={"class":"form-control"}))
    term = forms.DateTimeField(label="Data ukończenia kursu", widget=forms.TextInput(attrs={"class":"form-control"}))
    group = forms.ModelChoiceField(queryset=StudentGroup.objects.all())

class EditPlatformForm(forms.ModelForm):
    class Meta:
        model = Platform
        fields = ["name","logo"]
    name = forms.CharField(label="Nazwa platformy", widget=forms.Textarea(attrs={'name':'text', 'rows':4, 'cols':170}))

class ChangeTermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ["time"]