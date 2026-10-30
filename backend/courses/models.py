from django.db import models

# Create your models here.
class Course(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    university = models.CharField(max_length=200)

    class Meta:
        # Yet to add ordering
        constraints = [
            models.UniqueConstraint(
                fields=['code', 'university'],
                name='Unique_code_per_university'
            ),
        ]