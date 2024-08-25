from django.shortcuts import render
# from django.http import HttpResponse

def hello_world(request):
    return render(request, 'accountapp/hello_world.html')
    # 템플릿 가져와서 채워줌
    

    
    
# from django.shortcuts import render
# from .forms import UploadFileForm

# def hello_world(request):
#     if request.method == "POST":
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             handle_uploaded_file(request.FILES['file'])
#             return render(request, 'accountapp/hello_world.html', {'form': form, 'success': True})
#     else:
#         form = UploadFileForm()
    
#     return render(request, 'accountapp/hello_world.html', {'form': form})

# def handle_uploaded_file(f):
#     with open('uploaded_files/' + f.name, 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)
