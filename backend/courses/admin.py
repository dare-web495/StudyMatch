from django.contrib import admin
from .models import Enrollment, Course

# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'university')
    search_fields = ('code', 'name')
    list_filter = ('university',)


class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'semester')
    list_filter = ('semester',)
    list_select_related = ('user', 'course')

admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)