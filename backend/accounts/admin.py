from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Availability

class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 0

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

    inlines = [AvailabilityInline]

class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('user', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week',)
    list_select_related = ('user',)

admin.site.register(Availability, AvailabilityAdmin)
admin.site.register(User, CustomUserAdmin)
