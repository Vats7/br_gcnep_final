from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from home.forms import CourseForm
from home.models import Course


@method_decorator(staff_member_required, name='dispatch')
class AllCourses(ListView):
    model = Course
    queryset = Course.objects.all()
    context_object_name = 'courses'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['form'] = CourseForm()
        return context


# @method_decorator(user_passes_test(lambda u: not u.is_staff))
@user_passes_test(lambda u: not u.is_staff)
def my_courses(request):
    courses = set()
    for e in request.user.training_set.all().select_related('course'):
        courses.add(e.course)
    # trainings = request.user.training_set.all().select_related('course')
    # courses = [t.course.all() for t in trainings]
    return render(request, 'home/my_courses.html', {'courses': courses})


class CourseDetail(DetailView):
    model = Course
    queryset = Course.objects.all()
    context_object_name = 'course'


def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.created_by = request.user
            course.save()
            return redirect('home:all_courses')
    else:
        form = CourseForm()
    return render(request, 'home/create_course.html', {'form': form})


def all_courses_search(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'GET':
            url_parameter = request.GET.get("q")
            courses = Course.objects.filter(title__icontains=url_parameter)
            html = render_to_string(
                template_name="home/includes/course_list.html",
                context={"courses": courses}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)





