from django.urls import path

from . import views

urlpatterns = [
    path('<int:id>', views.index, name='index'),
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('create/', views.create, name='create'),
    path('view/', views.view, name='view'),
    path('upload/', views.upload_file, name='upload_file'),
    path('contrato_info/<int:file_id>/', views.contrato_info, name='contrato_info'),
    path('caderno-encargos/', views.caderno_encargos, name='caderno_encargos'),
    path('contrato/detalhes/<int:contract_id>/', views.contrato_detalhes, name='contrato_detalhes'),
]