from django.db import models
from django.db.models import F, Q
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

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

"""
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
        ordering = ['day_of_week', 'start_time']

        constraints = [
            models.UniqueConstraint(
                condition=Q(end_time__gt=F('start_time'))
            )
        ]

    def clean(self):
        super().clean()

        """


