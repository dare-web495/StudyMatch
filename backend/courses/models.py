from django.db import models
from django.conf import settings

# Create your models here.
class Course(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    university = models.CharField(max_length=200)

    class Meta:
        ordering = ['university', 'code']

        constraints = [
            models.UniqueConstraint(
                fields=['code', 'university'],
                name='courses_unique_code_per_university'
            ),
        ]

    def __str__(self):
        return f"{self.code} ({self.university})"


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="enrollments")
    semester = models.CharField(max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'course', 'semester'],
                name='courses_unique_enrollment_per_semester'
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.course} - {self.semester}"