from django.urls import path
from . import views
from .websocket import WebSocketConsumer



urlpatterns = [
    path("api/accounts/", views.create_user),
    path('api/tasks/', views.tasks, name='tasks'),
    path('api/deliveries/', views.deliver, name='deliver'),
    path('api/notifications/', views.notifications, name='notifications'),
    path('api/notifications/<int:group_number>/', views.notifications_detail, name='notifications_detail'),

]

websocket_urlpatterns = [
    path('ws/<str:room_name>/', WebSocketConsumer.as_asgi()),
]
