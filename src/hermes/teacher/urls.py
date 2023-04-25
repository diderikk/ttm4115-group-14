from django.urls import path
from . import views

urlpatterns = [
    path('api/duty/', views.duty, name='duty'),
    path('teacher/', views.render_state_teacher),
    path('api/login/', views.login, name='login'),
    path('api/tcancel/', views.cancel, name='tcancel'),
]
