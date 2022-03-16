from urllib.parse import urlencode
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView
from lms.models import Training, Enrollment
import boto3
from django.contrib.auth.decorators import user_passes_test
from . forms import EnrollmentForm, TrainingForm, BulkAddAttendeeForm, TestForm


client = boto3.client(
    'chime-sdk-meetings',
    aws_access_key_id=settings.AWS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name='us-east-1'
)


@login_required
def index(request):
    return render(request, 'lms/index.html',)


@user_passes_test(lambda u: u.is_superuser)
#@staff_member_required
def all_trainings(request):
    trainings = Training.objects.all()
    context = {
        'trainings': trainings
    }
    return render(request, 'lms/all_trainings.html', context=context)


def my_training_list(request):
    trainings = request.user.training_set.all()
    if request.user.is_staff:
        return render(request, 'lms/training_list_staff.html', {
            'trainings': trainings,
        })
    return render(request, 'lms/training_list_user.html', {
        'trainings': trainings,
    })

# class MyTrainingList(ListView):
#     context_object_name = 'trainings'
#     model = Training
#     paginate_by = 5
#
#     def get_queryset(self):
#         return self.request.user.training_set.all()
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in a QuerySet of all the books
#         context['enroll_form'] = EnrollmentForm()
#         return context


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
def join_meeting(request,pk):
    return render(request, 'lms/chime.html')


@login_required
def redirect_meeting(request, pk):
    base_url = reverse('lms:chime')
    training = get_object_or_404(Training, pk=pk)
    # e = get_object_or_404(Enrollment, user=request.user.profile, training=training)

    query_string = urlencode(
        {
            'user_id': request.user.id,
            'user_name': request.user.name,
            'meet_id': training.unique_id,
        }
    )
    url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
    return redirect(url)


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
        form = TestForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            course = form.cleaned_data['course']
            training_type = form.cleaned_data['training_type']
            quizzes = form.cleaned_data['quiz']
            assignments = form.cleaned_data['assignment']
            main_image = form.cleaned_data['main_image']
            start_at = form.cleaned_data['start_at']
            end_at = form.cleaned_data['end_at']

            training = Training.objects.create(
                title=title,
                description=description,
                course=course,
                training_type=training_type,
                main_image=main_image,
                start_at=start_at,
                end_at=end_at,
                created_by=request.user,
            )

            training.quiz.add(*quizzes)
            training.assignment.add(*assignments)
            return redirect('lms:my_trainings')
        else:
            print(form.errors)
            return render(request, 'lms/create_training.html', {'form': form})
    else:
        form = TestForm()
    return render(request, 'lms/create_training.html', {'form': form})


@staff_member_required
def update_training(request, pk):
    training = get_object_or_404(Training, pk=pk)
    if request.method == 'POST':
        form = TestForm(request.POST, request.FILES, inital=training)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            course = form.cleaned_data['course']
            training_type = form.cleaned_data['training_type']
            quizzes = form.cleaned_data['quiz']
            assignments = form.cleaned_data['assignment']
            main_image = form.cleaned_data['main_image']
            start_at = form.cleaned_data['start_at']
            end_at = form.cleaned_data['end_at']

            training = Training.objects.create(
                title=title,
                description=description,
                course=course,
                training_type=training_type,
                main_image=main_image,
                start_at=start_at,
                end_at=end_at,
                created_by=request.user,
            )

            training.quiz.add(*quizzes)
            training.assignment.add(*assignments)
            return redirect('lms:my_trainings')
        else:
            print(form.errors)
            return render(request, 'lms/create_training.html', {'form': form})
    else:
        form = TestForm()
    return render(request, 'lms/create_training.html', {'form': form})


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
            return redirect('lms:my_trainings')
    else:
        form = EnrollmentForm()
    return render(request, 'lms/enrollment_create_form.html', {
        'form': form,
        'training': training,
    })


# @staff_member_required
# def create_enrollment(request):
#     is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
#
#     if is_ajax:
#         if request.method == 'POST':
#             form = EnrollmentForm(request.POST)
#             if form.is_valid():
#                 form.save()
#                 return JsonResponse({'success': 'successfully enrolled'})
#             return JsonResponse({'errors': form.errors}, status=400)
#         return JsonResponse({'status': 'Invalid request bcoz only post is allowed '}, status=400)
#     return HttpResponseBadRequest('Invalid request (only ajax allowed)')


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
            return redirect('lms:my_trainings')
    else:
        form = BulkAddAttendeeForm()
    return render(request, 'lms/bulk_attendee.html', {
        'form': form,
        'training': training,
    })


def all_trainings_search(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'GET':
            url_parameter = request.GET.get("q")
            trainings = Training.objects.filter(title__icontains=url_parameter, description__icontains=url_parameter)
            html = render_to_string(
                template_name="lms/includes/all_trainings_list.html",
                context={"trainings": trainings}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)


def my_trainings_search_staff(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'GET':
            url_parameter = request.GET.get("q")
            trainings = request.user.training_set.all().\
                filter(title__icontains=url_parameter, description__icontains=url_parameter)

            if request.user.is_staff:
                html = render_to_string(
                    template_name="lms/includes/my_training_list_staff.html",
                    context={"trainings": trainings}
                )
            else:
                html = render_to_string(
                    template_name="lms/includes/my_training_list_user.html",
                    context={"trainings": trainings}
                )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)










# def delete_training(request, pk):
#     training = get_object_or_404(Training, pk=pk)
#




# class EnrollmentCreateView(CreateView):
#     model = Enrollment
