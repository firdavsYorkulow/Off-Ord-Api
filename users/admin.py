from django.contrib import admin
from .models import  User
# Register your models here.

# admin.site.register(User)

@admin.register(User)
class AdminUser(admin.ModelAdmin):
    list_display = ['id','username','auth_status','work_type']