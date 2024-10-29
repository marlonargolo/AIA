from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("", views.webhook, name='webhook'),    #www.arquiteturadeia.com 
    #path('home/', views.home, name='home'),     #www.arquiteturadeia.com.br/home 
    path('cadastro/', views.cadastro, name='cadastro'),
    path('perfil/', views.perfil, name='perfil'),
    path('messages/', views.get_messages, name='get_messages'),
    path('chat', views.chat, name='chat'),
    #pagamentos
    path('pagamento/', views.create_preference, name='create_preference'),
    # Rotas de callback do pagamento
    path('pagamento/sucesso/', views.payment_success, name='payment_success'),
    path('pagamento/erro/', views.payment_failure, name='payment_failure'),
    path('pagamento/pendente/', views.payment_pending, name='payment_pending'),
    path('notificacoes/', views.notification_handler, name='notification_handler'),
]
