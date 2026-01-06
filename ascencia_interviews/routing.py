# from django.urls import re_path
# from . import consumers
# from ascencia_interviews.routing import websocket_urlpatterns as base_websocket_urlpatterns

# websocket_urlpatterns = base_websocket_urlpatterns + [
#     re_path(r"ws/deepgram/$", consumers.DeepgramProxyConsumer.as_asgi()),
# ]
# app/routing.py
# ascencia_interviews/routing.py
# from django.urls import re_path
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
from ascencia_interviews.consumers import TranscriptionConsumer  # adjust if needed

# application = ProtocolTypeRouter({
#     "websocket": AuthMiddlewareStack(
#         URLRouter([
#             # re_path(r"ws/audio/$", AudioStreamConsumer.as_asgi()),
#             re_path(r"(ws/)?audio/$", AudioStreamConsumer.as_asgi()),
#         ])
#     )
# })
# websocket_urlpatterns = [
#     re_path(r"(ws/)?audio/$", AudioStreamConsumer.as_asgi()),
# ]


from django.urls import re_path
from .consumers import TranscriptionConsumer

websocket_urlpatterns = [
    # re_path(r"ws/transcription/$", TranscriptionConsumer.as_asgi()),
    re_path(r"^transcription/?$", TranscriptionConsumer.as_asgi()),
]