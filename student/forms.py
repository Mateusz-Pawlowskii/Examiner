from django import forms
from django.utils.translation import gettext_lazy as _


class StudentSearchCourseForm(forms.Form):
    name = forms.CharField(label=_("Search by name"), widget=forms.TextInput(attrs={"class":"form-control"}))

class StudentSearchStatusForm(forms.Form):
    CHOICES= (
    ('1',_('Failed')),
    ('2',_('Passed')),
    ('3',_('Unfinished')),
    )
    status = forms.ChoiceField(widget=forms.Select, choices=CHOICES)