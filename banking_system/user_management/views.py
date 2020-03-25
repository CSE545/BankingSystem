from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from user_management.forms import RegistrationForm, LoginForm, EditForm, AccountOverrideLoginForm
from user_management.models import User, employee_info_update, OverrideRequest
from user_management.utility.twofa import generate_otp, get_user_phone_number, save_otp_in_db  # , send_otp

# Create your views here.


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    context = {}
    if request.POST:
        email = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active:
                form = LoginForm(request, data=request.POST)
                context['login_form'] = form
                is_valid_form = form.is_valid()
                if is_valid_form:
                    login(request, user)
                    return redirect('home')
                else:
                    context['otp_sent'] = True
                    return render(request, 'user_management/login.html', context)
            else:
                context['inactive'] = True
                form = LoginForm(request, data=request.POST)
                context['login_form'] = form
                return render(request, 'user_management/login.html', context)
        else:
            context['user_none'] = True
            form = LoginForm(request, data=request.POST)
            context['login_form'] = form
            return render(request, 'user_management/login.html', context)
    else:
        form = LoginForm()
        context['login_form'] = form
    return render(request, 'user_management/login.html', context)


def register_view(request):
    context = {}
    context['created'] = False
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password1")
            authenticate(email=email, password=raw_password)
            # login(request, user)
            # return redirect('home')
            context['created'] = True
        else:
            context['registration_form'] = form
    else:  # GET REQUEST
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'user_management/register.html', context)


def logout_user(request):
    logout(request)
    context = {}
    form = LoginForm()
    context['login_form'] = form
    return redirect(request, 'user_management/login.html')


@login_required
def view_profile(request):
    if request.user.user_type == 'CUSTOMER':
        base_template_name = 'homepage.html'
    else:
        base_template_name = 'employee_home.html'
    context = {'user': request.user, 'base_template_name': base_template_name}
    return render(request, 'user_management/profile.html', context)


@login_required
def edit_profile(request):
    if request.POST:
        form = EditForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            user_id = int(request.user.user_id)

            num_results = employee_info_update.objects.filter(user_id=user_id, status='NEW').count()
            if num_results > 0:
                return render(request, 'employee_request_already_exists.html')

            new_entry = employee_info_update(user_id=user_id, email=data.get('email'),
                                             first_name=data.get('first_name'),
                                             last_name=data.get('last_name'), phone_number=data.get('phone_number'),
                                             gender=data.get('gender'), status='NEW')
            new_entry.save()

            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            context = {}
            context['request_received'] = True
            return render(request, 'employee_edit_request_submitted.html', context)
    else:
        context = {}
        form = EditForm(instance=request.user)
        context['edit_form'] = form
        return render(request, 'user_management/edit_profile.html', context)


@login_required
def show_pending_employee_requests(request):
    if request.POST:
        employee_info_update.objects.filter(user_id=int(
            request.POST['user_id']), status='NEW').update(status=request.POST['status'])

        if request.POST['status'] == 'APPROVE':
            user_object = User.objects.get(
                user_id=int(request.POST['user_id']))
            user_object.email = request.POST['email_id']
            user_object.first_name = request.POST['first_name']
            user_object.last_name = request.POST['last_name']
            user_object.phone_number = request.POST['phone_number']
            user_object.gender = request.POST['gender']
            user_object.save()

        return render(request, 'user_management/pendingEmployeeRequests.html')
    context = {}
    context['employee_info_update_request'] = {
        'headers': [u'user_id', u'email', u'first_name', u'last_name', u'phone_number', u'gender', u'approve',
                    u'reject'],
        'rows': []
    }

    for e in employee_info_update.objects.filter(status="NEW"):
        context['employee_info_update_request']['rows'].append([e.user_id, e.email,
                                                                e.first_name, e.last_name,
                                                                e.phone_number,
                                                                e.gender])
    return render(request, 'user_management/pendingEmployeeRequests.html', context)


@login_required
def technicalSupport(request):
    headers = [u"user_id", u"email", u"first_name", u"last_name", u"user_type"]

    users = [[getattr(user, header) for header in headers] for user in User.objects.exclude(user_id=request.user.user_id)
             if user.user_type in ["T1", "T2", "T3"]]

    req_headers = [u"id", u"for_id", u"requesting_id", u"status"]
    overrides = [[getattr(req, header) for header in req_headers] for req
                 in OverrideRequest.objects.exclude(status="DENIED") if req.requesting_id == request.user.user_id]

    context = {
        "users": {
            "headers": headers + ["Account Override"],
            "rows": users
        },
        "override": {
            "headers": req_headers + ["Action"],
            "rows": overrides
        }
    }

    if request.POST:
        requesting_id = request.user.user_id
        for_id = request.POST['user_id']
        if request.POST["action"] == "REQUEST_ACCESS":
            if OverrideRequest.objects.filter(requesting_id=requesting_id, for_id=for_id, status="NEW").count() > 0:
                return render(request, 'employee_request_already_exists.html')
            else:
                new_request = OverrideRequest(requesting_id=requesting_id, for_id=for_id)
                new_request.save()
        elif request.POST["action"] == "DELETE":
            print(requesting_id, for_id)
            OverrideRequest.objects.filter(requesting_id=requesting_id, for_id=for_id, status="NEW").delete()
        elif request.POST["action"] == "LOGIN":
            return render(request, "user_management/login.html")

    return render(request, 'user_management/technicalSupport.html', context)


def override_login(request):
    if request.POST:
        if request.POST["action"] == "SEND_OTP":
            otp = generate_otp()
            request.session['_overrideOTP'] = otp
            print(otp)
            # Uncomment this once the sns credentials are added in twofa.py file
            # send_otp(otp, request.user.phone_number)

            request_id = request.POST["request-id"]
            override = OverrideRequest.objects.get(pk=request_id)
            override_for = User.objects.get(pk=override.for_id).email
            override.status = "EXPIRED"
            override.save()

            context = {
                "otp_form": AccountOverrideLoginForm(),
                "override": {
                    "for_email": override_for
                }
            }
            return render(request, "user_management/overrideLogin.html", context)
        elif request.POST["action"] == "LOGIN":
            user_email = request.POST["overrideUser"]
            otp = request.POST["otp"]
            print("Overriding %s with OPT: %s" % (user_email, otp))
            if otp != request.session["_overrideOTP"]:
                context = {
                    "otp_form": AccountOverrideLoginForm(),
                    "override": {
                        "for_email": user_email
                    },
                    "error": "Invalid OTP"
                }
                return render(request, "user_management/overrideLogin.html", context)
            else:
                logout(request)
                user = User.objects.filter(email=user_email)[0]
                login(request, user)
                return redirect("/")


def override_request(request):
    override_requests_for_user = OverrideRequest.objects.filter(for_id=request.user.user_id, status="NEW")
    requesting_users = [{"name": "No Name", "id": req.requesting_id} for req in override_requests_for_user]
    for user in requesting_users:
        corresponding_user = User.objects.filter(user_id=user["id"])[0]
        user["name"] = corresponding_user.first_name + " " + corresponding_user.last_name

    context = {
        "override_requests": requesting_users
    }

    if request.POST:
        for_id = request.user.user_id
        requesting_id = request.POST['user_id']
        override = OverrideRequest.objects.filter(requesting_id=requesting_id, for_id=for_id, status="NEW")[0]

        if request.POST["action"] == "ACCEPTED":
            override.status = "ACCEPTED"
            override.save()
        elif request.POST["action"] == "DENIED":
            override.status = "DENIED"
            override.save()

    return render(request, "user_management/overrideRequests.html", context)
