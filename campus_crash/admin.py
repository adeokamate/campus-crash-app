from django.contrib import admin

# Register your models here.
from .models import User
from .models import Chat
from .models import Report

admin.site.register(User)
admin.site.register(Chat)
admin.site.register(Report)
