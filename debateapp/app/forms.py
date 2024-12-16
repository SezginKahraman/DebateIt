# forms.py
from django import forms
from .models import Room


class RoomCreateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["name", "topic", "image"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-500 focus:outline-none",
                    "placeholder": "Oda Adı",
                }
            ),
            "topic": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-500 focus:outline-none",
                    "placeholder": "Münazara Konusu",
                }
            ),
            "image": forms.FileInput(
                attrs={
                    "class": "w-full px-4 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-500 focus:outline-none",
                }
            ),
        }
