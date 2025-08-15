import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


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
    return render(request, "news.html", data)
