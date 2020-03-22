from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from account_management.forms import BankAccountForm

# Create your views here.


@login_required
def open_account(request):
    context = {}
    if request.POST:
        form = BankAccountForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user_id = request.user
            print('saving')
            instance.save()
            # context['request_received'] = True
            return redirect('/accounts/profile')

    else:
        form = BankAccountForm()
        context['bank_form'] = form
        return render(request, 'account_management/open_account.html', context)
