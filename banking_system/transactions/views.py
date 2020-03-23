from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from transactions.forms import Trans_Create, Transaction_main

from .models import EMP_Transaction_Create


@login_required
def transaction_main(request):
    if request.user.is_authenticated:
        """trans=Transaction_main()
        if request.method=="POST":
            trans = Transaction_main(request.POST)
            if trans.is_valid():
                trans.save()
                return redirect('/trans/create')
            else:
                print(trans.errors)
        context={
            'trans':trans
        }"""
        request.method == "POST"
        context = {}
        return render(request, 'user_management/trans_main.html', context)
    else:
        return render(request, 'user_management/login.html')

@login_required
def transaction_details(request):
    if request.user.is_authenticated:
        """trans=Transaction_main()
        if request.method=="POST":
            trans = Transaction_main(request.POST)
            if trans.is_valid():
                trans.save()
                return redirect('/trans/create')
            else:
                print(trans.errors)
        context={
            'trans':trans
        }"""
        request.method == "POST"
        context = {}
        return render(request, 'user_management/trans_details.html', context)
    else:
        return render(request, 'user_management/login.html')


@login_required
def trans_create(request):
    if request.user.is_authenticated:
        trans_c = Trans_Create()
        if request.method == "POST":
            trans_c = Trans_Create(request.POST)
            if trans_c.is_valid():
                trans_c.save()
                return redirect('/trans')
            else:
                print(trans_c.errors)
        content = {
            "trans_c": trans_c
        }
        return render(request, 'user_management/trans_create.html', content)
    else:
        return render(request, 'user_management/login.html')


@login_required
def transaction_view(request, id):
    if request.user.is_authenticated:
        obj = EMP_Transaction_Create.objects.get(id=id)
        context = {
            "obj": obj
        }
        return render(request, "user_management/trans_view.html", context)
    else:
        return render(request, 'user_management/login.html')


@login_required
def trans_list_view(request):
    if request.user.is_authenticated:
        object_list = EMP_Transaction_Create.objects.all()
        context = {
            "object_list": object_list
        }
        return render(request, "user_management/trans_list.html", context)
    else:
        return render(request, 'user_management/login.html')
