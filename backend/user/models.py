from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import os

# Create your models here.


class Team(AbstractUser):
    register_completed = models.BooleanField(default=False)
    verification_completed = models.BooleanField(default=False)

    def payment_image_upload_to(instance, filename):
        ext = filename.split('.')[-1]
        filename = f"{instance.id}_{uuid.uuid4()}.{ext}"
        return os.path.join('payment_images/', filename)
    payment_number = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self):
        res = ""
        for team_member in TeamMember.objects.filter(team=self):
            res += str(team_member)+" "
        return ("✔ " if self.verification_completed else "❌ ")+("✔ " if self.register_completed else "❌ ")+self.username+":"+res


class TeamMember(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='members')
    leader = models.BooleanField(default=False)
    student_number = models.CharField(max_length=15, null=True, blank=True)
    university = models.CharField(max_length=128, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    major = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class StaffTeam(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StaffMember(models.Model):
    staff_team = models.ForeignKey(
        StaffTeam, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='staff_member_images/', null=True, blank=True)
    description = models.CharField(max_length=512, null=True, blank=True)
    role = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
