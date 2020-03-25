#from django.contrib.auth import login, authenticate, logout
#from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from transactions.forms import  Trans_Create, Transaction_main, Trans_Create_Credit

from .models import EMP_Transaction_Create
from user_management.models import AccountRequests

def transaction_main(request):
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
    return render(request, 'transactions/trans_main.html', context)

def transaction_details(request):
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
    acc_type= AccountRequests.objects.filter(account_type="Credit").count()
    if acc_type>0:
        context = {'acc_type'}
    else:
        context={}
    return render(request, 'transactions/trans_details.html', context)

def no_transaction_details(request):
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
    return render(request, 'transactions/no_trans_details.html', context)



def trans_create(request):
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
    return render(request, 'transactions/trans_create.html', content)

def trans_create_credit(request):
    trans_c = Trans_Create_Credit()
    if request.method == "POST":
        trans_c = Trans_Create_Credit(request.POST)
        if trans_c.is_valid():
            trans_c.save()
            return redirect('/trans')
        else:
            print(trans_c.errors)
    content = {
        "trans_c": trans_c
    }
    return render(request, 'transactions/trans_create_credit.html', content)


def transaction_view(request, id):
    obj = EMP_Transaction_Create.objects.get(id=id)
    context = {
        "obj": obj
    }
    return render(request, "transactions/trans_view.html", context)


def trans_list_view(request):
    object_list = EMP_Transaction_Create.objects.all()
    context = {
        "object_list": object_list
    }
    return render(request, "transactions/trans_list.html", context)

