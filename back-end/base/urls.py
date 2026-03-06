from rest_framework.routers import DefaultRouter
from .views import novo_exame
from django.urls import path

router = DefaultRouter()

urlpatterns = [
    path('webhook/novo-exame/', novo_exame),
]

urlpatterns += router.urls