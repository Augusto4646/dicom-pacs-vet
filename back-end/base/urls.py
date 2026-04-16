from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Autenticação
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),

    # Dashboard
    path('dashbord/', views.dashbord, name='dashbord'),
    path('menu/', views.menu, name='menu'),
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
    path('dicom-para-imagens/<int:exame_id>/', views.dicom_para_imagens),
    # Portal do paciente (sem código = página de busca)
    path('portal/', views.portal_exame, name='portal'),
    path('portal/<str:codigo>/', views.portal_exame, name='portal_exame'),

    # Editar paciente
    path('editar-paciente/<int:exame_id>/', views.editar_paciente, name='editar_paciente'),
    path("baixar/<int:exame_id>/", views.baixar_dicom, name="baixar_dicom"),
    # Listar criar e deletar modelos
    path('listar_modelos/',views.listar_modelos,name='listar_modelos'),
    path('criar_modelos/',views.criar_modelos,name='criar_modelos'),
    path('atualizar_status/<int:exame_id>/',views.atualizar_status),
    path('atualizar_status_laudo_editor/<int:exame_id>/', views.atualizar_status_laudo_editor),
    path('dashboard_visual/',views.dashboard_visual,name='dashboard_visual'),
    path('editar_cabecalho/<int:exame_id>/', views.editar_cabecalho, name='editar_cabecalho'),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
