from django.urls import path
from . import views

urlpatterns = [

    # Autenticação
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Sync Orthanc
    path('sync/', views.sync_exames, name='sync_exames'),

    # Webhook (Orthanc → Django)
    path('webhook/novo-exame/', views.novo_exame, name='novo_exame'),

    # Editor de laudo
    path('laudo/<int:exame_id>/', views.laudo_editor, name='laudo_editor'),

    # Salvar laudo em HTML
    path('salvar-laudo/', views.salvar_laudo, name='salvar_laudo'),

    # ✅ Salvar PDF (base64 enviado pelo frontend)
    path('salvar-pdf/<int:exame_id>/', views.salvar_pdf, name='salvar_pdf'),

    # Upload de PDF via formulário
    path('upload-pdf/', views.upload_laudo_pdf, name='upload_laudo_pdf'),

    # Portal do paciente (sem código = página de busca)
    path('portal/', views.portal_exame, name='portal'),
    path('portal/<str:codigo>/', views.portal_exame, name='portal_exame'),

    # Editar paciente
    path('editar-paciente/<int:exame_id>/', views.editar_paciente, name='editar_paciente'),
    path('forcar-codigos/', views.forcar_codigos, name='forcar_codigos'),
    path("baixar/<int:exame_id>/", views.baixar_dicom, name="baixar_dicom"),
]
