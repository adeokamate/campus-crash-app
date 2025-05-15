from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm
from .models import User, Chat
import random
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
    
from django.contrib.auth.forms import PasswordChangeForm


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        age = forms.IntegerField(min_value=18)
        course = forms.CharField(
    max_length=200,
    widget=forms.TextInput(attrs={
        'placeholder': 'ENTER ONLY THE COURSE CODE e.g BCOM, BSCSC,'
    })
)
        fields = ["username","student_email","first_name", "age","last_name" ,"profile_pic" ,"academic_year", "course", "tribe","password1", "password2"]

    def Clean_email(self):
        email = self.cleaned_data.get('email')

        
        #if not email.endswith('@gmail.com'):
        if not email.endswith('@students.mak.ac.ug'):
            raise forms.ValidationError("Please your email must end with  @students.mak.ac.ug email.")
        return email
    def save(self,request):
    
        user = super().save(request)
        user.age = self.cleaned_data['age']
      

        # Set verification
        code = str(random.randint(100000, 999999))
        user.verification_code = code
        user.is_active = False  # temporarily deactivate
        user.save()
       

        request.session['pending_user_id'] = user.id  # Store for verification

        send_mail(
            subject="Campus Crush Email Verification",
            message=f"Hello {user.username},\n\nYour verification code is: {code}",
            from_email="no-reply@campuscrush.com",
            recipient_list=[user.student_email],
            fail_silently=False,
        )

        return user

class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['message', 'attachment']

        
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})




class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'age',
            'student_email',
            'password',
            'profile_pic',
            'bio',
            'course',
            'academic_year',
            'tribe',
        ]
        widgets = {
            'password': forms.PasswordInput(),
        }



class SupportForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)