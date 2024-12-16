from django.urls import path
from . import views

urlpatterns = [
    path("", views.room_list, name="room_list"),
    path("room/<int:room_id>/", views.room_detail, name="room_detail"),
    path("room/<int:room_id>/join/", views.join_room, name="join_room"),
    path("room/<int:room_id>/raise-hand/", views.raise_hand, name="raise_hand"),
    path("room/<int:room_id>/break/", views.take_break, name="take_break"),
    path("create-room/", views.create_room, name="create_room"),
]
