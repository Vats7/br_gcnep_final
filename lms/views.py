import json
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from lms.models import Training, Enrollment
import boto3
from django.contrib.auth.decorators import user_passes_test

from users.models import UserType
from .forms import EnrollmentForm, BulkAddAttendeeForm, TrainingForm
User = get_user_model()

client = boto3.client(
    'chime-sdk-meetings',
    aws_access_key_id=settings.AWS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name='us-east-1'
)


@login_required
def index(request):
    trainer = UserType.objects.get(type='TRAINER')
    trainee = UserType.objects.get(type='TRAINEE')
    observer = UserType.objects.get(type='OBSERVER')
    if request.user.is_superuser:
        context = {
            'total_users': User.objects.all().count(),
            'total_moderators': User.objects.filter(is_mod=True).count(),
            'total_trainers': User.objects.filter(types__in=[trainer]).count(),
            'total_trainees': User.objects.filter(types__in=[trainee]).count(),
            'total_observers': User.objects.filter(types__in=[observer]).count(),
            'total_trainings': Training.objects.all().count()
        }
        return render(request, 'lms/admin_index.html', context=context)
    elif request.user.is_mod:
        context = {
            'total_trainers': User.objects.filter(types__in=[trainer]).count(),
            'total_trainees': User.objects.filter(types__in=[trainee]).count(),
            'total_observers': User.objects.filter(types__in=[observer]).count(),
            'total_trainings': Training.objects.filter(created_by=request.user).count()
        }
        return render(request, 'lms/mod_index.html', context)
    else:
        context = {
            'my_trainings': request.user.training_set.all().count(),

        }
        return render(request, 'lms/user_index.html', context)


@user_passes_test(lambda u: u.is_superuser)
def all_trainings(request):
    return render(request, 'lms/all_trainings.html')


@user_passes_test(lambda u: u.is_superuser)
def all_trainings_list(request):
    trainings = Training.objects.all()
    paginator = Paginator(trainings, 5)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'trainings': trainings,
        'page_obj': page_obj,
    }
    return render(request, 'lms/includes/all_trainings_list.html', context=context)


def htmx_paginate_all_trainings(request):
    trainings = Training.objects.all()
    paginator = Paginator(trainings, 5)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'trainings': trainings,
        'page_obj': page_obj,
    }
    return render(request, 'lms/includes/all_trainings_loop.html', context)

# @method_decorator(staff_member_required, name='dispatch')
# class AllTrainingsList(ListView):
#     model = Training
#     template_name = 'lms/includes/all_trainings_list.html'
#     context_object_name = 'trainings'
#     paginate_by = 5
#     queryset = Training.objects.all()


def my_trainings(request):
    if request.user.is_staff:
        return render(request, 'lms/training_list_staff.html')
    return render(request, 'lms/training_list_user.html')


def my_trainings_list(request):
    trainings = request.user.training_set.all()
    paginator = Paginator(trainings, 5)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'trainings': trainings,
        'page_obj': page_obj
    }
    if request.htmx:
        if request.user.is_staff:
            return render(request, 'lms/includes/my_training_list_staff.html', context)
        return render(request, 'lms/includes/my_training_list_user.html',context)
    else:
        if request.user.is_staff:
            return render(request, 'lms/training_list_staff.html')
        return render(request, 'lms/training_list_user.html')


def htmx_paginate_my_trainings(request):
    trainings = request.user.training_set.all()
    paginator = Paginator(trainings, 5)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'trainings': trainings,
        'page_obj': page_obj
    }
    if request.user.is_staff:
        return render(request, 'lms/includes/my_trainings_staff_loop.html', context=context)
    return render(request, 'lms/includes/my_trainings_user_loop.html', context=context)



# def my_trainings_list(request):
#     trainings = request.user.training_set.all()
#     if request.user.is_staff:
#         return render(request, 'lms/includes/my_training_list_staff.html', {
#             'trainings': trainings,
#         })
#     return render(request, 'lms/includes/my_training_list_user.html', {
#         'trainings': trainings,
#     })


def training_detail(request, pk):
    training = get_object_or_404(Training, pk=pk)
    enrollments = Enrollment.objects.filter(training=training).exclude(permission='ADMIN')
    print(enrollments)
    context = {
        'training': training,
        'enrollments': enrollments,
    }
    return render(request, 'lms/training_detail.html', context=context)


@login_required
def join_meeting(request, pk):
    training = get_object_or_404(Training, pk=pk)
    return render(request, 'lms/chime.html', {'training': training})


def get_meeting(request, pk):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'GET':
            meeting = Training.objects.get(pk=pk)
            response = client.get_meeting(
                MeetingId=meeting.chime_id
            )
            print('FROM VIEW ----MEETING')
            print(response)
            return JsonResponse(response['Meeting'])
        return JsonResponse({'status': 'Invalid request bcoz only GET is allowed '}, status=400)
    return HttpResponseBadRequest('Invalid request (only ajax allowed)')


def get_attendee(request, pk):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'GET':
            meeting = Training.objects.get(pk=pk)
            enroll = Enrollment.objects.get(training=meeting, user=request.user)
            response = client.get_attendee(
                MeetingId=meeting.chime_id,
                AttendeeId=enroll.attendee_id
            )
            print('FROM VIEW ----ATTENDEE')
            print(response)
            return JsonResponse(response['Attendee'])
        return JsonResponse({'status': 'Invalid request bcoz only GET is allowed '}, status=400)
    return HttpResponseBadRequest('Invalid request (only ajax allowed)')


@staff_member_required
def start_meeting(request, pk):
    training = get_object_or_404(Training, pk=pk)
    attendees_ids = [u.unique_id for u in training.attendees.all()]
    attendees = []
    for i in attendees_ids:
        attendees.append({
            'ExternalUserId': str(i)
        })
    print('FINAL ATTENDEES for API CALL')
    print(len(attendees))
    print(attendees)
    res = client.create_meeting_with_attendees(
        MediaRegion='ap-south-1',
        ExternalMeetingId=str(training.unique_id),
        MeetingFeatures={
            'Audio': {
                'EchoReduction': 'AVAILABLE'
            }
        },
        Attendees=attendees
    )
    print('RESPONSE FROM CHIME')
    print(res['Meeting'])
    print(res['Attendees'])
    training.chime_id = res['Meeting']['MeetingId']
    training.save()

    id_list = [i['ExternalUserId'] for i in res['Attendees']]
    print('EXTERUSERID LIST from chime')
    print(id_list)

    info_list = [{k: v for k, v in d.items() if k != 'ExternalUserId'} for d in res['Attendees']]
    print('ExtraINFO LIST from chime')
    print(info_list)

    req_dict = dict(zip(id_list, info_list))
    print('FINAL DICT')
    print(req_dict)

    with transaction.atomic():
        for key, value in req_dict.items():
            Enrollment.objects.filter(user__unique_id=key).update(join_token=value['JoinToken'],
                                                                  attendee_id=value['AttendeeId'])

    return redirect('lms:my_trainings')


@staff_member_required
def create_training(request):
    if request.method == 'POST':
        form = TrainingForm(request.POST, request.FILES or None)
        if form.is_valid():
            new_training = form.save(commit=False)
            new_training.created_by = request.user
            new_training.save()
            form.save_m2m()
            messages.success(request, 'Training Created')
            return redirect('lms:my_trainings_list')
    else:
        form = TrainingForm()
    return render(request, 'lms/create_training.html', {'form': form})


@staff_member_required
def update_training(request, pk):
    training = get_object_or_404(Training, pk=pk)
    if request.method == 'POST':
        form = TrainingForm(request.POST, request.FILES, instance=training)
        if form.is_valid():
            form.save()
            return redirect('lms:my_trainings_list')
    else:
        form = TrainingForm(instance=training)
    return render(request, 'lms/update_training.html', {'form': form, 'training': training})


@staff_member_required
@require_http_methods(['DELETE'])
def delete_training(request, pk):
    training = get_object_or_404(Training, pk=pk)
    training.delete()
    return HttpResponse(
        status=204, headers={
            'HX-Trigger': json.dumps({
                "trainingListChanged": None,
                "showMessage": f"training deleted"
            })
        })


@staff_member_required
def create_enrollment(request, pk):
    training = get_object_or_404(Training, pk=pk)
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            if Enrollment.objects.filter(training=training, user=user).exists():
                messages.add_message(request, messages.ERROR, 'User already enrolled')
                return redirect('lms:create_enrollment', pk=pk)
            enroll = form.save(commit=False)
            enroll.training = training
            enroll.created_by = request.user
            enroll.save()
            messages.add_message(request, messages.SUCCESS, 'SUCCESS')
            return redirect('lms:my_trainings_list')
    else:
        form = EnrollmentForm()
    return render(request, 'lms/enrollment_create_form.html', {
        'form': form,
        'training': training,
    })


@staff_member_required
def bulk_add_attendee(request, pk):
    training = get_object_or_404(Training, pk=pk)
    if request.method == 'POST':
        form = BulkAddAttendeeForm(request.POST)
        if form.is_valid():
            permission = form.cleaned_data['permission']
            users = form.cleaned_data['users']
            for u in users:
                if Enrollment.objects.filter(training=training, user=u).exists():
                    messages.add_message(request, messages.ERROR, 'One or More Users already enrolled')
                    return redirect('lms:bulk_add_attendee', pk=pk)
                else:
                    Enrollment.objects.create(training=training, user=u, permission=permission, created_by=request.user)
            # messages.add_message(request, messages.SUCCESS, 'SUCCESS')
            return redirect('lms:my_trainings_list')
    else:
        form = BulkAddAttendeeForm()
    return render(request, 'lms/bulk_attendee.html', {
        'form': form,
        'training': training,
    })


def all_trainings_search(request):
    if request.method == 'GET':
        url_parameter = request.GET.get("query")
        trainings = Training.objects.filter(title__icontains=url_parameter, description__icontains=url_parameter)
        context = {
            'trainings': trainings
        }
        return render(request, 'lms/includes/all_trainings_list.html', context=context)


def my_trainings_search(request):
    if request.method == 'GET':
        url_parameter = request.GET.get("query")
        trainings = request.user.training_set.all().\
            filter(title__icontains=url_parameter, description__icontains=url_parameter)

        context = {
            'trainings': trainings
        }
        if request.user.is_staff:
            return render(request, 'lms/includes/search_results_staff.html', context=context)
        else:
            return render(request, 'lms/includes/search_results_user.html', context=context)
    return HttpResponseBadRequest('Invalid request (only GET allowed)')

