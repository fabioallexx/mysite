from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import ToDoList, Item, UploadedFile
from .forms import CreateNewList

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

def contrato_info(request, file_id):
    uploaded_file = UploadedFile.objects.get(id=file_id, user=request.user)
    
    if request.method == "POST":
        procedimento = request.POST.get("procedimento")
        numero = request.POST.get("numero")
        tipo_contrato = request.POST.get("tipo_contrato")
        fornecedor = fornecedor.POST.get("fornecedor")
        nif = nif.POST.get("nif")
        
        print(f"Procedimento selecionado: {procedimento}")
        print(f"Número inserido: {numero}")
        print(f"Tipo de Contrato: {tipo_contrato}")
        print(f"Fornecedor: {fornecedor}")
        print(f"NIF: {nif}")

        return render(request, 'main/contrato_info.html', {'uploaded_file': uploaded_file, 'procedimento': procedimento, 'numero': numero, 'tipo_contrato': tipo_contrato, 'fornecedor': fornecedor,
        'nif': nif})
    
    return render(request, 'main/contrato_info.html', {'uploaded_file': uploaded_file})