from django.shortcuts import render
from django.contrib import auth
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from models import *
from forms import *


def index(request):
    if request.method == "POST" and "logarGlobal" in request.POST:  # global login
        return login(request)

    if request.method == "POST" and "cadastrarGlobal" in request.POST:
        return HttpResponseRedirect('/cadastro')

    if request.method == "POST" and "sairGlobal" in request.POST:
        auth.logout(request)
        return HttpResponseRedirect('/')

    return render(request, "home.html")

def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    if request.method == "POST" and "cadastrarGlobal" in request.POST:
        return HttpResponseRedirect("/cadastro")

    avisos= []
    if request.method == "POST" and "voltar" in request.POST:
        return HttpResponseRedirect('/')

    elif request.method == "POST" and ("logar" in request.POST
                                    or "cadastrar" in request.POST
                                    or "logarGlobal" in request.POST):
        form = LoginForm(request.POST)

        if form.is_valid():
            user = auth.authenticate(username=form.cleaned_data.get("nome"),
                                     password=form.cleaned_data.get("senha"))
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect("/")
                else:
                    avisos.append("Essa conta foi desativada.")
            else:
                request.path= "/login/" #TODO bug consertar
                avisos.append("Senha ou usuario incorretos.")

    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form, "avisos": avisos})


def cadastro(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    if request.method == "POST" and "logarGlobal" in request.POST:  # global login
        return login(request)

    avisos = []
    if request.method == "POST" and "voltar" in request.POST:
        return HttpResponseRedirect('/')

    elif request.method == "POST" and "cadastrar" in request.POST:
        form = CadastroForm(request.POST)

        if form.is_valid():
            if auth.models.User.objects.filter(username=form.cleaned_data.get("nome")).count() == 0:
                grupo = auth.models.Group.objects.get(name="Clientes")
                user = auth.models.User.objects.create_user(form.cleaned_data.get("nome"),
                                                            "emal", form.cleaned_data.get("senha"))
                user.groups.add(grupo)
                user.save()
                avisos.append("Cadastrado Com Sucesso")
                return login(request)

            else:
                avisos.append("Usuario ja existe")
                form = CadastroForm()
    else:
        form = CadastroForm()

    return render(request, "cadastro.html", {"form": form, "clientes": auth.models.User.objects.all(),
                                             "avisos": avisos})


def favoritos(request):
    if not request.user.groups.filter(name="Clientes").exists():
        return HttpResponseRedirect("/")

    if request.method == "POST" and "sairGlobal" in request.POST:
        auth.logout(request)
        return HttpResponseRedirect("/")

    return render(request, "favoritos.html")

def produtos(request):
    if not request.user.groups.filter(name="Donos").exists():
        return HttpResponseRedirect("/")

    if request.method == "POST" and "sairGlobal" in request.POST:
        auth.logout(request)
        return HttpResponseRedirect("/")

    avisos= []
    produtos= []
    if request.method == "POST" and "cadastrarProd" in request.POST:
        form = CadastroProd(request.POST)

        if form.is_valid():
            dono= Dono.objects.filter(idEmpresario=request.user.id)[0]

            possui= Possui()
            produto = Produto()
            produto.nome = form.cleaned_data.get("nome")
            produto.marca = form.cleaned_data.get("marca")
            produto.save()

            possui.idProduto = produto
            possui.idSupermercado = dono.idSupermercado
            possui.preco = form.cleaned_data.get("preco")
            possui.quantidade = form.cleaned_data.get("quantidade")
            possui.save()
            form = CadastroProd()
        else:
            avisos.append("Produto Invalido")
    else:
        form = CadastroProd()

    dono = Dono.objects.filter(idEmpresario=request.user.id)[0]
    produtos = Possui.objects.filter(idSupermercado=dono.idSupermercado)
    return render(request, "produtos.html", {"form":form, "avisos":avisos,
                                             "produtos": produtos})

def sobre(request):
    if request.method == "POST" and "logarGlobal" in request.POST:  # global login
        return login(request)

    if request.method == "POST" and "sairGlobal" in request.POST:
        auth.logout(request)
        return HttpResponseRedirect("/")

    if request.method == "POST" and "cadastrarGlobal" in request.POST:
        return HttpResponseRedirect("/cadastro")

    return render(request, "sobre.html")

def cadastroDono(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")

    if request.method == "POST" and "sairGlobal" in request.POST:
        auth.logout(request)
        return HttpResponseRedirect("/")

    avisos= []
    if request.method == "POST" and "cadastrar" in request.POST:
        form = CadastroDono(request.POST)
        if form.is_valid():
            if auth.models.User.objects.filter(username=form.cleaned_data.get("nome")).exists():
                avisos.append("Usuario ja existe")
            else:
                #usuario = Usuario()
                supermercado = Supermercado()
                grupo = auth.models.Group.objects.get(name="Donos")
                user = auth.models.User.objects.create_user(form.cleaned_data.get("nome"),
                                                            "emal",
                                                            form.cleaned_data.get("senha"))
                user.groups.add(grupo)
                user.save()
                #empresaio= Empresario()
                dono= Dono()
                #usuario.nome = form.cleaned_data.get("nome")
                #usuario.senha = form.cleaned_data.get("senha")
                supermercado.nome = form.cleaned_data.get("nomeSupermercado")
                supermercado.localizacao = form.cleaned_data.get("localizacao")
                #usuario.save()
                supermercado.save()
                #empresaio.idEmpresario = usuario
                #empresaio.CNPJ = form.cleaned_data.get("CNPJ")
                #empresaio.save()
                dono.idEmpresario = user
                dono.idSupermercado = supermercado
                dono.CNPJ= form.cleaned_data.get("CNPJ")
                dono.save()

                form = CadastroDono()
                avisos.append("Cadastrado Com Sucesso") #TODO mudar cor do aviso no html
        else:
            avisos.append("Erro Formulario")
    else:
        form= CadastroDono()
    return render(request, "cadastroDono.html", {"form":form, "avisos":avisos})

def pesquisa(request):
    pesquisa = []
    if request.method == "POST" and "buscaSimples" in request.POST:
        pesAux = Produto.objects.filter(nome__icontains = request.POST.get("buscaNome"))
        pesquisa = Possui.objects.filter(idProduto__in = pesAux)

    return render(request, "pesquisa.html", {"pesquisa":pesquisa})