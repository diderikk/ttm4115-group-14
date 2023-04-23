from django.urls import path
from . import views
from .websocket import WebSocketConsumer



urlpatterns = [
    path("api/accounts/", views.create_user),
    path('api/login/', views.login, name='login'),
    path('api/tasks/', views.tasks, name='tasks'),
    path('api/tasks/<uuid:id>/', views.task_detail),
    path('api/deliveries/', views.deliver, name='deliver'),
    path('api/deliveries/<uuid:id>/', views.deliver_detail, name='deliver_detail'),
    path('api/notifications/', views.notifications, name='notifications'),
    path('api/notifications/<uuid:id>/', views.notifications_detail, name='notifications_detail'),
    path('api/duty/', views.duty, name='duty'),
    # path('api/test/', views.test_http_to_websocket),
    # path('test/', views.test_template),
    # path('login/', views.test_login),
    # path('tasks/', views.test_task_form),
    # path('teachers/', views.progression_view),
    path('state/', views.render_state)
]

websocket_urlpatterns = [
    path('ws/<str:room_name>/', WebSocketConsumer.as_asgi()),
]
