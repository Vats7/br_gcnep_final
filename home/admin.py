from django.contrib import admin
from .models import School, Department, Course


class BaseAdmin(admin.ModelAdmin):
    readonly_fields = ('unique_id', 'created_by', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(School)
class SchoolAdmin(BaseAdmin):
    pass


@admin.register(Department)
class DepartmentAdmin(BaseAdmin):
    pass


@admin.register(Course)
class CourseAdmin(BaseAdmin):
    list_display = ('title', 'school')
