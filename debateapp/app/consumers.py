# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime
from .models import Room, Message, Participant, Team
import logging

logger = logging.getLogger(__name__)


class DebateRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"debate_room_{self.room_id}"
        self.user = self.scope["user"]

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Kullanıcı bağlandığında mevcut katılımcıları al ve gönder
        participant_info = await self.get_participant_info()
        await self.send(
            text_data=json.dumps(
                {"type": "participant_list", "participants": participant_info}
            )
        )

        # Diğer kullanıcılara yeni kullanıcı bağlandı bilgisi gönder
        if self.user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_join",
                    "username": self.user.username,
                },
            )

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            # Kullanıcıyı takımdan çıkar
            await self.leave_team()

            # Diğer kullanıcılara bildir
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_leave",
                    "username": self.user.username,
                },
            )

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type", "chat_message")

        if message_type == "chat_message":
            message = data["message"]
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": self.user.username,
                    "timestamp": datetime.now().strftime("%H:%M"),
                },
            )
        elif message_type == "join_team":
            logger.info(f"Join team: {data}")
            team_type = data["team"]
            success = await self.join_team(team_type)
            if success:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "team_update",
                        "username": self.user.username,
                        "team": team_type,
                        "action": "join",
                    },
                )
        elif message_type == "leave_team":
            await self.leave_team()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "team_update",
                    "username": self.user.username,
                    "action": "leave",
                },
            )
        elif message_type == "get_participants":
            participant_info = await self.get_participant_info()
            await self.send(
                text_data=json.dumps(
                    {"type": "participant_list", "participants": participant_info}
                )
            )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat_message",
                    "message": event["message"],
                    "username": event["username"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def user_join(self, event):
        await self.send(
            text_data=json.dumps({"type": "user_join", "username": event["username"]})
        )

    async def user_leave(self, event):
        await self.send(
            text_data=json.dumps({"type": "user_leave", "username": event["username"]})
        )

    async def team_update(self, event):
        if event.get("action") == "join":
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "team_update",
                        "username": event["username"],
                        "team": event["team"],
                    }
                )
            )
        elif event.get("action") == "leave":
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "team_update",
                        "username": event["username"],
                        "team": None,
                    }
                )
            )

    @database_sync_to_async
    def get_participant_info(self):
        room = Room.objects.get(id=self.room_id)
        pro_team = Team.objects.get(room=room, team_type="PRO")
        con_team = Team.objects.get(room=room, team_type="CON")

        participants = {"PRO": [], "CON": []}
        for participant in Participant.objects.filter(team__room=room):
            team_type = participant.team.team_type
            participants[team_type].append(
                {
                    "username": participant.user.username,
                    "hand_raised": participant.hand_raised,
                }
            )
        return participants

    @database_sync_to_async
    def join_team(self, team_type):
        try:
            room = Room.objects.get(id=self.room_id)
            team = Team.objects.get(room=room, team_type=team_type)
            Participant.objects.create(user=self.user, team=team)
            return True
        except Exception:
            return False

    @database_sync_to_async
    def leave_team(self):
        try:
            participant = Participant.objects.filter(
                user=self.user, team__room_id=self.room_id
            ).first()
            if participant:
                participant.delete()
                return True
        except Exception:
            return False
