from .models import Membership
from django.contrib import admin

class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0

# Register your models here.
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'visibility', 'is_archived', 'created_at')
    list_filter = ('visibility', 'is_archived')
    search_fields = ('name',)
    list_select_related = ('course', 'created_by')
    inlines = [MembershipInline]

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'status', 'joined_at')
    list_filter = ('role', 'status')
    list_select_related = ('user', 'group')
    