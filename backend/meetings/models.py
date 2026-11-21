from django.db import models
from django.db.models import Q, F
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import timedelta

# Create your models here.
class StudySession(models.Model):
    class MeetingStatus(models.TextChoices):
        scheduled = 'scheduled'
        cancelled = 'cancelled'

    group = models.ForeignKey('groups.StudyGroup', on_delete=models.CASCADE, related_name="sessions")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_sessions")
    title = models.CharField(max_length=150)
    location_or_link = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    duration = models.PositiveIntegerField()# In minutes
    status = models.CharField(choices=MeetingStatus, default=MeetingStatus.scheduled, max_length=20)

    class Meta:
        ordering = ['start_time']

        constraints = [
            models.CheckConstraint(
                condition=Q(duration__gt=0),
                name='meetings_session_duration_positive'
            ),
        ]

    @property
    def end_time(self):
        return self.start_time + timedelta(minutes=self.duration)

    def __str__(self):
        return f"{self.title} - {self.group}"


class Attendance(models.Model):
    class AttendanceChoices(models.TextChoices):
        going = 'going'
        attended = 'attended'
        no_show = 'no_show'

    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(choices=AttendanceChoices, default=AttendanceChoices.going, max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'user'],
                name="meetings_unique_user_per_session"
            ), 
        ]

    def __str__(self):
        return f"{self.user}, {self.session}, {self.status}"


class PeerRating(models.Model):
    rater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ratings_given')
    rated_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_received')
    session = models.ForeignKey(StudySession, on_delete=models.PROTECT, related_name='ratings')
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['rater', 'rated_user', 'session'],
                name='meetings_unique_rater_and_rated_user_per_session'  
            ),

            models.CheckConstraint(
                condition=Q(score__gte=1) & Q(score__lte=5),
                name='meetings_rating_score_1_to_5'
            ),

            models.CheckConstraint(
                condition=~Q(rater=F('rated_user')),
                name='meetings_rating_no_self_rating'
            )
        ]

    def __str__(self):
        return f"{self.rater}, {self.rated_user}, {self.score}"
