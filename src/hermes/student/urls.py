from django.urls import path
from . import views

urlpatterns = [
    path('student/', views.render_state_student),
    path('student/<uuid:id>/', views.render_task_state_student),
    path('slogin/', views.login, name="student login"),
    path('api/select/', views.select_task),
    path('api/back/', views.back),
    path('api/ask/', views.ask),
    path('api/cancel/', views.cancel),
]
