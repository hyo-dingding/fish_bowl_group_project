# llm/urls.py

from django.urls import path
from .views import file_upload, upload_success, result_page, check_processing_status

urlpatterns = [
    path("upload/", file_upload, name="file_upload"),
    path("upload_success/", upload_success, name="upload_success"),
    path("result/", result_page, name="result_page"),
    path(
        "check_processing_status/",
        check_processing_status,
        name="check_processing_status",
    ),
]
