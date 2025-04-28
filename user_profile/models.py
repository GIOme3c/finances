from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField("Активный", default=True)

    def __str__(self):
        return self.user.username

    @property
    def all_projects(self):
        return [{"project": p, "status": "owner"} for p in self.owned_projects.all()] + [{"project": p, "status": "member"} for p in self.member_projects.all()]

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"


class Project(models.Model):
    name = models.CharField("Название", max_length=64)
    owner = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='owned_projects', verbose_name="Создатель")
    members = models.ManyToManyField(Profile, blank=True, related_name='member_projects', verbose_name="Участники")
    is_active = models.BooleanField("Активный", default=True)

    class Meta:
        unique_together = (("name", "owner"),)

