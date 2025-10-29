from django.http import HttpResponse


def index(request):
    return HttpResponse("<h1>Olá — app gerado com template Django minimal</h1>")
