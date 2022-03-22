from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.views.generic import ListView

from users.forms import LoginForm, SignUpForm, UserProfileForm, UserChangeFormNew, UserCreationFormNew
from django.views.decorators.cache import cache_control
from django.db.models.query_utils import Q

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
                messages.error(request, "Already exists")
        else:
            messages.error(request, "Invalid email or password.")
    form = LoginForm()
    return render(request=request, template_name="users/login_new.html", context={"login_form": form})


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


def profile_view(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile Updated")
            return redirect("lms:home")
        messages.error(request, form.errors)
    form = UserProfileForm()
    return render(request=request, template_name="users/profile.html", context={"form": form})

# def my_profile(request, id):
#     user = User.objects.get(pk=unique_id)


@method_decorator(staff_member_required, name='dispatch')
class UserList(ListView):
    model = User
    template_name = 'users/all_users.html'
    context_object_name = 'users'
    paginate_by = 5
    permission_classes = []

    def get_queryset(self):
        queryset = User.objects.all()
        if self.request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(is_staff=False)


def user_search(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'GET':
            url_parameter = request.GET.get("q")
            if request.user.is_superuser:
                users = User.objects.filter(name__icontains=url_parameter, email__icontains=url_parameter)
                html = render_to_string(
                    template_name="users/includes/user_list.html",
                    context={"users": users}
                )
                data_dict = {"html_from_view": html}
                return JsonResponse(data=data_dict, safe=False)
            else:
                users = User.objects.filter(name__icontains=url_parameter, email__icontains=url_parameter, is_staff=False)
                html = render_to_string(
                    template_name="users/includes/user_list.html",
                    context={"users": users}
                )
                data_dict = {"html_from_view": html}
                return JsonResponse(data=data_dict, safe=False)


def create_user(request):
    if request.method == 'POST':
        form = UserCreationFormNew(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:user_list')
    else:
        form = UserCreationFormNew()
    return render(request, 'users/create_user.html', {'form': form,})


def update_user(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        form = UserChangeFormNew(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users:user_list')
    else:
        form = UserChangeFormNew(instance=user)
    return render(request, 'users/update_user.html', {'form': form, 'user': user})
