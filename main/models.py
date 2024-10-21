from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ToDoList(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="todolist", null=True)
	name = models.CharField(max_length=200)

	def __str__(self):
		return self.name


class Item(models.Model):
	todolist = models.ForeignKey(ToDoList, on_delete=models.CASCADE)
	text = models.CharField(max_length=300)
	complete = models.BooleanField()

	def __str__(self):
		return self.text

class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploadedfile')
    file = models.FileField(upload_to='uploads/')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
	
class Contract(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    procedimento = models.CharField(max_length=255)
    numero = models.CharField(max_length=100)
    tipo_contrato = models.CharField(max_length=100)
    fornecedor = models.CharField(max_length=255)
    nif = models.CharField(max_length=100)
    data_inicial = models.DateField()
    data_final = models.DateField()
    prazo = models.CharField(max_length=255)  # Ou use um modelo diferente para armazenar isso
    preco_contratual = models.DecimalField(max_digits=10, decimal_places=2)
    observacao = models.TextField(blank=True, null=True)
    valor_entregue = models.DecimalField(max_digits=10, decimal_places=2)
    recorrente = models.BooleanField(default=False)
    compromisso = models.BooleanField(default=False)
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.numero} - {self.fornecedor}"