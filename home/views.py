import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from datetime import datetime


# Create your views here.
def credits(request):
    content = "Nicky\nRuairi"
    return HttpResponse(content, content_type="text/plain")


def about(request):
    content = "<h1>About Me!</h1>"
    return HttpResponse(content, content_type="text/html")


def version_info(request):
    content = {"version": "1.0"}
    return JsonResponse(content)


def news(request):
    data = {
        "news": [
            "RiffMates now has a news page!",
            "RiffMates has its first web page",
        ]
    }
    return render(request, "news2.html", data)


def news_advanced(request):
    data = {
        "news": [
            (datetime(2025, 8, 15), "RiffMates now has a news page!"),
            (datetime(2025, 8, 14), "RiffMates has its first web page!"),
        ]
    }
    return render(request, "news_adv.html", data)


def home(request):
    return render(request, "home.html")
