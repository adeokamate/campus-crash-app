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
from django.http import HttpResponseForbidden
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .models import Chat
from django.db.models import Q
from .forms import ChatForm
from django.db import models
from django.contrib.auth import authenticate,login,logout
from .forms import LoginForm 
from django.contrib.auth import get_user_model
User = get_user_model()
import time, random
from .forms import ProfileUpdateForm
from .forms import SupportForm

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        return redirect('campus_crash:home')  # Redirect to home if user is already logged in
    
    timestamp = int(time.time())  # Get the current timestamp
    context = {
        'timestamp': timestamp
    }
    return render(request, 'index.html', context)


# ✅ Register View with Email Verification
def generate_unique_token():
    return get_random_string(length=64)  # Or your token generation strategy



def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST,request.FILES)

        if form.is_valid():
            email = form.cleaned_data.get("student_email")

            # Check if the email already exists
            if User.objects.filter(student_email=email).exists():
                messages.error(request, "This email is already registered.")
                return render(request, "signup.html", {"form": form})

            # Proceed with user creation
            user = form.save(request)
            user.is_active = False  # Don't activate the user until email is verified
            verify_email(user)  # ✅ Send the code via email

        # Store user ID in session for later verification
            request.session['pending_user_id'] = user.id
            return redirect('campus_crash:verify_code') 
            
      
        else:
            print(form.errors.as_data())
            return render(request, "signup.html", {"form": form})

    else:
        form = RegisterForm()
    return render(request, "signup.html", {"form": form})


# ✅ Email Verification View

def generate_code():
    return str(random.randint(100000, 999999))

def verify_email(user):
    code = generate_code()
    user.verification_code = code
    user.save()

    send_mail(
    'Your Kampus Crush Verification Code',
    f'Hello {user.username}, your verification code is: {code}',
    'noreply@kampuscrush.com',
    [user.student_email],
    fail_silently=False,
)

def verify_code(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        return redirect('campus_crash:register')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        code = request.POST.get('code')
        if code == user.verification_code:
            user.is_active = True
            user.email_verified = True
            user.verification_code = {code}
            user.save()
            messages.success(request, "Email verified successfully. You can now log in.")
            return redirect('campus_crash:index')
        else:
            messages.error(request, "Incorrect verification code.")

    return render(request, 'verify_code.html')


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
                return redirect('campus_crash:home')
            else:
                messages.error(request,'Invalid Username or Password')
                return redirect('campus_crash:index')
    else:
        form = LoginForm()
    return render(request,'login.html',{'form':form})


@login_required
def home(request):
    user = request.user
    chats = Chat.objects.filter(models.Q(sender=user) | models.Q(receiver=user)).order_by('-timestamp')[:5]
   

    return render(request, 'home.html', {
        'user': user,
        'chats': chats,
        
    })





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
            return redirect('campus_crash:chat_with_user', user_id=other_user.id)

    else:
        form = ChatForm()

    return render(request, 'chat/chat_room.html', {
        'messages': messages,
        'other_user': other_user,
        'form': form
    })
@login_required
def messages_view(request):
    # Get all chats where the user is either the sender or receiver
    chats = Chat.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')

    return render(request, 'messages.html', {'chats': chats})
@login_required
def logout_user(request):
    messages.success(request, "logout successful \n please login")
    logout(request)
    return redirect('campus_crash:index')

@login_required
def user_list(request):
    users = User.objects.all()  # Get all users to display in the list
    return render(request, 'user_list.html', {'users': users})

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    # Only the sender or receiver can view the chat
    if request.user != chat.sender and request.user != chat.receiver:
        return HttpResponseForbidden("You are not allowed to view this chat.")

    return render(request, 'chat_detail.html', {'chat': chat})


@login_required
def match_make(request):
    current_user = request.user

    potential_matches = User.objects.exclude(id=current_user.id)

    matches = []

    for user in potential_matches:
        match_score = 0

        if user.age_bracket() == current_user.age_bracket():
            match_score += 1
        if user.academic_year == current_user.academic_year:
            match_score += 1
        if user.course == current_user.course:
            match_score += 1
        if user.tribe == current_user.tribe:
            match_score += 1

        if match_score > 0:
            matches.append({
                'user': user,
                'score': match_score
            })

    # Sort matches by best score (descending)
    matches.sort(key=lambda x: x['score'], reverse=True)

    context = {
        'matches': matches,
    }
    return render(request, 'match_make.html', context)

@login_required
def settings_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('campus_crash:settings')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'settings.html', {'form': form})

  # Ensure this form is defined correctly

@login_required
def support_view(request):
    if request.method == 'POST':
        form = SupportForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            full_message = f"From: {name} <{email}>\n\nMessage:\n{message}"

            try:
                send_mail(
                    subject="Support Request",
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['deoakamate@gmail.com'],
                    fail_silently=False,
                )
                messages.success(request, "Your message has been sent.")
                return redirect('campus_crash:support')
            except Exception as e:
                messages.error(request, f"Failed to send message: {e}")
    else:
        form = SupportForm()

    return render(request, 'support.html', {'form': form})
