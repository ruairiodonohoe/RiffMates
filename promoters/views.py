from django.shortcuts import render
from time import sleep

# Create your views here.
from promoters.models import Promoter


def promoters(request):
    return render(request, "promoters.html")


def partial_promoters(request):
    sleep(2)
    data = {"promoters": Promoter.objects.all()}
    return render(request, "partials/promoters.html", data)
