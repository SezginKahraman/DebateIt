# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Room(models.Model):
    """Münazara odası modeli"""

    name = models.CharField(max_length=200)
    topic = models.TextField()
    image = models.ImageField(upload_to="room_images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_initials(self):
        """Oda adının baş harflerini döndürür"""
        return "".join(word[0].upper() for word in self.name.split())


class Team(models.Model):
    """Takım modeli - Savunan veya Karşı Çıkan"""

    TEAM_TYPES = [
        ("PRO", "Savunan"),
        ("CON", "Karşı Çıkan"),
    ]
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    team_type = models.CharField(max_length=3, choices=TEAM_TYPES)

    def __str__(self):
        return f"{self.get_team_type_display()} - {self.room.name}"


class Participant(models.Model):
    """Katılımcı modeli"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    is_speaking = models.BooleanField(default=False)
    hand_raised = models.BooleanField(default=False)
    speaking_time = models.IntegerField(default=0)  # Saniye cinsinden

    def __str__(self):
        return f"{self.user.username} - {self.team}"


class Judge(models.Model):
    """Hakem modeli"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    room = models.OneToOneField(Room, on_delete=models.CASCADE)
    is_ai = models.BooleanField(default=False)

    def __str__(self):
        if self.is_ai:
            return f"AI Hakem - {self.room.name}"
        return f"{self.user.username} - {self.room.name}"


class Break(models.Model):
    """Mola modeli"""

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def is_active(self):
        return self.ended_at is None

    def duration(self):
        if self.ended_at:
            return (self.ended_at - self.started_at).seconds
        return (timezone.now() - self.started_at).seconds
