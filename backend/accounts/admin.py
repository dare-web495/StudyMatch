from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('StudyMatch profile', {
            'fields': ('university', 'year_of_study', 'bio', 'avatar', 'reliability_score')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('StudyMatch profile', {
            'fields': ('university', 'year_of_study', 'bio', 'avatar')
        }),
    )

    readonly_fields = ('reliability_score',)

    list_display = ('username', 'email', 'university', 'year_of_study', 'reliability_score')


admin.site.register(User, CustomUserAdmin)