# # """
# # ASGI config for ascencia_interviews project.

# # It exposes the ASGI callable as a module-level variable named ``application``.

# # For more information on this file, see
# # https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
# # """

# # import os

# # from django.core.asgi import get_asgi_application
# # from channels.routing import ProtocolTypeRouter, URLRouter
# # from channels.auth import AuthMiddlewareStack
# # from ascencia_interviews.consumers import TranscriptionConsumer  # adjust if needed
# # import django
# # from django.urls import re_path
# from .routing import websocket_urlpatterns

# # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ascencia_interviews.settings')

# # # application = get_asgi_application()

# # django.setup()

# # # application = ProtocolTypeRouter({
# # #     "http": get_asgi_application(),
# # #     "websocket": AuthMiddlewareStack(
# # #         URLRouter(websocket_urlpatterns)
# # #         #     [
# # #         #     # re_path(r"ws/audio/$", AudioStreamConsumer.as_asgi()),
# # #         #     re_path(r"(ws/)?audio/$", AudioStreamConsumer.as_asgi()),
# # #         # ]
# # #     ),
# # # })



# # # from channels.routing import ProtocolTypeRouter, URLRouter
# # # from .routing import websocket_urlpatterns

# # # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')


# # application = ProtocolTypeRouter({
# #     "http": get_asgi_application(),
# #     "websocket": AuthMiddlewareStack(
# #         URLRouter(
# #             ascencia_interviews.routing.websocket_urlpatterns
# #         )
# #     ),
# # })


# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ascencia_interviews.settings")

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             websocket_urlpatterns
#         )
#     ),
# })




import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from ascencia_interviews.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ascencia_interviews.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
