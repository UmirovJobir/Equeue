from django import forms
from .models import *

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(attrs={'style': 'width: 100px;'}),
            'last_name': forms.TextInput(attrs={'style': 'width: 100px;'}),
            'patronymic': forms.TextInput(attrs={'style': 'width: 100px;'}),
            'phone': forms.TextInput(attrs={'style': 'width: 100px;'}),
            'duration': forms.TextInput(attrs={'style': 'width: 100px;'}),
        }
