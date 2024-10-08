from django.contrib import admin
from django.urls import include, path
from register import views as v

urlpatterns = [
    path('', include('main.urls')), # main will be the name of your app
    path('admin/', admin.site.urls),
    path('register/', v.register, name="register"),
    path('', include("django.contrib.auth.urls")),
]