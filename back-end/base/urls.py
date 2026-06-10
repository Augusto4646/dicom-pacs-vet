from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .dicom_utils import get_jpg_urls_for_study
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
    path('laudo_editor/<int:exame_id>/', views.laudo_editor, name='laudo_editor'),
    path('view_monitor/<int:exame_id>/', views.view_monitor, name='view_monitor'),

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
    path('listar_clinicas/',views.listar_clinicas,name='listar_clinicas'),
    path('criar_clinica/',views.criar_clinica,name='criar_clinica'),
    path('deletar_clinica/<int:clinica_id>/', views.deletar_clinica, name='deletar_clinica'),
    path('editar_clinica/<int:clinica_id>/', views.editar_clinica, name='editar_clinica'),

    path('criar_modelos/',views.criar_modelos,name='criar_modelos'),
    path('atualizar_status/<int:exame_id>/', views.atualizar_status),
    path('atualizar_status_laudo_editor/<int:exame_id>/', views.atualizar_status_laudo_editor),
    path('atualizar_tipo_exame/<int:exame_id>/', views.atualizar_tipo_exame, name='atualizar_tipo_exame'),    path('dashboard_visual/',views.dashboard_visual,name='dashboard_visual'),
    path('editar_cabecalho/<int:exame_id>/', views.editar_cabecalho, name='editar_cabecalho'),
    path('pagina_laudos/',views.pagina_laudos,name='pagina_laudos'),
    path('listar_veterinarios/', views.listar_veterinarios,name='listar_veterinarios'),
    path('criar_veterinario/', views.criar_veterinario,name='criar_veterinario'),
    path('deletar_modelo/<int:modelo_id>/', views.deletar_modelo),
    path('deletar_clinica/<int:clinica_id>/',views.deletar_clinica),
    path('deletar_veterinario/<int:veterinario_id>/',views.deletar_veterinario),   
    path('deletar_exame/<int:exame_id>/', views.deletar_exame, name='deletar_exame'),
    path(
    'financeiro/',
    views.financeiro,
    name='financeiro'
    ),
    path('financeiro/excluir/<int:id>/', views.excluir_lancamento, name='excluir_lancamento'),
    path('financeiro/importar/',views.importar_lancamentos, name='importar_lancamentos'),
    path('dicom-para-imagens/<int:exame_id>/',  views.dicom_para_imagens,   name='dicom_para_imagens'),
    path('get-modelo-html/<int:modelo_id>/<int:exame_id>/', views.get_modelo_html, name='get_modelo_html'),
    path('blank-docx/', views.blank_docx, name='blank_docx'),
    path('modelos/docx/<int:modelo_id>/', views.servir_docx_modelo, name='servir_docx_modelo'),
    path(
    "gerar-pdf-completo/<int:exame_id>/",
    views.gerar_pdf_completo,
    name="gerar_pdf_completo"

),
path(
    "onlyoffice-callback/<int:exame_id>/",
    views.onlyoffice_callback,
    name="onlyoffice_callback"
),

path(
    'forcar-save-onlyoffice/<int:exame_id>/',
    views.forcar_save_onlyoffice,
    name='forcar_save_onlyoffice'
),
path('check-docx/<int:exame_id>/', views.check_docx, name='check_docx'),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
