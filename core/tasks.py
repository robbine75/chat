import datetime
import langid

from celery import Celery, shared_task
from chatterbot import ChatBot
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache

from .models import Profile, Message

app = Celery('chat')

channel_layer = get_channel_layer()
User = get_user_model()

chatbot = ChatBot(**settings.CHATTERBOT)
langid.set_languages([code for code, _ in settings.LANGUAGES])


@app.task
def update_user_statuses():
    """ Task to update user online statuses via websockets. """
    # Chat bot is always online.
    now = datetime.datetime.now()
    cache.set('seen_chatbot', now, settings.USER_ONLINE_TIMEOUT)

    async_to_sync(channel_layer.group_send)(
        'users',
        {
            'type': 'users.update',
            'content': Profile.get_online_users()
        }
    )


@shared_task
def chatbot_response(thread_id, text):
    """ Task to send a response from Chatbot. """
    chatbot_user = User.objects.get(username='chatbot')

    response = str(chatbot.get_response(text))

    message = Message(
        thread_id=thread_id,
        user=chatbot_user,
        text=response
    )
    message.lang, _ = langid.classify(message.text)
    message.save()
