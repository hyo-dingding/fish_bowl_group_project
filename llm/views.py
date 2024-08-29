# llm/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import upload_file_form
from .models import file_data
from .scripts.stt import azure_stt_from_audio_file
from .scripts.llm import process_text
from asgiref.sync import async_to_sync
import os
from django.conf import settings
import asyncio


def handle_uploaded_file(f):
    upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_path = os.path.join(upload_dir, f.name)
    with open(file_path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path


def upload_file(request):
    if request.method == "POST":
        form = upload_file_form(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            file_path = instance.file.path
            request.session["file_path"] = file_path
            return redirect("upload_success")
    else:
        form = upload_file_form()
    return render(request, "upload.html", {"form": form})


def upload_success(request):
    file_path = request.session.get("file_path", None)
    if file_path:
        return render(request, "upload_success.html", {"file_path": file_path})
    else:
        return redirect("upload")


async def process_file(file_path):
    if file_path.endswith(".wav"):
        change_wav = file_path
    stt_text = azure_stt_from_audio_file(change_wav)
    result = await process_text(stt_text)
    return result


def check_processing_status(request):

    file_path = request.session.get("file_path", None)
    if file_path:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process_file(file_path))
        request.session["result"] = result
        loop.close()
        return JsonResponse({"status": "done"})
    return JsonResponse({"status": "error"})


def result_page(request):
    result = request.session.get("result", {})
    return render(request, "result.html", {"result": result})
