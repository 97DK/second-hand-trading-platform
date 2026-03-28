from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PasswordResetRequest

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'student_id', 'nickname', 'is_verified', 'user_type')
    list_filter = ('is_verified', 'user_type')
    fieldsets = UserAdmin.fieldsets + (
        ('校园信息', {'fields': ('student_id', 'student_card_photo', 'is_verified', 'nickname', 'avatar')}),
    )

@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'student_name', 'status', 'created_at')
    list_filter = ('status',)
    readonly_fields = ('created_at',)