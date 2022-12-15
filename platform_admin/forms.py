from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.forms.widgets import ClearableFileInput
from django.core.exceptions import ValidationError

from exam.models import StudentGroup, Platform, Term, Grade
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

class ClearableFileInputPL(ClearableFileInput):
    clear_checkbox_label = 'Wyczyść'
    initial_text = 'Obecny'
    input_text = 'Nowy'

class EditPlatformForm(forms.ModelForm):
    class Meta:
        model = Platform
        fields = ["name","logo"]
    name = forms.CharField(label="Nazwa platformy", widget=forms.Textarea(attrs={'name':'text', 'rows':4, 'cols':170}))
    logo = forms.ImageField(required=False, widget=ClearableFileInputPL)

class ChangeTermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ["time"]

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ["name","bar","platform"]
    name = forms.CharField(label="", widget=forms.TextInput(attrs={"class":"form-control"}))

    def clean_bar(self):
        data = self.cleaned_data['bar']
        if data < 0:
            raise ValidationError("Pułap nie może być ujemny")
        if data > 100:
            raise ValidationError("Ocena nie może być przyznawana powyżej 100%")
        return data

class FeedbackForm(forms.Form):
    points = forms.ChoiceField(required=True, label = "Na ile oceniasz aplikacje Examiner w skali od 1 do 5?",
        choices=[('1','1'),('2','2'),("3","3"),("4","4"), ("5","5")])
    feedback = forms.CharField(required=False, label = "Uwagi słowne:", 
        widget=forms.Textarea(attrs={'name':'text', 'rows':4, 'cols':170}))