from django import forms
from django.utils.translation import gettext_lazy as _


class StudentSearchCourseForm(forms.Form):
    name = forms.CharField(label="Wyszukaj po nazwie", widget=forms.TextInput(attrs={"class":"form-control"}))

class StudentSearchStatusForm(forms.Form):
    CHOICES= (
    ('1','Niezaliczony'),
    ('2','Zaliczony'),
    ('3','Jeszcze nie ukończony'),
    )
    status = forms.ChoiceField(widget=forms.Select, choices=CHOICES)