from django.contrib import admin
from .models import UploadedFile, Contract, CadernoEncargo, Historico

class ContractAdmin(admin.ModelAdmin):
    exclude = ('_estado',)

admin.site.register(UploadedFile)
admin.site.register(Contract, ContractAdmin)
admin.site.register(CadernoEncargo)

class HistoricoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fornecedor', 'data_inicial', '_estado')
    list_editable = ('_estado',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj._estado:
            obj.reativar_contrato()
            obj.delete()

admin.site.register(Historico, HistoricoAdmin)