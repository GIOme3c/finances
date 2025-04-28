from django.db import models
from user_profile.models import Project


class ProjectRelatedMixin(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)

    class Meta:
        abstract = True


class DeactivatedMixin(models.Model):
    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        abstract = True
