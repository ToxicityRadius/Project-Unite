from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),
    )
    student_number = forms.CharField(
        max_length=7,
        min_length=7,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Student Number (7 digits)'}),
        help_text='Enter a unique 7-digit student number.'
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'student_number', 'password1', 'password2')

    def clean_student_number(self):
        student_number = self.cleaned_data.get('student_number')
        if not student_number.isdigit():
            raise forms.ValidationError('Student number must contain only digits.')
        if len(student_number) != 7:
            raise forms.ValidationError('Student number must be exactly 7 digits.')
        return student_number
