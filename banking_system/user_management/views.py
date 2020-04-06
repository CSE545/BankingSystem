from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from user_management.forms import RegistrationForm, LoginForm, EditForm, AccountOverrideLoginForm
from user_management.models import User, employee_info_update, OverrideRequest, CustomerInfoUpdate, UserLog
from user_management.utility.twofa import generate_otp  # , send_otp


# Create your views here.


def login_view(request):
    if request.user.is_authenticated:
        create_user_log(user_id=request.user.user_id,
                        log_str="User Already Logged In", log_type="info")
        return redirect('home')
    context = {}
    if request.POST:
        email = request.POST['username']
        email = email.strip()
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        if user is not None:
            if user.is_active:
                form = LoginForm(request, data=request.POST)
                context['login_form'] = form
                is_valid_form = form.is_valid()
                if is_valid_form:
                    login(request, user)
                    create_user_log(user_id=user.user_id,
                                    log_str="Login Successful", log_type="info")
                    return redirect('home')
                else:
                    context['otp_sent'] = True
                    create_user_log(user_id=user.user_id,
                                    log_str="OTP Sent", log_type="info")
                    return render(request, 'user_management/login.html', context)
            else:
                context['inactive'] = True
                create_user_log(
                    user_id=user.user_id, log_str="Login Failed: User Inactive", log_type="debug")
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
            user = authenticate(email=email, password=raw_password)
            context['created'] = True
            create_user_log(user_id=user.user_id,
                            log_str="Register Successful", log_type="info")
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

            if request.user.user_type == 'CUSTOMER':
                num_results = CustomerInfoUpdate.objects.filter(
                    user_id=user_id, status='NEW').count()
                if num_results > 0:
                    create_user_log(
                        user_id=user_id, log_str="customer request already exists for edit profile", log_type="debug")
                    return render(request, 'customer_request_already_exists.html')

                new_entry = CustomerInfoUpdate(user_id=user_id, email=data.get('email'),
                                               first_name=data.get('first_name'),
                                               last_name=data.get('last_name'), phone_number=data.get('phone_number'),
                                               gender=data.get('gender'), status='NEW')
                new_entry.save()
                instance = form.save(commit=False)
                instance.created_by = request.user
                instance.save()
                context = {}
                context['request_received'] = True
                create_user_log(
                    user_id=user_id, log_str="customer request successfully created for edit profile", log_type="info")
                return render(request, 'customer_edit_request_submitted.html', context)
            # For employees
            num_results = employee_info_update.objects.filter(
                user_id=user_id, status='NEW').count()
            if num_results > 0:
                create_user_log(
                    user_id=user_id, log_str="employee request already exists for edit profile", log_type="debug")
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
            create_user_log(
                user_id=user_id, log_str="employee request created for edit profile", log_type="info")
            return render(request, 'employee_edit_request_submitted.html', context)
    else:
        context = {}
        form = EditForm(instance=request.user)
        context['edit_form'] = form
        create_user_log(user_id=request.user.user_id,
                        log_str="Profile Edit Failed: Non POST call", log_type="debug")
        return render(request, 'user_management/edit_profile.html', context)


# use this function only in POST calls. Writing in db is not recommended in GET calls.
def create_user_log(user_id, log_str, log_type):
    user_log = UserLog.objects.create(user_id=User.objects.get(
        user_id=user_id), log=log_str, log_type=log_type)
    user_log.save()

def t3_check(user):
    return user.user_type == "T3"

def t1_check(user):
    return user.user_type == "T1"

@login_required
@user_passes_test(t3_check)
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
            create_user_log(user_id=request.POST['user_id'],
                            log_str="Request Approved for edit by " + str(request.user.user_id),
                            log_type="info")

        return render(request, 'user_management/pendingEmployeeRequests.html')
    context = {}
    context['employee_info_update_request'] = {
        'headers': [u'User id', u'Email', u'First_name', u'Last_name', u'Phone number', u'Gender', u'Action'],
        'rows': []
    }

    for e in employee_info_update.objects.filter(status="NEW"):
        context['employee_info_update_request']['rows'].append([e.user_id, e.email,
                                                                e.first_name, e.last_name,
                                                                e.phone_number,
                                                                e.gender])
    return render(request, 'user_management/pendingEmployeeRequests.html', context)


@login_required
@user_passes_test(t1_check)
def show_pending_customer_requests(request):
    if request.POST:
        CustomerInfoUpdate.objects.filter(user_id=int(
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
            create_user_log(user_id=request.POST['user_id'],
                            log_str="Request Approved for edit by " +
                                    str(request.user.user_id),
                            log_type="info")

        return render(request, 'user_management/pendingCustomerRequests.html')

    context = {}
    context['customer_info_update_request'] = {
        'headers': [u'User id', u'Email', u'First name', u'Last name', u'Phone number', u'Gender', u'Action'],
        'rows': []
    }

    for e in CustomerInfoUpdate.objects.filter(status="NEW"):
        context['customer_info_update_request']['rows'].append([e.user_id, e.email,
                                                                e.first_name, e.last_name,
                                                                e.phone_number,
                                                                e.gender])
    return render(request, 'user_management/pendingCustomerRequests.html', context)


def userID_to_human_readable(userID):
    user = User.objects.get(pk=userID)
    return "%s, %s (%s)" % (user.last_name, user.first_name, user.email)


def generate_support_context(request, errors=""):
    headers = [u"user_id", u"email", u"first_name", u"last_name", u"user_type"]
    cleaned_headers = [u"User ID", u"Email",
                       u"First Name", u"Last Name", u"User Type"]

    users = [[getattr(user, header) for header in headers] for user in
             User.objects.exclude(user_id=request.user.user_id)
             if user.user_type in ["T1", "T2", "T3"]]

    req_headers = [u"id", u"for_id", u"requesting_id", u"status"]
    cleaned_req_headers = [u"Request ID",
                           u"Request For", u"Requesting Admin", u"Status"]
    overrides = [[getattr(req, header) for header in req_headers] for req
                 in OverrideRequest.objects.all() if req.requesting_id == request.user.user_id]

    for override in overrides:
        for_id_index = req_headers.index("for_id")
        req_id_index = req_headers.index("requesting_id")
        override[for_id_index] = userID_to_human_readable(
            override[for_id_index])
        override[req_id_index] = userID_to_human_readable(
            override[req_id_index])

    return {
        "users": {
            "headers": cleaned_headers + ["Account Override"],
            "rows": users
        },
        "override": {
            "headers": cleaned_req_headers + ["Action"],
            "rows": overrides,
        },
        "errors": errors
    }


@login_required
@user_passes_test(t3_check)
def technical_support(request):
    if request.POST:
        if request.POST["action"] == "REQUEST_ACCESS":
            requesting_id = request.user.user_id
            for_id = request.POST['user_id']
            if OverrideRequest.objects.filter(requesting_id=requesting_id, for_id=for_id, status="NEW").count() > 0:
                create_user_log(user_id=requesting_id,
                                log_str="Request for technical support for " +
                                        str(for_id) + " already exist",
                                log_type="debug")
                return render(request, 'user_management/technicalSupport.html',
                              generate_support_context(request, "REQUEST_EXISTS"))
            else:
                new_request = OverrideRequest(
                    requesting_id=requesting_id, for_id=for_id)
                new_request.save()
                create_user_log(user_id=requesting_id,
                                log_str="Request for technical support for " +
                                        str(for_id) + " added",
                                log_type="debug")
        elif request.POST["action"] == "DELETE":
            print(request.POST)
            OverrideRequest.objects.filter(
                id=request.POST["request-id"])[0].delete()
            create_user_log(user_id=request.POST["request-id"],
                            log_str="Request for technical support for deleted",
                            log_type="debug")

    return render(request, 'user_management/technicalSupport.html', generate_support_context(request))


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
            create_user_log(user_id=override.for_id,
                            log_str="Override Login: Send OTP action, OTP Created",
                            log_type="info")
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
                login(request, user,
                      backend="django.contrib.auth.backends.ModelBackend")
                create_user_log(user_id=user.user_id,
                                log_str="Override Login, Login Successful",
                                log_type="info")
                return redirect("/")


def override_request(request):
    override_requests_for_user = OverrideRequest.objects.filter(
        for_id=request.user.user_id, status="NEW")
    requesting_users = [{"name": "No Name", "id": req.requesting_id}
                        for req in override_requests_for_user]
    for user in requesting_users:
        corresponding_user = User.objects.filter(user_id=user["id"])[0]
        user["name"] = corresponding_user.first_name + " " + corresponding_user.last_name

    context = {
        "override_requests": requesting_users
    }

    if request.POST:
        for_id = request.user.user_id
        requesting_id = request.POST['user_id']
        override = OverrideRequest.objects.filter(
            requesting_id=requesting_id, for_id=for_id, status="NEW")[0]

        if request.POST["action"] == "ACCEPTED":
            override.status = "ACCEPTED"
            override.save()
            create_user_log(user_id=requesting_id,
                            log_str="Override Request accepted for " +
                                    str(for_id),
                            log_type="info")
        elif request.POST["action"] == "DENIED":
            override.status = "DENIED"
            override.save()
            create_user_log(user_id=requesting_id,
                            log_str="Override Request denied for " +
                                    str(for_id),
                            log_type="debug")

    return render(request, "user_management/overrideRequests.html", context)
