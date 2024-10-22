from django.contrib import admin
from .models import ToDoList, Item, UploadedFile, Contract, CadernoEncargos

# Register your models here.

admin.site.register(ToDoList)
admin.site.register(Item)
admin.site.register(UploadedFile)
admin.site.register(Contract)
admin.site.register(CadernoEncargos)