from django.urls import path
from . import views
from .websocket import WebSocketConsumer



urlpatterns = [
    path("api/accounts/", views.create_user),
    path('api/login/', views.login, name='login'),
    path('api/logout/', views.logout),
    path('api/tasks/', views.tasks, name='tasks'),
    path('api/tasks/<uuid:id>/', views.task_detail),
    path('api/deliveries/', views.deliver, name='deliver'),
    path('api/deliveries/<uuid:id>/', views.deliver_detail, name='deliver_detail'),
    path('api/test/', views.test_http_to_websocket),
    path('test/', views.test_template),
    path('login/', views.test_login),
    path('tasks/', views.test_task_form),
    path('teachers/', views.test_teacher_home),
]

websocket_urlpatterns = [
    path('ws/<str:room_name>/', WebSocketConsumer.as_asgi()),
]
