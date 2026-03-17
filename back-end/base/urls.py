from rest_framework.routers import DefaultRouter
from django.urls import path

from django.contrib.auth import views as auth_views
from .views import novo_exame, dashboard, home,login_view,sync_exames,laudo_editor,salvar_laudo,portal_exame
router = DefaultRouter()

urlpatterns = [
    path('webhook/novo-exame/', novo_exame),
    path("laudo/<int:exame_id>/", laudo_editor, name="laudo_editor"),
    path("", home, name="home"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("salvar-laudo/", salvar_laudo),
    path("portal/", portal_exame, name="portal_exame"),
    path("portal/<str:codigo>/", portal_exame, name="portal_exame_codigo"),
    path("dashboard/", dashboard, name="dashboard"),
    path("sync-exames/", sync_exames, name="sync_exames"),
    path("r/<str:codigo>/", portal_exame, name="portal_exame_direto"),

]
urlpatterns += router.urls

