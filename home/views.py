from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from home.forms import CourseForm
from home.models import Course


class AllCourses(ListView):
    model = Course
    queryset = Course.objects.all()
    context_object_name = 'courses'
    paginate_by = 5


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

