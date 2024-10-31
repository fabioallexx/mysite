from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.index, name='index'),
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('contrato_info/<int:file_id>/', views.contrato_info, name='contrato_info'),
    path('caderno_encargos/<int:contract_id>/', views.caderno_encargos, name='caderno_encargos'),
    path('contrato/detalhes/<int:contract_id>/', views.contrato_detalhes, name='contrato_detalhes'),
    path('fechar_contrato/<int:contract_id>/', views.fechar_contrato, name='fechar_contrato'),
    path('historico/', views.historico_list, name='historico'),
    path('contrato/detalhes/inativo/<int:contract_id>/', views.detalhes_contrato_inativo, name='detalhes_contrato_inativo'),
    path('execucao_contrato/<int:contract_id>/', views.execucao_contrato, name='execucao_contrato'),
    path('inserir_fatura/<int:contract_id>/', views.inserir_fatura, name='inserir_fatura'),
    path('faturas/lista/<int:contract_id>/', views.lista_faturas, name='lista_faturas'),
    path('fatura/<int:fatura_id>/', views.detalhes_fatura, name='detalhes_fatura'),
    path('contrato/<int:contract_id>/pdf/', views.visualizar_pdf, name='visualizar_pdf'),
    path('gerar_pdf_caderno/<int:caderno_id>/', views.gerar_pdf_caderno, name='gerar_pdf_caderno'),
]