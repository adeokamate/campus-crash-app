from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Chat
import re
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model


class RegisterForm(UserCreationForm):
    class Meta:
        model = User

        fields = ["username","student_email","first_name", "last_name" ,"profile_pic" ,"academic_year", "course", "tribe", "student_number","date_of_birth" ,"password1", "password2"]

    '''def clean_email(self):
        email = self.cleaned_data.get("email")
        if not re.match(r"^[a-zA-Z]+\.[a-zA-Z]+@students\.mak\.ac\.ug$", email):
            raise forms.ValidationError("Please enter a valid Makerere University email.")
        return email
'''
class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['message', 'attachment']

        
class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        #user = get_user_model()
        fields = ["username","password"]

    