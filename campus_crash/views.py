from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.db import IntegrityError
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.crypto import get_random_string
from django.contrib.auth.tokens import default_token_generator
from .forms import RegisterForm
from .models import User
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .models import Chat
from django.db.models import Q
from .forms import ChatForm

from django.contrib.auth import authenticate,login,logout
from .forms import LoginForm 
from django.contrib.auth import get_user_model
User = get_user_model()
import time

# Create your views here.
from django.shortcuts import render


def index(request):
    timestamp = int(time.time())  # Get the current timestamp
    context = {
        'timestamp': timestamp
    }
    return render(request, 'index.html', context)




def user_list(request):
    users = User.objects.all()  # Get all users to display in the list
    return render(request, 'user_list.html', {'users': users})

def notifications(request):
    return render(request, 'notifications.html')

# def messages(request):
#     return render(request, 'messages.html')

def settings(request):
    return render(request, 'settings.html')

def logout_user(request):
    messages.success(request, "logout successful \n please login")
    logout(request)
    return redirect('campus_crash:login')


# ✅ Register View with Email Verification
def generate_unique_token():
    return get_random_string(length=64)  # Or your token generation strategy



def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("student_email")

            # Check if the email already exists
            if User.objects.filter(student_email=email).exists():
                messages.error(request, "This email is already registered.")
                return render(request, "signup.html", {"form": form})

            # Proceed with user creation
            user = form.save(commit=False)
            user.is_active = False  # Don't activate the user until email is verified
            user.save()

            # Generate the Verification Token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = f"http://127.0.0.1:8000/verify/{uid}/{token}"

            # Send Verification Email
            send_mail(
                "Verify Your Makerere Account",
                f"Click the link to verify your account: {verification_link}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            messages.success(request, "Account created! Please check your email to verify.")
            return redirect("campus_crash:login")
        else:
            print(form.errors.as_data())
            return render(request, "signup.html", {"form": form})

    else:
        form = RegisterForm()
    return render(request, "signup.html", {"form": form})


# ✅ Email Verification View
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_verified = True
            user.save()
            messages.success(request, "Email verified! You can now log in.")
            return redirect("campus_crash:login")
        else:
            messages.error(request, "Invalid verification link.")
    except:
        messages.error(request, "Verification failed.")
    
    return redirect("campus_crash:signup")

def login_user(request):
   if request.method == "POST":
       
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect('campus_crash:index')
        else:
            messages.success(request,('Login not successful something happened please try Again....'))
            return redirect('campus_crash:login')
   else:
       return render(request,'login.html',{})
       

def login_user(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username = username,password=password)
            

            if user is not None:
                login(request,user)
                messages.success(request, 'login successful!')
                return redirect('campus_crash:index')
            else:
                messages.error(request,'Invalid Username or Password')
    else:
        form = LoginForm()
        return render(request,'login.html',{'form':form})

       
@login_required

def chat_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    messages = Chat.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')
 
    if request.method == 'POST':
        form = ChatForm(request.POST, request.FILES)
        if form.is_valid():
            chat = form.save(commit=False)
            chat.sender = request.user
            chat.receiver = other_user
            chat.save()
            return redirect('campus_crash:chat_room', user_id=other_user.id)
    else:
        form = ChatForm()

    return render(request, 'chat/chat_room.html', {
        'messages': messages,
        'other_user': other_user,
        'form': form
    })

