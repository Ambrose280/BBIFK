from django.shortcuts import redirect


def application(request):
    return redirect("home")