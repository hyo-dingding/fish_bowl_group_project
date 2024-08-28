# views.py

from django.shortcuts import render, redirect
from .scripts.upload_handlers import handle_text_file, handle_csv_file
from .scripts.llm import process_text
import sys
import logging

# logging.basicConfig(filename='upload_debug.log', level=logging.DEBUG)


from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import upload_file_form
import os
from django.conf import settings
from .models import file_data  
from django.db import models
from .scripts.llm import process_csv, process_text
from .scripts.mp3_to_wav import process_mp3
from .scripts.stt import azure_stt_from_audio_file
from django.shortcuts import render, redirect


# def handle_uploaded_file(f):
#     with open('some/file/name.txt', 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)
            
def handle_uploaded_file(f):
    # 파일이 저장될 경로 설정
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    
    # 경로가 존재하지 않으면 생성
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # 파일을 경로에 저장
    file_path = os.path.join(upload_dir, f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

# 1번
# def upload_file(request):
    # if request.method == 'POST':
    #     form = UploadFileForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         instance = file_data(file_field=request.FILES['file'])
    #         instance.save()  # 파일이 자동으로 media/uploads/에 저장됨
    #         return HttpResponseRedirect('/llm/upload_success/')  # 업로드 성공 시 리디렉션
    # else:
    #     form = UploadFileForm()
    # return render(request, 'upload.html', {'form': form})


# 2번
def upload_file(request):
    if request.method == 'POST':
        form = upload_file_form(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            file_path = instance.file.path  # 저장된 파일의 경로를 가져옴
            if file_path.endswith('.wav'):
                change_wav = file_path
            stt_text = azure_stt_from_audio_file(change_wav)    #stt
            result = process_text(stt_text)  #llm에 넣기
                
            """with open(file_path) as f:
                if file_path.endswith('.mp3'):
                    file_content = f.read()
                    change_wav = process_mp3(file_content)  # mp3 파일 처리
                elif file_path.endswith('.wav'):
                    file_content = f.read()
                    change_wav = file_content   #wav파일은 그대로
                stt_text = azure_stt_from_audio_file(change_wav)    #stt
                result = process_text(stt_text)  #llm에 넣기
            """
            request.session['result'] = result  # 세션에 결과 저장
            return redirect('upload_success')  # 업로드 성공 페이지로 리다이렉트
    else:
        form = upload_file_form()
    
    return render(request, 'upload.html', {'form': form})



def upload_success(request):
    result = request.session.get('result', {})

    if result:
        print("세션에 저장된 결과:", result)  # 서버 로그에 출력해 확인
        return redirect('result_page') 
    else:
        print("세션에 결과가 없습니다.")

    return render(request, 'upload_success.html', {'result': result})


def result_page(request):
    result = request.session.get('result', {})
    return render(request, 'result.html', {'result': result})



