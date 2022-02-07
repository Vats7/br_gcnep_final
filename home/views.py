from django.views.generic import ListView, DetailView

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
