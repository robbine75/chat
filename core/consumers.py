import langid

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.conf import settings

from .models import Profile, UnreadThread, Message
from .tasks import chatbot_response

langid.set_languages([code for code, _ in settings.LANGUAGES])


class WsUsers(JsonWebsocketConsumer):
    """ WebsocketConsumer related to 'users' group. """
    def connect(self):
        """ Adds to 'users' group and send a list of active users. """
        async_to_sync(self.channel_layer.group_add)(
            'users',
            self.channel_name
        )
        super().connect()
        self.send_json(Profile.get_online_users())

    def disconnect(self, code):
        """ Remove from 'users' group and close the webSocket. """
        async_to_sync(self.channel_layer.group_discard)(
            'users',
            self.channel_name
        )
        self.close()

    def users_update(self, message):
        """ User binding. """
        self.send_json(message['content'])


class WsThread(JsonWebsocketConsumer):
    """ WebsocketConsumer related to specific 'thread' group. """
    thread_id = None

    def connect(self):
        """ Adds to specific 'thread' group. """
        self.thread_id = int(self.scope['url_route']['kwargs'].get('thread'))

        async_to_sync(self.channel_layer.group_add)(
            'thread-{}'.format(str(self.thread_id)),
            self.channel_name
        )
        super().connect()

    def disconnect(self, code):
        """ Remove from specific 'thread' group and close the webSocket. """
        async_to_sync(self.channel_layer.group_discard)(
            'thread-{}'.format(str(self.thread_id)),
            self.channel_name
        )
        self.close()

    def receive_json(self, content, **kwargs):
        if 'text' in content:
            message = Message(
                thread_id=self.thread_id,
                user=self.scope.get('user'),
                text=content.get('text')
            )
            if message and message.thread.users.filter(pk=message.user.pk):
                message.lang, _ = langid.classify(message.text)
                message.save()

                # Create unread thread for each user in thread,
                # we will delete it latter.
                for user in message.thread.users.all():
                    if user.username == 'chatbot':
                        # This is a message for chat bot.
                        chatbot_response.delay(self.thread_id,
                                               content.get('text'))
                    else:
                        UnreadThread.objects.get_or_create(
                            thread_id=self.thread_id,
                            user=user
                        )
        elif 'read' in content:
            # The message was delivered - delete user's unread thread.
            UnreadThread.objects.filter(
                thread_id=self.thread_id,
                user=self.scope.get('user')
            ).delete()

    def message_update(self, message):
        """ Message binding. """
        self.send_json(message['content'])
