from django.db import models
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
