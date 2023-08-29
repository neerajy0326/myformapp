
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from . import consumers
from channels.auth import AuthMiddlewareStack
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<user_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]


application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})