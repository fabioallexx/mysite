from django.contrib import admin
from django.urls import include, path
from register import views as v

urlpatterns = [
    path('', include('main.urls')),
    path('', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('register/', v.register, name="register"),
]