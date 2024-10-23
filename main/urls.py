from django.urls import path

from . import views

urlpatterns = [
    path('<int:id>', views.index, name='index'),
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('contrato_info/<int:file_id>/', views.contrato_info, name='contrato_info'),
    path('caderno_encargos/<int:contract_id>/', views.caderno_encargos, name='caderno_encargos'),
    path('contrato/detalhes/<int:contract_id>/', views.contrato_detalhes, name='contrato_detalhes'),
    path('fechar_contrato/<int:contract_id>/', views.fechar_contrato, name='fechar_contrato'),
    path('historico/', views.historico_list, name='historico'),
    path('contrato/detalhes/inativo/<int:contract_id>/', views.detalhes_contrato_inativo, name='detalhes_contrato_inativo'),
    path('fatura/<int:contract_id>', views.fatura, name='fatura'),
]