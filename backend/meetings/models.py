from django.db import models
from django.db import Q, F
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from groups.models import StudyGroup
from datetime import timedelta

# Create your models here.
class StudySession(models.Model):
    class MeetingStatus(models.TextChoices):
        scheduled = 'scheduled'
        cancelled = 'cancelled'

    meetings_group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name="sessions")
    meetings_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_sessions")
    meetings_title = models.CharField(max_length=150)
    meetings_location_or_link = models.CharField(max_length=255)
    meetings_start_time = models.DateTimeField()
    meetings_duration = models.PositiveIntegerField()#Yet to be finished
    meetings_status = models.CharField(choices=MeetingStatus, default=MeetingStatus.scheduled, max_length=20)

    class Meta:
        ordering = ['meetings_start_time']

        constraints = [
            models.CheckConstraint(
                condition=Q(meetings_duration__gt=0),
                name='duration_constraint'
            ),
        ]

    @property
    def meetings_end_time(self):
        return self.meetings_start_time + timedelta(minutes=self.meetings_duration)

    def __str__(self):
        return f"{self.meetings_title} - {self.meetings_group}"


class Attendance(models.Model):
    class AttendanceChoices(models.TextChoices):
        going = 'going'
        attended = 'attended'
        no_show = 'no_show'

    meetings_session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name='attendances')
    meetings_user = models.ForeignKey(settings.AUTH_MODEL_USER, on_delete=models.CASCADE, related_name='attendances')
    meetings_status = models.CharField(choices=AttendanceChoices, default=AttendanceChoices.going, max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'user'],
                name="meetings_unique_user_per_session"
            ),
        ]

    def __str__(self):
        return f"{self.meetings_user}, {self.meetings_session}, {self.meetings_status}"


class PeerRating(models.Model):
    meetings_rater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ratings_given')
    meetings_rated_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_received')
    meetings_session = models.ForeignKey(StudySession, on_delete=models.PROTECT, related_name='ratings')
    meetings_score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    meetings_comment = models.TextField(blank=True)
    meetings_created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['meetings_rater', 'meetings_rated_user', 'meetings_session'],
                name='meetings_unique_rater_and_rated_user_per_session'  
            ),

            models.CheckConstraint(
                condition=Q(meetings_score__gte=1) & Q(meetings_score__lte=5),
                name='score_check'
            ),

            models.CheckConstraint(
                condition=~Q(meetings_rater=F('meetings_rated_user')),
                name='rater_and_rated_user_constraint'
            )
        ]

    def __str__(self):
        return f"{self.meetings_rater}, {self.meetings_rated_user}, {self.meetings_score}"
