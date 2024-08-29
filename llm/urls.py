# llm/urls.py

from django.urls import path
from .views import upload_file, upload_success, result_page, check_processing_status

urlpatterns = [
    path("upload/", upload_file, name="file_upload"),
    path("upload_success/", upload_success, name="upload_success"),
    path("result/", result_page, name="result_page"),
    path(
        "check_processing_status/",
        check_processing_status,
        name="check_processing_status",
    ),
]
