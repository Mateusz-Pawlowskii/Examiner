from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.forms.widgets import ClearableFileInput
from django.core.exceptions import ValidationError

from exam.models import StudentGroup, Platform, Deadline, Grade
class UserNameChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ["username"]
    username = forms.CharField(label="", widget=forms.TextInput(attrs={"class":"form-control"}))

class StudentGroupForm(forms.ModelForm):
    class Meta:
        model = StudentGroup
        fields = ["name", "platform"]
    name = forms.CharField(label=_("Group name"), widget=forms.TextInput(attrs={"class":"form-control"}))

class AttachStudentForm(forms.Form):
    student = forms.CharField(label=_("Student username"), widget=forms.TextInput(attrs={"class":"form-control"}))
    group = forms.ModelChoiceField(queryset=StudentGroup.objects.all())

class ReverseAttachStudentForm(forms.Form):
    group = forms.CharField(label=_("Group name"), widget=forms.TextInput(attrs={"class":"form-control"}))

class AttachCourseForm(forms.Form):
    course = forms.CharField(label=_("Course name"), widget=forms.TextInput(attrs={"class":"form-control"}))
    deadline = forms.DateTimeField(label=_("Course deadline"), widget=forms.TextInput(attrs={"class":"form-control"}))
    group = forms.ModelChoiceField(queryset=StudentGroup.objects.all())

class ClearableFileInputPL(ClearableFileInput):
    clear_checkbox_label = _('Clear')
    initial_text = _('Present')
    input_text = _('New')

class EditPlatformForm(forms.ModelForm):
    class Meta:
        model = Platform
        fields = ["name","logo"]
    name = forms.CharField(label=_("Platform name"), widget=forms.Textarea(attrs={'name':'text', 'rows':4, 'cols':170}))
    logo = forms.ImageField(required=False, widget=ClearableFileInputPL)

class ChangeDeadlineForm(forms.ModelForm):
    class Meta:
        model = Deadline
        fields = ["time"]

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ["name","bar","platform"]
    name = forms.CharField(label="", widget=forms.TextInput(attrs={"class":"form-control"}))

    def clean_bar(self):
        data = self.cleaned_data['bar']
        if data < 0:
            raise ValidationError(_("Percentage bar can't be negative"))
        if data > 100:
            raise ValidationError(_("Grade can't be given above 100%"))
        return data

class FeedbackForm(forms.Form):
    points = forms.ChoiceField(required=True, label = _("How would you score Examiner aplication overall on a 1 to 5 scale?"),
        choices=[('1','1'),('2','2'),("3","3"),("4","4"), ("5","5")])
    ease_of_use = forms.ChoiceField(required=True, label = _("How would you score ease of use of Examiner aplication on a 1 to 5 scale?"),
        choices=[('1','1'),('2','2'),("3","3"),("4","4"), ("5","5")])
    looks = forms.ChoiceField(required=True, label = _("How would you score eastetic appeal of this application on a 1 to 5 scale?"),
        choices=[('1','1'),('2','2'),("3","3"),("4","4"), ("5","5")])
    feedback = forms.CharField(required=False, label = _("Feedback"), 
        widget=forms.Textarea(attrs={'name':'text', 'rows':4, 'cols':170}))