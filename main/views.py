from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, JsonResponse
from .models import UploadedFile, Contract, CadernoEncargo, Historico, Fatura
from datetime import datetime, date, timedelta
import locale
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from decimal import Decimal, InvalidOperation
import mimetypes
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa
import json
from django.template import Context
from django.template.loader import get_template
from django.views.decorators.http import require_http_methods
import os

@require_http_methods(["POST"])
def calcular_diferenca_ajax(request):
    data = json.loads(request.body)
    data_inicial = data.get('data_inicial')
    data_final = data.get('data_final')
    
    prazo = calcular_diferenca(data_inicial, data_final)
    return JsonResponse({'prazo': prazo})

def index(response, id):
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
            return render(response, 'main/list.html', {"tem_contrato": Contract.objects.filter(user=response.user).exists()})

def home(request):
    if request.user.is_authenticated:
        contratos_ativos = []
        for uf in request.user.uploadedfile.all():
            contrato = uf.contract_set.filter(estado=True).first()
            if contrato:
                contratos_ativos.append((uf, contrato))

        context = {
            'contratos_ativos': contratos_ativos,
            **get_global_context(request)
        }
        return render(request, 'main/home.html', context)
    else:
        return render(request, 'main/home.html', {'message': 'Por favor, faça login para ver seus contratos.'})

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)
        if mime_type != 'application/pdf':
            return HttpResponse("Apenas arquivos PDF são permitidos.", status=400)
        
        file_instance = UploadedFile(file=uploaded_file, name=uploaded_file.name, user=request.user)
        file_instance.save()
        
        return redirect('contrato_info', file_id=file_instance.id)
    
    return redirect('home')

def calcular_diferenca(data_inicial, data_final):
    # Converter para datetime se forem strings
    if isinstance(data_inicial, str):
        data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d')
    if isinstance(data_final, str):
        data_final = datetime.strptime(data_final, '%Y-%m-%d')

    # Calcular a diferença diretamente em dias
    diferenca = (data_final - data_inicial).days

    # Verificando a diferença de dias
    if diferenca < 0:
        return "0 dias"  # Se a data final for antes da data inicial

    anos = diferenca // 365  # Aproximadamente 365 dias por ano
    meses = (diferenca % 365) // 30  # Aproximadamente 30 dias por mês
    dias = diferenca % 30  # O resto são os dias restantes

    partes = []
    if anos:
        partes.append(f"{anos} {'ano' if anos == 1 else 'anos'}")
    if meses:
        partes.append(f"{meses} {'mês' if meses == 1 else 'meses'}")
    if dias:
        partes.append(f"{dias} {'dia' if dias == 1 else 'dias'}")

    # Se houver mais de um componente de tempo, unimos com 'e'
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

def contrato_editar(request, file_id):
    uploaded_file = UploadedFile.objects.get(id=file_id, user=request.user)
    tem_contrato = Contract.objects.filter(user=request.user).exists() if request.user.is_authenticated else False
    contract = Contract.objects.filter(uploaded_file=uploaded_file, user=request.user).first()
    estado = True

    anos_plurianual = []
    if contract and contract.data_inicial and contract.data_final:
        ano_inicial = contract.data_inicial.year
        ano_final = contract.data_final.year
        anos_plurianual = list(range(ano_inicial, ano_final + 1))

    if request.method == 'POST':
        objeto = request.POST.get("objeto", "")
        procedimento = request.POST.get("procedimento", "")
        tipo_produto = request.POST.get("tipo_produto", "")
        numero = request.POST.get("numero", "")
        tipo_contrato = request.POST.get("tipo_contrato", "")
        fornecedor = request.POST.get("fornecedor", "")
        nif = request.POST.get("nif", "")
        data_inicial = request.POST.get("data_inicial", "")
        data_final = request.POST.get("data_final", "")
        plurianual = ', '.join(map(str, anos_plurianual))
        preco_contratual_str = request.POST.get("preco_contratual", "").replace('€', '').replace('.', '').replace(',', '.').strip()
        valor_entregue_str = request.POST.get("valor_entregue", "").replace('€', '').replace('.', '').replace(',', '.').strip()
        preco_contratual = float(preco_contratual_str) if preco_contratual_str else 0.0
        valor_entregue = float(valor_entregue_str) if valor_entregue_str else 0.0
        iva_str = request.POST.get("iva", "").replace('€', '').replace('.', '').replace(',', '.').strip()
        iva = float(iva_str.replace('%', '').strip()) / 100 if iva_str else 0.0
        valor_total = preco_contratual * (1 + iva)
        observacao = request.POST.get("observacao", "")
        recorrente = request.POST.get("recorrente") == "Sim"
        compromisso = request.POST.get("compromisso") == "Sim"
        prazo = calcular_diferenca(data_inicial, data_final)
        alerta_prazo = request.POST.get("alerta_prazo", "")

        plurianual_values = {}
        for key, value in request.POST.items():
            if key.startswith('plurianual_valor_'):
                year = key.split('_')[-1]
                try:
                    value = value.replace('€', '').replace('.', '').replace(',', '.').strip()
                    value_float = float(value) if value else 0.0
                    plurianual_values[year] = value_float
                except ValueError:
                    messages.warning(request, f"Valor inválido para o ano {year}")
                    plurianual_values[year] = 0.0

        total_allocated = sum(plurianual_values.values())
        if total_allocated > valor_total:
            messages.error(request, 
                f"Total alocado ({total_allocated:.2f}€) excede o valor do contrato ({valor_total:.2f}€)")

        plurianual_json = json.dumps(plurianual_values) if plurianual_values else None
        
        if contract:
            estado = contract.estado
            contract.objeto = objeto
            contract.procedimento = procedimento
            contract.tipo_produto = tipo_produto
            contract.numero = numero
            contract.tipo_contrato = tipo_contrato
            contract.fornecedor = fornecedor
            contract.nif = nif
            contract.data_inicial = data_inicial
            contract.data_final = data_final
            contract.prazo = prazo
            contract.preco_contratual = preco_contratual
            contract.iva = iva
            contract.valor_total = valor_total
            contract.observacao = observacao
            contract.valor_entregue = valor_entregue
            contract.recorrente = recorrente
            contract.compromisso = compromisso
            contract.estado = estado
            contract.alerta_prazo = alerta_prazo
            contract.plurianual = plurianual_json
            contract.save()
        else:
            contract = Contract(
                user=request.user,
                objeto=objeto,
                procedimento=procedimento,
                tipo_produto=tipo_produto,
                numero=numero,
                tipo_contrato=tipo_contrato,
                fornecedor=fornecedor,
                nif=nif,
                data_inicial=data_inicial,
                data_final=data_final,
                prazo=prazo,
                preco_contratual=preco_contratual,
                iva=iva,
                valor_total=valor_total,
                observacao=observacao,
                valor_entregue=valor_entregue,
                recorrente=recorrente,
                compromisso=compromisso,
                uploaded_file=uploaded_file,
                plurianual=plurianual_json,
                anos_plurianual=anos_plurianual,
                estado=True,
                alerta_prazo=alerta_prazo,
            )
            contract.save()
        return redirect('contrato_detalhes', contract_id=contract.id)
    plurianual_values = {}
    if contract and contract.plurianual:
        try:
            plurianual_values = json.loads(contract.plurianual)
        except (json.JSONDecodeError, TypeError):
            plurianual_values = {}
    return render(request, 'main/contrato_editar.html', {
        'uploaded_file': uploaded_file,
        "tem_contrato": tem_contrato,
        "contract": contract,
        "objeto": contract.objeto if contract else '',
        "procedimento": contract.procedimento if contract else '',
        "tipo_produto": contract.tipo_produto if contract else '',
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
        "iva": contract.iva if contract else '',
        "valor_total": contract.valor_total if contract else '',
        "recorrente": 'Sim' if contract and contract.recorrente else 'Não',
        "compromisso": 'Sim' if contract and contract.compromisso else 'Não',
        "plurianual": contract.plurianual if contract else '',
        "estado": contract.estado if contract else True, 
        "alerta_prazo": contract.alerta_prazo if contract else '',
        "plurianual_values": plurianual_values,
        "plurianual": contract.plurianual if contract else '',
        "anos_plurianual": anos_plurianual,
    })

def contrato_info(request, file_id):
    uploaded_file = UploadedFile.objects.get(id=file_id, user=request.user)
    tem_contrato = Contract.objects.filter(user=request.user).exists() if request.user.is_authenticated else False
    contract = Contract.objects.filter(uploaded_file=uploaded_file, user=request.user).first()
    estado = True

    anos_plurianual = []
    if contract and contract.data_inicial and contract.data_final:
        ano_inicial = contract.data_inicial.year
        ano_final = contract.data_final.year
        anos_plurianual = list(range(ano_inicial, ano_final + 1))

    if request.method == "POST":
        objeto = request.POST.get("objeto", "")
        procedimento = request.POST.get("procedimento", "")
        tipo_produto = request.POST.get("tipo_produto", "")
        numero = request.POST.get("numero", "")
        tipo_contrato = request.POST.get("tipo_contrato", "")
        fornecedor = request.POST.get("fornecedor", "")
        nif = request.POST.get("nif", "")
        data_inicial = request.POST.get("data_inicial", "")
        data_final = request.POST.get("data_final", "")
        plurianual = ', '.join(map(str, anos_plurianual))
        preco_contratual_str = request.POST.get("preco_contratual", "").replace('€', '').replace('.', '').replace(',', '.').strip()
        valor_entregue_str = request.POST.get("valor_entregue", "").replace('€', '').replace('.', '').replace(',', '.').strip()
        preco_contratual = float(preco_contratual_str) if preco_contratual_str else 0.0
        valor_entregue = float(valor_entregue_str) if valor_entregue_str else 0.0
        iva_str = request.POST.get("iva", "").replace('€', '').replace('.', '').replace(',', '.').strip()
        iva = float(iva_str.replace('%', '').strip()) / 100 if iva_str else 0.0
        valor_total = preco_contratual * (1 + iva)
        observacao = request.POST.get("observacao", "")
        recorrente = request.POST.get("recorrente") == "Sim"
        compromisso = request.POST.get("compromisso") == "Sim"
        prazo = calcular_diferenca(data_inicial, data_final)
        alerta_prazo = request.POST.get("alerta_prazo", "")

        plurianual_values = {}
        for key, value in request.POST.items():
            if key.startswith('plurianual_valor_'):
                year = key.split('_')[-1]
                try:
                    value = value.replace('€', '').replace('.', '').replace(',', '.').strip()
                    value_float = float(value) if value else 0.0
                    plurianual_values[year] = value_float
                except ValueError:
                    messages.warning(request, f"Valor inválido para o ano {year}")
                    plurianual_values[year] = 0.0

        total_allocated = sum(plurianual_values.values())
        if total_allocated > valor_total:
            messages.error(request, 
                f"Total alocado ({total_allocated:.2f}€) excede o valor do contrato ({valor_total:.2f}€)")

        plurianual_json = json.dumps(plurianual_values) if plurianual_values else None
        
        if contract:
            estado = contract.estado
            contract.objeto = objeto
            contract.procedimento = procedimento
            contract.tipo_produto = tipo_produto
            contract.numero = numero
            contract.tipo_contrato = tipo_contrato
            contract.fornecedor = fornecedor
            contract.nif = nif
            contract.data_inicial = data_inicial
            contract.data_final = data_final
            contract.prazo = prazo
            contract.preco_contratual = preco_contratual
            contract.iva = iva
            contract.valor_total = valor_total
            contract.observacao = observacao
            contract.valor_entregue = valor_entregue
            contract.recorrente = recorrente
            contract.compromisso = compromisso
            contract.estado = estado
            contract.alerta_prazo = alerta_prazo
            contract.plurianual = plurianual_json
            contract.save()
        else:
            contract = Contract(
                user=request.user,
                objeto=objeto,
                procedimento=procedimento,
                tipo_produto=tipo_produto,
                numero=numero,
                tipo_contrato=tipo_contrato,
                fornecedor=fornecedor,
                nif=nif,
                data_inicial=data_inicial,
                data_final=data_final,
                prazo=prazo,
                preco_contratual=preco_contratual,
                iva=iva,
                valor_total=valor_total,
                observacao=observacao,
                valor_entregue=valor_entregue,
                recorrente=recorrente,
                compromisso=compromisso,
                uploaded_file=uploaded_file,
                plurianual=plurianual_json,
                anos_plurianual=anos_plurianual,
                estado=True,
                alerta_prazo=alerta_prazo,
            )
            contract.save()
        return redirect('contrato_detalhes', contract_id=contract.id)
    plurianual_values = {}
    if contract and contract.plurianual:
        try:
            plurianual_values = json.loads(contract.plurianual)
        except (json.JSONDecodeError, TypeError):
            plurianual_values = {}
    return render(request, 'main/contrato_info.html', {
        'uploaded_file': uploaded_file,
        "tem_contrato": tem_contrato,
        "contract": contract,
        "objeto": contract.objeto if contract else '',
        "procedimento": contract.procedimento if contract else '',
        "tipo_produto": contract.tipo_produto if contract else '',
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
        "iva": contract.iva if contract else '',
        "valor_total": contract.valor_total if contract else '',
        "recorrente": 'Sim' if contract and contract.recorrente else 'Não',
        "compromisso": 'Sim' if contract and contract.compromisso else 'Não',
        "plurianual": contract.plurianual if contract else '',
        "estado": contract.estado if contract else True, 
        "alerta_prazo": contract.alerta_prazo if contract else '',
        "plurianual_values": plurianual_values,
        "plurianual": contract.plurianual if contract else '',
        "anos_plurianual": anos_plurianual,
    })

def get_global_context(request):
    return {
        'tem_contrato': Contract.objects.filter(user=request.user).exists() if request.user.is_authenticated else False,
        'is_contrato_detalhes': request.path.startswith('/contrato/detalhes/')
    }

def caderno_encargos(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id, user=request.user)

    if request.method == "POST":
        procedimento_n = request.POST.get("procedimento_n")
        contrato_celebrado = request.POST.get("contrato_celebrado")
        periodo_vigencia = request.POST.get("periodo_vigencia")

        valor_contrato_str = request.POST.get("valor_contrato", "").replace('€', '').replace('.', '').replace(',', '.').strip()
        try:
            valor_contrato = float(valor_contrato_str) if valor_contrato_str else 0.0
        except ValueError:
            error_message = "Valor inválido para o contrato."
            return render(request, 'main/caderno_encargos.html', {'contract_data': contract, 'error_message': error_message})

        fornecedor = request.POST.get("fornecedor")
        nif = request.POST.get("nif")
        cumprimento_prazo = request.POST.get("cumprimento_prazo") == "sim"
        penalidade = request.POST.get("penalidade") == "sim"

        justificar_prazo = request.POST.get("justificar_prazo", "") if not penalidade else ""

        defeitos = request.POST.get("defeitos", "")
        sugestoes = request.POST.get("sugestoes", "")

        caderno = CadernoEncargo(
            user=request.user,
            procedimento_n=procedimento_n,
            contrato_celebrado=contrato_celebrado,
            periodo_vigencia=periodo_vigencia,
            valor_contrato=valor_contrato,
            fornecedor=fornecedor,
            nif=nif,
            cumprimento_prazo=cumprimento_prazo,
            penalidade=penalidade,
            justificar_prazo=justificar_prazo if not penalidade else None,
            defeitos=defeitos,
            sugestoes=sugestoes,
        )
        caderno.save()
        return redirect('caderno_encargos', contract_id=contract_id)

    try:
        caderno = CadernoEncargo.objects.get(user=request.user, procedimento_n=contract.numero)
        return render(request, 'main/caderno_encargos_visualizar.html', {'caderno': caderno, 'contract': contract})
    except CadernoEncargo.DoesNotExist:
        contract_data = {
            'procedimento_n': contract.numero,
            'contrato_celebrado': contract.data_inicial,
            'periodo_vigencia': calcular_diferenca(contract.data_inicial, contract.data_final),
            'valor_contrato': contract.valor_total,
            'fornecedor': contract.fornecedor,
            'nif': contract.nif,
        }
        return render(request, 'main/caderno_encargos.html', {'contract_data': contract_data, 'contract': contract})

def contrato_detalhes(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id, user=request.user)

    alerta_prazo = contract.alerta_prazo
    prazo_alerta_data = contract.data_final - timedelta(days=int(alerta_prazo))

    data_atual = timezone.now().date()

    exibir_alerta_prazo = data_atual >= prazo_alerta_data
    dias = (contract.data_final - data_atual).days

    valor_total = contract.valor_total
    valor_entregue = contract.valor_entregue

    porcentagem = (valor_entregue / valor_total) * 100 if valor_total > 0 else 0

    alerta_valor = None
    if porcentagem >= 100:
        alerta_valor = "Atingiu 100% do valor total!"
    elif porcentagem >= 75:
        alerta_valor = "Atingiu 75% do valor total!"
    elif porcentagem >= 50:
        alerta_valor = "Atingiu 50% do valor total!"
    elif porcentagem >= 25:
        alerta_valor = "Atingiu 25% do valor total!"

    context = {
        'contract': contract,
        'faturas_existem': contract.fatura_set.exists(),
        'exibir_alerta_prazo': exibir_alerta_prazo,
        'exibir_alerta_valor': alerta_valor is not None,
        'alerta_valor': alerta_valor,
        'dias': dias,
    }
    context.update(get_global_context(request))
    return render(request, 'main/contrato_detalhes.html', context)

def gerar_plurianual(data_inicial, data_final):
    anos = []
    if data_inicial and data_final:
        ano_inicial = datetime.strptime(data_inicial, '%Y-%m-%d').year
        ano_final = datetime.strptime(data_final, '%Y-%m-%d').year
        anos = list(range(ano_inicial, ano_final + 1))
    return anos

def fechar_contrato(request, contract_id):
    contrato = get_object_or_404(Contract, id=contract_id, user=request.user)

    historico = Historico(
        user=contrato.user,
        objeto=contrato.objeto,
        procedimento=contrato.procedimento,
        tipo_produto=contrato.tipo_produto,
        numero=contrato.numero,
        tipo_contrato=contrato.tipo_contrato,
        fornecedor=contrato.fornecedor,
        nif=contrato.nif,
        data_inicial=contrato.data_inicial,
        data_final=contrato.data_final,
        prazo=contrato.prazo,
        preco_contratual=contrato.preco_contratual,
        observacao=contrato.observacao,
        valor_entregue=contrato.valor_entregue,
        iva=contrato.iva,
        valor_total=contrato.valor_total,
        recorrente=contrato.recorrente,
        compromisso=contrato.compromisso,
        uploaded_file=contrato.uploaded_file,
        plurianual=contrato.plurianual,
        _estado=False,
        alerta_prazo=contrato.alerta_prazo,
    )
    historico.save()

    contrato.delete()

    return redirect('home')

def historico_list(request):
    if request.user.is_authenticated:
        contratos_inativos = Historico.objects.filter(_estado=False, user=request.user)
    else:
        contratos_inativos = []

    context = {
        'contratos_inativos': contratos_inativos,
        **get_global_context(request)
    }
    return render(request, 'main/historico.html', context)

def detalhes_contrato_inativo(request, contract_id):
    contrato = get_object_or_404(Historico, id=contract_id)
    return render(request, 'main/detalhes_contrato_inativo.html', {'contrato': contrato})

def execucao_contrato(request, contract_id):
    contrato = get_object_or_404(Contract, id=contract_id, user=request.user)

    data_atual = timezone.now().date()

    valor_total = contrato.preco_contratual  

    valor_sem_iva = valor_total / Decimal('1.23') if valor_total else Decimal('0.00')
    valor_requisitado = valor_sem_iva  

    context = {
        'contrato': contrato,
        'data_atual': data_atual,
        'valor_sem_iva': valor_sem_iva,  
        'valor_requisitado': valor_requisitado,  
    }
    return render(request, 'main/execucao_contrato.html', context)

@login_required
def inserir_fatura(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)

    if request.method == 'POST':
        numero = request.POST.get('numero')
        data = request.POST.get('data')
        valor_str = request.POST.get('valor', '').replace('€', '').replace('.', '').replace(',', '.').strip()  # Limpeza do valor
        mydoc = request.POST.get('mydoc')

        try:
            valor = Decimal(valor_str) if valor_str else Decimal('0.00')
        except (ValueError, InvalidOperation):
            return render(request, 'main/execucao_financeira.html', {
                'contract': contract,
                'error': "Valor inválido. Por favor, insira um valor numérico válido."
            })

        if contract.valor_entregue + valor > contract.valor_total:
            max_valor = contract.valor_total - contract.valor_entregue
            return render(request, 'main/execucao_financeira.html', {
                'contract': contract,
                'error': f"A soma do valor da fatura e do valor entregue não pode ultrapassar o valor total do contrato. O valor máximo que pode ser inserido é {max_valor:.2f} €."
            })

        fatura = Fatura(
            user=request.user,
            contract=contract,
            numero=numero,
            data=data,
            valor=valor,
            mydoc=mydoc
        )
        fatura.save()

        contract.valor_entregue += valor
        contract.save()

        messages.success(request, "Fatura inserida com sucesso.")
        return redirect('contrato_detalhes', contract_id=contract.id)

    return render(request, 'main/execucao_financeira.html', {'contract': contract})

def lista_faturas(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id, user=request.user)
    faturas = Fatura.objects.filter(contract=contract)

    context = {
        'contract': contract,
        'faturas': faturas,
    }
    return render(request, 'main/lista_faturas.html', context)

def detalhes_fatura(request, fatura_id):
    fatura = get_object_or_404(Fatura, id=fatura_id, user=request.user)
    return render(request, 'main/fatura.html', {'fatura': fatura})

def visualizar_pdf(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id, user=request.user)
    uploaded_file = contract.uploaded_file
    
    file_path = uploaded_file.file.path

    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{uploaded_file.name}"'
        return response
    else:
        return HttpResponse("Arquivo não encontrado.", status=404)

def render_to_pdf(template_src, context_dict={}):
    """Renderiza o HTML para PDF."""

    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_contrato.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erro ao gerar o PDF.')
    return response

def gerar_pdf_caderno(request, caderno_id):
    locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')  # Define o locale para português
    caderno = get_object_or_404(CadernoEncargo, id=caderno_id, user=request.user)

    current_date = datetime.now().strftime('%d de %B de %Y')
    
    context = {
        'caderno_data': {
            'procedimento_n': caderno.procedimento_n,
            'contrato_celebrado': caderno.contrato_celebrado,
            'periodo_vigencia': caderno.periodo_vigencia,
            'valor_contrato': caderno.valor_contrato,
            'fornecedor': caderno.fornecedor,
            'nif': caderno.nif,
            'cumprimento_prazo': caderno.cumprimento_prazo,
            'penalidade': caderno.penalidade,
            'justificar_prazo': caderno.justificar_prazo,
            'defeitos': caderno.defeitos,
            'sugestoes': caderno.sugestoes,
            'current_date': current_date  # Adiciona a data ao contexto
        }
    }
    return render_to_pdf('main/template_relatorio.html', context)