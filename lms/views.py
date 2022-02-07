from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView
from lms.models import Training, Enrollment
from users.models import CustomUser


@login_required
def index(request):
    return render(request, 'lms/index.html')


# @staff_member_required
# def create_meeting(request):
#     if request.method == "POST":
#         form = TrainingForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect("lms:home")
#         messages.error(request, form.errors)
#     form = TrainingForm()
#     return render(request=request, template_name="lms/create_meeting.html", context={"form": form})


class TrainingList(ListView):
    context_object_name = 'trainings'
    model = Training
    paginate_by = 5

    def get_queryset(self):
        queryset = Training.objects.all()
        staff = self.request.user.is_staff
        admin = self.request.user.is_superuser
        if admin:
            return queryset
        if staff and not admin:
            return queryset.filter(created_by=self.request.user)
        else:
            user = self.request.user
            qs = user.profile.training_set.all()
            return qs


@login_required
def meeting_detail(request, pk):
    u = request.user
    t = get_object_or_404(Training, pk=pk)
    if not u.is_staff:
        if u in t.attendees.all():
            return JsonResponse({
                'user': u.name,
                'training': t.title,
            })
        return JsonResponse({'error': 'Not an Attendee'})
    return JsonResponse({
        'user': u.name,
        'training': t.title,
    })




@login_required
def join_meeting(request, pk):
    user = request.user
    training = Training.objects.get(pk=pk)
    e = get_object_or_404(Enrollment, user=user.profile, training=training)
    res = {
        'meeting_id': training.unique_id,
        'user_id': user.id,
        'user_unique_token': e.user_unique_id,
        'status': e.training_status,
        'start_at': e.start_at,
        'end_at': e.end_at,
        'joined_at': e.joined_at,
        'perm': e.permission,
    }

    return JsonResponse(res)


# def all_attendees(request, pk):
#     training = Training.objects.get(pk=pk)
#     attendees = training.attendees.all()
#
#     res = {
#         'meeting_id': training.unique_id,
#         'user_id': user.id,
#         'user_unique_token': user.id,
#         'attendee_id': attendee_id,
#         'perm': perm,
#     }





@login_required
def redirect_meeting(request, pk):
    base_url = reverse('lms:chime')
    training = get_object_or_404(Training, pk=pk)
    #e = get_object_or_404(Enrollment, user=request.user.profile, training=training)

    query_string = urlencode(
        {
            'user_id': request.user.id,
            'user_name': request.user.name,
            'meet_id': training.unique_id,
        }
    )
    url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
    return redirect(url)


def chime(request):
    return render(request, 'lms/chime.html')

