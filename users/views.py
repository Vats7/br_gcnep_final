import json
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from users.forms import LoginForm, SignUpForm, UserProfileForm, \
    UserChangeFormNew, UserCreationFormNew, ModProfileForm, DocumentForm
from django.views.decorators.cache import cache_control
from django.db.models.query_utils import Q
from users.models import Document, UserProfile
User = get_user_model()


def register_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            u_types = form.cleaned_data['types']
            user.types.add(*u_types)
            user.save()
            print(user)
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("lms:home")
        messages.error(request, form.errors)
    else:
        form = SignUpForm()
    return render(request=request, template_name="users/register.html", context={"form": form})


@cache_control(no_cache=True, must_revalidate=True)
def login_view(request):
    if request.method == "POST":
        # trainer = UserType.objects.get(type='TRAINER')
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            if user is not None:
                # if not user.is_staff:
                login(request, user)
                messages.success(request, f'Successfully logged in as {user.email}')
                return redirect('lms:home')
            else:
                messages.error(request, "Not Registered")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request=request, template_name="users/login_new.html", context={"login_form": form,})


@cache_control(no_cache=True, must_revalidate=True)
def logout_view(request):
    logout(request)
    #messages.info(request, "You have successfully logged out.")
    return redirect("users:login")


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "users/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@example.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
                    return redirect("users:login")
            messages.error(request, 'An invalid email has been entered.')
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="users/password_reset.html",
                  context={"password_reset_form": password_reset_form})


@user_passes_test(lambda u: not u.is_superuser)
def my_profile_view(request):
    if request.method == 'POST':
        if request.user.is_mod:
            profile = request.user.mod_profile
            profile_form = ModProfileForm(request.POST, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                return redirect('users:my_profile')
            return render(request, 'users/profile.html', {'profile_form': profile_form})
        else:
            profile = request.user.profile
            profile_form = UserProfileForm(request.POST, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                return redirect('users:my_profile')
            return render(request, 'users/profile.html', {'profile_form': profile_form})
    else:
        if request.user.is_mod:
            profile = request.user.mod_profile
            profile_form = ModProfileForm(instance=profile)
            context = {
                'profile_form': profile_form
            }
        else:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            # profile = request.user.profile
            if created:
                profile_form = UserProfileForm(instance=request.user.profile)
            else:
                profile_form = UserProfileForm(instance=profile)
            doc_form = DocumentForm()
            context = {
                'profile_form': profile_form,
                'doc_form': doc_form
            }
    return render(request, 'users/profile.html', context=context)


@method_decorator(staff_member_required, name='dispatch')
class UserList(ListView):
    model = User
    template_name = 'users/all_users.html'
    context_object_name = 'users'
    paginate_by = 5
    permission_classes = []

    # def get_template_names(self):
    #     if self.request.htmx:
    #         return 'users/includes/user_list.html'
    #     return 'users/all_users.html'

    def get_queryset(self):
        queryset = User.objects.all()
        if self.request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(is_staff=False)


@staff_member_required
def all_users_list(request):
    if request.user.is_superuser:
        users = User.objects.all()
    else:
        users = User.objects.filter(is_staff=False)

    paginator = Paginator(users, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'users': users,
        'page_obj': page_obj,
    }
    return render(request, 'users/includes/user_list.html', context)


def htmx_paginate_users(request):
    users = User.objects.all()
    paginator = Paginator(users, 5)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'users': users,
        'page_obj': page_obj,
    }
    return render(request, 'users/includes/user_list_loop.html', context=context)


def user_search(request):
    if request.method == 'GET':
        url_parameter = request.GET.get("query")
        if request.user.is_superuser:
            users = User.objects.filter(
                Q(name__icontains=url_parameter) | Q(email__icontains=url_parameter))

            context ={
                'users': users,
            }
            return render(request, 'users/includes/search_results.html', context=context)
        else:
            users = User.objects.filter(
                Q(name__icontains=url_parameter) | Q(email__icontains=url_parameter, is_staff=False))
            context = {
                'users': users,
            }
            return render(request, 'users/includes/search_results.html', context=context)


@staff_member_required
def create_user(request):
    if request.method == 'POST':
        form = UserCreationFormNew(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:all_users')
    else:
        form = UserCreationFormNew()
    return render(request, 'users/create_user.html', {'form': form})


@staff_member_required
@require_http_methods(['DELETE'])
def delete_user(request, id):
    user = get_object_or_404(User, pk=id)
    user.delete()
    return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "userListChanged": None,
                "showMessage": f"{user.name} deleted."
            })
        })


@staff_member_required
def update_user(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        form = UserChangeFormNew(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users:all_users')
    else:
        form = UserChangeFormNew(instance=user)
    return render(request, 'users/update_user.html', {'form': form, 'user': user})


@user_passes_test(lambda u: not u.is_staff)
def upload_documents(request):
    if request.method == "POST":
        doc_form = DocumentForm(request.POST, request.FILES)
        if doc_form.is_valid():
            print('yes')
            files = request.FILES.getlist('file')
            print(files)
            for f in files:
                Document.objects.create(
                    user=request.user.profile,
                    created_by=request.user,
                    type=doc_form.cleaned_data['type'],
                    file=f
                )
            print('yes-again')
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "docsListChanged": None,
                    "showMessage": 'documents added'

                })
            })
    else:
        doc_form = DocumentForm()
    return render(request, 'users/document_form.html', {
        'doc_form': doc_form,
    })


def get_my_documents(request):
    profile = request.user.profile
    documents = profile.documents.all()
    paginator = Paginator(documents, 10)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'user': request.user,
        'documents': documents,
        'page_obj': page_obj
    }
    if request.htmx:
        return render(request, 'users/includes/my_documents_list.html', context)
    return render(request, 'users/my_documents.html', context)


def htmx_paginate_my_docs(request):
    profile = request.user.profile
    documents = profile.documents.all()
    paginator = Paginator(documents, 10)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'documents': documents,
        'page_obj': page_obj,
    }
    return render(request, 'users/includes/my_documents_loop.html', context=context)


def search_my_documents(request):
    if request.method == 'GET':
        url_parameter = request.GET.get("query")
        documents = request.user.profile.documents.all().filter(type__in=[url_parameter,])
        # documents = Document.objects.filter(
        #     Q(type__in=[url_parameter]) #| Q(__icontains=url_parameter)
        # )
        context = {
            'documents': documents
        }
        print(documents)
        return render(request, 'users/includes/my_documents_list.html', context=context)


@staff_member_required
def staff_get_user_documents(request, id):
    user = User.objects.get(pk=id)
    documents = user.profile.documents.all()
    paginator = Paginator(documents, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'user': user,
        'documents': documents,
        'page_obj': page_obj
    }
    if request.htmx:
        return render(request, 'users/includes/user_documents_list.html', context)
    return render(request, 'users/user_documents.html', context)


def htmx_paginate_user_docs(request, id):
    user = User.objects.get(pk=id)
    documents = user.profile.documents.all()
    paginator = Paginator(documents, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'user': user,
        'documents': documents,
        'page_obj': page_obj
    }
    return render(request, 'users/includes/user_documents_loop.html', context=context)


@staff_member_required
def user_profile_view(request, id):
    user = User.objects.get(pk=id)
    if request.method == 'POST':
        if user.is_mod:
            profile = user.mod_profile
            form = ModProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                return redirect('users:all_users_list')
            return render(request, 'users/user_profile.html', {'form': form})
        else:
            profile = user.profile
            form = UserProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                return redirect('users:all_users_list')
            return render(request, 'users/user_profile.html', {'form': form})
    else:
        if user.is_mod:
            profile = user.mod_profile
            form = ModProfileForm(instance=profile)
            context = {
                'form': form
            }
        else:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            if created:
                form = UserProfileForm(instance=user.profile)
            else:
                form = UserProfileForm(instance=profile)
            context = {
                'form': form,
                'user': user,
            }
    return render(request, 'users/user_profile.html', context)


@staff_member_required
def all_documents(request):
    users = User.objects.filter(is_staff=False)
    documents = Document.objects.all()
    paginator = Paginator(documents, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'users': users,
        'documents': documents,
        'page_obj': page_obj,
    }
    if request.htmx:
        return render(request, 'users/includes/all_documents_list.html', context)
    return render(request, 'users/all_documents.html', context)


def htmx_paginate_all_docs(request):
    documents = Document.objects.all()
    paginator = Paginator(documents, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'documents': documents,
        'page_obj': page_obj
    }
    return render(request, 'users/includes/all_documents_loop.html', context)
