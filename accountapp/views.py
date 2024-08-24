from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.


def hello_world(request):
    return HttpResponse("안녕하세요!")

    