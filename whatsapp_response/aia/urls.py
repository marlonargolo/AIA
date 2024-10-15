from django.urls import path
from . import views

urlpatterns = [
path("", views.webhook, name='webhook'),
path('home/', views.home, name='home'),
path('cadastro/', views.cadastro, name='cadastro'),
path('login/', views.login, name='login'),
path('perfil/', views.perfil, name='perfil'),
path('messages/', views.get_messages, name='get_messages'),
path('acompanhamento/', views.acompanhamento, name='acompanhamento'),
path('atendimento', views.atendimento, name='atendimento')
]
