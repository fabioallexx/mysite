from django.contrib import admin
from .models import UploadedFile, Contract, CadernoEncargo, Historico

# Register your models here.
class ContractAdmin(admin.ModelAdmin):
    exclude = ('_estado',)

admin.site.register(UploadedFile)
admin.site.register(Contract, ContractAdmin)
admin.site.register(CadernoEncargo)
admin.site.register(Historico)