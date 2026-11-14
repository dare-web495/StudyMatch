from django.db import models
from django.db.models import Q
from django.conf import settings
from courses.models import Course

# Create your models here.
class StudyGroup(models.Model):
    class Visibility(models.TextChoices):
        public = 'public'
        invite_only = 'invite_only'

    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="study_groups")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_groups")
    name = models.CharField(max_length=100)
    goal = models.CharField(max_length=255, blank=True)
    max_members = models.PositiveSmallIntegerField(default=6)
    visibility = models.CharField(choices=Visibility, default=Visibility.public)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ['created_at']

        constraints = [
            models.CheckConstraint(
                check = Q(max_member__gte=1),
                name = 'groups_max_members_at_least_one'
            ),
        ]

    def __str__(self):
        return f"{self.name}: {self.course}"


class Membership(models.Model):
    class Role(models.TextChoices):
        owner = 'owner'
        member = 'member'

    class Status(models.TextChoices):
        pending = 'pending'
        active = 'active'
        left = 'left'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    group = models.ForeignKey(StudyGroup, on_delete=models.SET_NULL, null=True, related_name="created_groups")
    role = models.CharField(choices=Role, default=Role.member)
    status = models.CharField(choices=Status, default=Status.pending)
    joined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'group'],
                name='unique_user_per_group'
            ),

            models.UniqueConstraint(
                fields=['group'],
                condition=Q(role='owner', status='active'),
                name='groups_one_active_owner_per_group'
            )
        ]

    def __str__(self):
        return f"{self.user}, {self.group}, {self.status}"
