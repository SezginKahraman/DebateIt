# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Room(models.Model):
    """Münazara odası modeli"""

    name = models.CharField(max_length=200)
    topic = models.TextField()
    image = models.ImageField(upload_to="app/img/room_images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Yeni alanlar - varsayılan değerlerle
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_rooms",
        null=True,  # Mevcut kayıtlar için null izin ver
    )
    description = models.TextField(
        default="", blank=True  # Boş string varsayılan değer
    )
    max_participants_per_team = models.IntegerField(default=5)  # Varsayılan değer
    speaker_time_limit = models.IntegerField(default=180)  # Varsayılan değer (3 dakika)
    is_private = models.BooleanField(default=False)  # Varsayılan değer
    room_password = models.CharField(
        max_length=50, blank=True, default=""  # Boş string varsayılan değer
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("waiting", "Başlamayı Bekliyor"),
            ("in_progress", "Devam Ediyor"),
            ("break", "Mola"),
            ("finished", "Tamamlandı"),
        ],
        default="waiting",  # Varsayılan değer
    )

    def __str__(self):
        return self.name

    def get_initials(self):
        return "".join(word[0].upper() for word in self.name.split())


class Team(models.Model):
    """Takım modeli - Savunan veya Karşı Çıkan"""

    TEAM_TYPES = [
        ("PRO", "Savunan"),
        ("CON", "Karşı Çıkan"),
    ]
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    team_type = models.CharField(max_length=3, choices=TEAM_TYPES)
    total_speaking_time = models.IntegerField(
        default=0
    )  # Takımın toplam konuşma süresi

    def __str__(self):
        return f"{self.get_team_type_display()} - {self.room.name}"

    def get_available_speaking_time(self):
        """Takımın kalan konuşma süresini döndürür"""
        return (
            self.room.speaker_time_limit * self.room.max_participants_per_team
        ) - self.total_speaking_time


# Diğer modeller aynı kalacak
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


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
