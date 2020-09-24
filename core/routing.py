from django.conf.urls import url

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from .consumers import WsUsers, WsThread


chat = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            url(r"^ws/users/$", WsUsers),
            url(r"^ws/thread/(?P<thread>\w+)$", WsThread),
        ])
    ),
})
