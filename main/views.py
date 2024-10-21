from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import ToDoList, Item, UploadedFile, Contract
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
                        item.complete = False
                    item.save()
            elif response.POST.get("newItem"):
                txt = response.POST.get("new")
                if len(txt) > 2:
                    ls.item_set.create(text=txt, complete=False)
                else:
                    print("invalid")

        return render(response, 'main/list.html', {"ls": ls, "tem_contrato": Contract.objects.filter(user=response.user).exists()})
    return render(response, 'main/view.html', {"ls": ls})

def home(request):
    context = get_global_context(request)
    return render(request, 'main/home.html', context)

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

def gerar_plurianual(data_inicial, data_final):
    anos = []
    if data_inicial and data_final:
        ano_inicial = datetime.strptime(data_inicial, '%Y-%m-%d').year
        ano_final = datetime.strptime(data_final, '%Y-%m-%d').year
        anos = list(range(ano_inicial, ano_final + 1))
    return anos

def contrato_info(request, file_id):
    uploaded_file = UploadedFile.objects.get(id=file_id, user=request.user)
    tem_contrato = Contract.objects.filter(user=request.user).exists() if request.user.is_authenticated else False
    contract = Contract.objects.filter(uploaded_file=uploaded_file, user=request.user).first()
    if request.method == "POST":
        procedimento = request.POST.get("procedimento", "")
        numero = request.POST.get("numero", "")
        tipo_contrato = request.POST.get("tipo_contrato", "")
        fornecedor = request.POST.get("nome", "")
        nif = request.POST.get("nif", "")
        data_inicial = request.POST.get("data_inicial", "")
        data_final = request.POST.get("data_final", "")
        preco_contratual_str = request.POST.get("preco_contratual", "").replace('€', '').replace('.', '').replace(',', '.').strip()
        valor_entregue_str = request.POST.get("valor_entregue", "").replace('€', '').replace('.', '').replace(',', '.').strip()
        preco_contratual = float(preco_contratual_str) if preco_contratual_str else 0.0
        valor_entregue = float(valor_entregue_str) if valor_entregue_str else 0.0
        observacao = request.POST.get("observacao", "")
        recorrente = request.POST.get("recorrente") == "Sim"
        compromisso = request.POST.get("compromisso") == "Sim"
        prazo = calcular_diferenca(data_inicial, data_final)
        
        if contract:
            contract.procedimento = procedimento
            contract.numero = numero
            contract.tipo_contrato = tipo_contrato
            contract.fornecedor = fornecedor
            contract.nif = nif
            contract.data_inicial = data_inicial
            contract.data_final = data_final
            contract.prazo = prazo
            contract.preco_contratual = preco_contratual
            contract.observacao = observacao
            contract.valor_entregue = valor_entregue
            contract.recorrente = recorrente
            contract.compromisso = compromisso
            contract.save()
        else:
            contract = Contract(
                user=request.user,
                procedimento=procedimento,
                numero=numero,
                tipo_contrato=tipo_contrato,
                fornecedor=fornecedor,
                nif=nif,
                data_inicial=data_inicial,
                data_final=data_final,
                prazo=prazo,
                preco_contratual=preco_contratual,
                observacao=observacao,
                valor_entregue=valor_entregue,
                recorrente=recorrente,
                compromisso=compromisso,
                uploaded_file=uploaded_file,
            )
            contract.save()
        return redirect('admin:main_contract_changelist')
    return render(request, 'main/contrato_info.html', {
        'uploaded_file': uploaded_file,
        "tem_contrato": tem_contrato,
        "contract": contract,
        "procedimento": contract.procedimento if contract else '',
        "numero": contract.numero if contract else '',
        "tipo_contrato": contract.tipo_contrato if contract else '',
        "fornecedor": contract.fornecedor if contract else '',
        "nif": contract.nif if contract else '',
        "data_inicial": contract.data_inicial if contract else '',
        "data_final": contract.data_final if contract else '',
        "prazo": contract.prazo if contract else '',
        "preco_contratual": contract.preco_contratual if contract else '',
        "observacao": contract.observacao if contract else '',
        "valor_entregue": contract.valor_entregue if contract else '',
        "recorrente": 'Sim' if contract and contract.recorrente else 'Não',
        "compromisso": 'Sim' if contract and contract.compromisso else 'Não'
    })

def get_global_context(request):
    return {
        'tem_contrato': Contract.objects.filter(user=request.user).exists() if request.user.is_authenticated else False,
        'is_contrato_detalhes': request.path.startswith('/contrato/detalhes/')
    }

def caderno_encargos(request):
    # Lógica para a página do caderno de encargos
    return render(request, 'main/caderno_encargos.html')

def contrato_detalhes(request, contract_id):
    contract = Contract.objects.get(id=contract_id, user=request.user)
    context = {'contract': contract}
    context.update(get_global_context(request))
    return render(request, 'main/contrato_detalhes.html', context)