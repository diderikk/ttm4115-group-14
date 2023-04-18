from django.urls import path

from . import views
import os, sys
sys.path.append(os.path.dirname(__file__))

import statemachine as stm


urlpatterns = [
    path('idle/', views.idle_view, name='idle'),
    path('active/', views.active_view, name='active'),
    path('start/', views.send, name='start'),
    path('stop/', views.send, name='stop'),
]
