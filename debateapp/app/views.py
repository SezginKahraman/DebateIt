# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Room, Team, Participant, Judge, Break
import random


# @login_required
def room_list(request):
    """Münazara odalarının listelendiği view"""
    rooms = Room.objects.filter(is_active=True)
    context = {
        "welcome_cards": [
            {
                "title": "Arkadaşlarını Davet Et",
                "description": "Tartışmalarını zenginleştirmek için arkadaşlarını davet et",
                "icon": "user-plus",
                "button_text": "Davet Gönder",
                "button_url": "#",
            },
            {
                "title": "İlk Münazarana Katıl",
                "description": "Hemen bir tartışma odasına katıl ve fikirlerini paylaş",
                "icon": "message-square",
                "button_text": "Münazaraya Katıl",
                "button_url": "#",
            },
            {
                "title": "Hoş Geldiniz",
                "description": "Münazara platformumuza hoş geldiniz! Başlamak için bir seçenek seçin.",
                "icon": "users",
                "button_text": "Keşfet",
                "button_url": "#",
            },
        ]
    }
    return render(request, "app/room_list.html", {"rooms": rooms, "context": context})


# @login_required
def room_detail(request, room_id):
    """Münazara odası detay view'i"""
    room = get_object_or_404(Room, id=room_id)
    pro_team = Team.objects.get(room=room, team_type="PRO")
    con_team = Team.objects.get(room=room, team_type="CON")
    judge = Judge.objects.get(room=room)

    context = {
        "room": room,
        "pro_team": pro_team,
        "con_team": con_team,
        "judge": judge,
        "pro_participants": Participant.objects.filter(team=pro_team),
        "con_participants": Participant.objects.filter(team=con_team),
    }
    return render(request, "app/room_detail.html", context)


# @login_required
def join_room(request, room_id):
    """Odaya katılma view'i"""
    room = get_object_or_404(Room, id=room_id)
    pro_team = Team.objects.get(room=room, team_type="PRO")
    con_team = Team.objects.get(room=room, team_type="CON")

    # Rastgele takım seçimi
    selected_team = random.choice([pro_team, con_team])

    # Katılımcı oluştur
    Participant.objects.create(user=request.user, team=selected_team)

    return redirect("room_detail", room_id=room_id)


# @login_required
def raise_hand(request, room_id):
    """El kaldırma view'i"""
    participant = get_object_or_404(
        Participant, user=request.user, team__room_id=room_id
    )
    participant.hand_raised = True
    participant.save()
    return JsonResponse({"status": "success"})


# @login_required
def take_break(request, room_id):
    """Mola alma view'i"""
    participant = get_object_or_404(
        Participant, user=request.user, team__room_id=room_id
    )

    # Mola sayısı kontrolü
    active_breaks = Break.objects.filter(
        team=participant.team, ended_at__isnull=True
    ).count()

    if active_breaks >= 3:
        return JsonResponse(
            {"status": "error", "message": "Maximum mola sayısına ulaşıldı"}
        )

    Break.objects.create(room_id=room_id, team=participant.team)
    return JsonResponse({"status": "success"})
