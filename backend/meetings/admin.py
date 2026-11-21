from .models import StudySession, Attendance, PeerRating
from django.contrib import admin

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0

# Register your models here.
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'start_time', 'status')
    list_filter = ('status',)
    search_fields = ('title',)
    list_select_related = ('group',)
    inlines = [AttendanceInline]

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('session', 'user', 'status')
    list_filter = ('status',)
    list_select_related = ('session', 'user')

class PeerRatingAdmin(admin.ModelAdmin):
    list_display = ('rater', 'rated_user', 'score', 'session', 'created_at')
    list_filter = ('score',)
    list_select_related = ('rater', 'rated_user', 'session')
    readonly_fields = ('created_at',)

admin.site.register(StudySession, StudySessionAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(PeerRating, PeerRatingAdmin)