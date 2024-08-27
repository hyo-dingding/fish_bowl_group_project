# llm/urls.py

from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import upload_file, upload_success, result_page



urlpatterns = [
	path('upload/', upload_file, name="file_upload"),
    path('upload_success/', upload_success, name='upload_success'),
    path('result/', result_page, name='result_page'),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)