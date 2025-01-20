from django.urls import path
from app.views import visualizador, process_code

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', visualizador, name='visualizador'),
    path('process-code', process_code, name='process_code'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
