
from adminpanel.common_imports import *

# def index(request):
#     return render(request, "index.html")

# def userdashboard(request):
#     return render(request, "userdashboard.html")

def admindashboard(request):
    return render(request, "admindashboard.html")


def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)