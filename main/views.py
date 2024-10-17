from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import ToDoList, Item, UploadedFile
from .forms import CreateNewList
from datetime import datetime
from dateutil.relativedelta import relativedelta

def index(response, id):
    ls = ToDoList.objects.get(id=id)

    if ls in response.user.todolist.all():

        if response.method == "POST":
            if response.POST.get("save"):
                for item in ls.item_set.all():
                    if response.POST.get("c" + str(item.id)) == "clicked":
                        item.complete = True
                    else:
                        item.complete =False
                    item.save()
            elif response.POST.get("newItem"):
                txt = response.POST.get("new")
                if len(txt) > 2:
                    ls.item_set.create(text=txt, complete=False)
                else:
                    print("invalid")

        return render(response, 'main/list.html', {"ls":ls})
    return render(response, 'main/view.html', {"ls":ls})

def home(response):
    return render(response, 'main/home.html', {})

def create(response):
    if response.method == "POST":
        form = CreateNewList(response.POST)
        
        if form.is_valid():
            n = form.cleaned_data["name"]
            t = ToDoList(name=n)
            t.save()
            response.user.todolist.add(t)

        return HttpResponseRedirect("/%i" %t.id)
    else:    
        form = CreateNewList()
    return render(response, "main/create.html", {"form":form})

def view(response):
    return render(response, "main/view.html", {})

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_instance = UploadedFile(file=uploaded_file, name=uploaded_file.name, user=request.user)
        file_instance.save()
        return redirect('contrato_info', file_id=file_instance.id)
    return redirect('home')

def calcular_diferenca(data_inicial, data_final):
    data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d')
    data_final = datetime.strptime(data_final, '%Y-%m-%d')
    
    diferenca = relativedelta(data_final, data_inicial)
    
    partes = []
    if diferenca.years:
        partes.append(f"{diferenca.years} {'ano' if diferenca.years == 1 else 'anos'}")
    if diferenca.months:
        partes.append(f"{diferenca.months} {'mês' if diferenca.months == 1 else 'meses'}")
    if diferenca.days:
        partes.append(f"{diferenca.days} {'dia' if diferenca.days == 1 else 'dias'}")

    if len(partes) > 1:
        partes[-1] = "e " + partes[-1]  
        return ', '.join(partes[:-1]) + ' ' + partes[-1] 
    elif partes: 
        return partes[0]  
    
    return "0 dias"  

def contrato_info(request, file_id):
    uploaded_file = UploadedFile.objects.get(id=file_id, user=request.user)
    
    procedimento = ""
    numero = ""
    tipo_contrato = ""
    fornecedor = ""
    nif = ""
    data_inicial = ""
    data_final = ""
    prazo = ""
    preco_contratual = ""
    
    if request.method == "POST":
        if "confirmar_datas" in request.POST:
            data_inicial = request.POST.get("data_inicial")
            data_final = request.POST.get("data_final")
            prazo = calcular_diferenca(data_inicial, data_final)
            
            procedimento = request.POST.get("procedimento")
            numero = request.POST.get("numero")
            tipo_contrato = request.POST.get("tipo_contrato")
            fornecedor = request.POST.get("nome")
            nif = request.POST.get("nif")
            preco_contratual = request.POST.get("preco_contratual").replace('€', '').strip()
        
        else:
            procedimento = request.POST.get("procedimento")
            numero = request.POST.get("numero")
            tipo_contrato = request.POST.get("tipo_contrato")
            fornecedor = request.POST.get("nome")
            nif = request.POST.get("nif")
            preco_contratual = request.POST.get("preco_contratual").replace('€', '').strip() 

            print(f"Procedimento selecionado: {procedimento}")
            print(f"Número inserido: {numero}")
            print(f"Tipo de Contrato: {tipo_contrato}")
            print(f"Fornecedor: {fornecedor}")
            print(f"NIF: {nif}")
            print(f"Preço Contratual: {preco_contratual}")

    return render(request, 'main/contrato_info.html', {
        'uploaded_file': uploaded_file,
        'procedimento': procedimento,
        'numero': numero,
        'tipo_contrato': tipo_contrato,
        'fornecedor': fornecedor,
        'nif': nif,
        'data_inicial': data_inicial,
        'data_final': data_final,
        'prazo': prazo,
        'preco_contratual': preco_contratual,
    })

    return render(request, 'main/contrato_info.html', {'uploaded_file': uploaded_file})