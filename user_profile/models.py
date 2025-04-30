from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField("Активный", default=True)

    def __str__(self):
        return self.user.username

    @property
    def all_projects(self):
        return [p for p in self.owned_projects.all()] + [p for p in self.member_projects.all()]
    
    @property
    def name(self):
        return self.user.username

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"


class Project(models.Model):
    name = models.CharField("Название", max_length=64)
    owner = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='owned_projects', verbose_name="Создатель")
    members = models.ManyToManyField(Profile, blank=True, related_name='member_projects', verbose_name="Участники")
    is_active = models.BooleanField("Активный", default=True)

    @property
    def members_to_string(self):
        result = ""
        for member in self.members.all():
            result += member.name
        return result
        # return ", ".join(str(self.members.all()))

    class Meta:
        unique_together = (("name", "owner"),)

