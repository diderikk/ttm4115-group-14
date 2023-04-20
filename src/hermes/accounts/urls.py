from django.urls import path
from . import views



urlpatterns = [
    path("api/accounts/", views.create_user),
    path('api/login/', views.login, name='login'),
    path('api/logout/', views.logout),
    path('api/tasks/', views.tasks),
    path('api/tasks/<uuid:id>/', views.task_detail),
    path('api/deliveries/', views.deliver, name='deliver'),
    path('api/deliveries/<uuid:id>/', views.deliver_detail, name='deliver_detail'),
    path('test/', views.test_template),
    path('login/', views.test_login),
]
