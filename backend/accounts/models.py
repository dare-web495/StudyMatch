from django.db import models
from django.db.models import F, Q
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

# Create your models here.
class User(AbstractUser):
    university = models.CharField(max_length=200, blank=False)
    year_of_study = models.PositiveSmallIntegerField(validators=[MaxValueValidator(7), MinValueValidator(1)])
    bio = models.TextField(null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to='avatars/')
    reliability_score = models.FloatField(default=3.0)

    REQUIRED_FIELDS = ['university', 'year_of_study']

    def __str__(self):
        return self.username

class Availability(models.Model):
    class WeekChoices(models.IntegerChoices):
        Monday = 0, "Monday"
        Tuesday = 1, "Tuesday"
        Wednesday = 2, "Wednesday"
        Thursday = 3, "Thursday"
        Friday = 4, "Friday"
        Saturday = 5, "Saturday"
        Sunday = 6, "Sunday"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="availability_slots")
    day_of_week = models.SmallIntegerField(choices=WeekChoices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['user__username', 'day_of_week', 'start_time']

        constraints = [
            models.CheckConstraint(
                condition=Q(end_time__gt=F('start_time')),
                name="accounts_availability_end_after_start"
            ),
        ]

    def clean(self):
        super().clean()
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")

        if self.user_id and self.day_of_week is not None and self.start_time and self.end_time:
            overlapping_slots = Availability.objects.filter(
                user_id=self.user_id,
                day_of_week=self.day_of_week,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            )

            if self.pk:
                overlapping_slots = overlapping_slots.exclude(pk=self.pk)

            if overlapping_slots.exists():
                raise ValidationError(
                    "This time slot overlaps with an existing slot for this user on the same day."
                )

    def __str__(self):
        return f"{self.user}, {self.get_day_of_week_display()}, {self.start_time} to {self.end_time}"
