from django.db import models
from django.contrib.auth.models import User
import json

# Create your models here.

class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploadedfile')
    file = models.FileField(upload_to='uploads/')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
	
class Contract(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    objeto = models.CharField(max_length=255)
    procedimento = models.CharField(max_length=255)
    tipo_produto = models.CharField(max_length=255)
    numero = models.CharField(max_length=100)
    tipo_contrato = models.CharField(max_length=100)
    fornecedor = models.CharField(max_length=255)
    nif = models.CharField(max_length=100)
    data_inicial = models.DateField()
    data_final = models.DateField()
    prazo = models.CharField(max_length=255)
    preco_contratual = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.CharField(max_length=100)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    observacao = models.TextField(blank=True, null=True)
    valor_entregue = models.DecimalField(max_digits=10, decimal_places=2)
    recorrente = models.BooleanField(default=False)
    compromisso = models.BooleanField(default=False)
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    plurianual = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)
    alerta_prazo = models.CharField(max_length=100)

    @property
    def is_active(self):
        return self.estado

    def __str__(self):
        return f"{self.numero} - {self.fornecedor}"
    
class CadernoEncargo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    procedimento_n = models.CharField(max_length=255)
    contrato_celebrado = models.CharField(max_length=255)
    periodo_vigencia = models.CharField(max_length=255)
    valor_contrato = models.DecimalField(max_digits=10, decimal_places=2)
    fornecedor = models.CharField(max_length=255)
    nif = models.CharField(max_length=100)
    cumprimento_prazo = models.BooleanField()
    penalidade = models.BooleanField()
    justificar_prazo = models.TextField(blank=True, null=True)
    defeitos = models.TextField(blank=True, null=True)
    sugestoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Relatório de {self.fornecedor} - {self.procedimento_n}"
    
class Historico(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    objeto = models.CharField(max_length=255)
    procedimento = models.CharField(max_length=255)
    tipo_produto = models.CharField(max_length=255)
    numero = models.CharField(max_length=100)
    tipo_contrato = models.CharField(max_length=100)
    fornecedor = models.CharField(max_length=255)
    nif = models.CharField(max_length=100)
    data_inicial = models.DateField()
    data_final = models.DateField()
    prazo = models.CharField(max_length=255)
    preco_contratual = models.DecimalField(max_digits=10, decimal_places=2)
    observacao = models.TextField(blank=True, null=True)
    valor_entregue = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.CharField(max_length=100)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    recorrente = models.BooleanField(default=False)
    compromisso = models.BooleanField(default=False)
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    plurianual = models.TextField(blank=True, null=True)
    _estado = models.BooleanField(default=False)
    alerta_prazo = models.CharField(max_length=100)

    def reativar_contrato(self):
        if self._estado:
            Contract.objects.create(
                user=self.user,
                objeto=self.objeto,
                procedimento=self.procedimento,
                tipo_produto=self.tipo_produto,
                numero=self.numero,
                tipo_contrato=self.tipo_contrato,
                fornecedor=self.fornecedor,
                nif=self.nif,
                data_inicial=self.data_inicial,
                data_final=self.data_final,
                prazo=self.prazo,
                preco_contratual=self.preco_contratual,
                observacao=self.observacao,
                valor_entregue=self.valor_entregue,
                recorrente=self.recorrente,
                iva=self.iva,
                valor_total=self.valor_total,
                compromisso=self.compromisso,
                uploaded_file=self.uploaded_file,
                plurianual=self.plurianual,
                estado=True,
                alerta_prazo=self.alerta_prazo,
            )

class Fatura(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    numero = models.CharField(max_length=100)
    nif = models.CharField(max_length=100)
    data = models.DateField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    mydoc = models.CharField(max_length=100)