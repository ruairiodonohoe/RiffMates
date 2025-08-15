import json
from django.http import HttpResponse


# Create your views here.
def credits(request):
    content = "Nicky\nRuairi"
    return HttpResponse(content, content_type="text/plain")


def about(request):
    content = "<h1>About Me!</h1>"
    return HttpResponse(content, content_type="text/html")


def version_info(request):
    content = {"version": "1.0"}
    content = json.dumps(content)
    return HttpResponse(content, content_type="json")
