from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.
class UserDetailInline(admin.StackedInline):
    model = UserDetail
    can_delete = False
    verbose_name_plural = 'User_Detail'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserDetailInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)