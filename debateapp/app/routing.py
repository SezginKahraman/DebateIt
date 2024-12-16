# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/debate/(?P<room_id>\w+)/$", consumers.DebateRoomConsumer.as_asgi()),
]
