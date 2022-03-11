from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.utils.translation import ngettext

# from lms.admin import EnrollmentInline
from .forms import UserAdminCreationForm, UserChangeForm
from .models import CustomUser, UserProfile, ModeratorProfile, UserType, Document, Education, Employment


class DocumentInlineAdmin(admin.StackedInline):
    model = Document
    extra = 0
    readonly_fields = ('sig_tag', 'pass_1_tag', 'pass_2_tag', 'unique_id', 'created_by', 'created_at', 'updated_at')
    classes = ['collapse']

    @admin.display(description='Signature')
    def sig_tag(self, obj):
        return format_html('<img src="{0}" style="width: 100px; height:100px;" />'.format(obj.sig_1.url))

    @admin.display(description='Passport Front')
    def pass_1_tag(self, obj):
        return format_html('<img src="{0}" style="width: 100px; height:100px;" />'.format(obj.pass_1.url))

    @admin.display(description='Passport Back')
    def pass_2_tag(self, obj):
        return format_html('<img src="{0}" style="width: 100px; height:100px;" />'.format(obj.pass_2.url))


class EducationInlineAdmin(admin.StackedInline):
    model = Education
    extra = 0
    readonly_fields = ('unique_id', 'created_by', 'created_at', 'updated_at')
    classes = ['collapse']


class EmploymentInlineAdmin(admin.StackedInline):
    model = Employment
    extra = 0
    readonly_fields = ('unique_id', 'created_by', 'created_at', 'updated_at')
    classes = ['collapse']


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    add_form = UserAdminCreationForm
    change_form = UserChangeForm
    model = CustomUser
    list_display = ('id', 'unique_id', 'email', 'name', 'is_active', 'get_types')
    list_filter = ('is_active', 'types')
    fieldsets = (
        (None, {'fields': ('email', 'name', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_mod', 'is_superuser', 'types', 'date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_active', 'is_mod', 'is_superuser',)}),#'types'
    )
    search_fields = ('email', 'name')
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login',)#'types'
    filter_horizontal = ('types',)
    inlines = []
    actions = ['activate_users', 'assign_trainees']

    @admin.display(description='Types')
    def get_types(self, obj):
        return [t for t in obj.types.all()]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(is_staff=False)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "types":
            types = ['TRAINER', 'TRAINEE', 'OBSERVER']
            kwargs["queryset"] = UserType.objects.filter(type__in=types)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # def get_readonly_fields(self, request, obj=None):
    #     if obj is not None and obj.is_staff:
    #         return self.readonly_fields + ('types',)
    #     return self.readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        if obj is not None and is_superuser:
            disabled_fields |= {
                'is_mod',
                'is_superuser',
            }
        if obj is not None and obj.is_staff:
            disabled_fields |= {
                'types',
            }

        if not is_superuser:
            disabled_fields |= {
                'is_mod',
                'is_superuser',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form


@admin.register(ModeratorProfile)
class ModeratorProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)
    list_display = ('user', 'get_name', 'designation', 'unit')

    @admin.display(description='Name')
    def get_name(self, obj):
        return obj.user.name

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_filter = ('user__types',)
    search_fields = ['user__name']
    readonly_fields = ('image_tag', )
    list_display = ('user', 'get_name',)
    autocomplete_fields = ['user']

    fieldsets = (
        (None, {
            'fields': (('image', 'image_tag'), 'school', ('first_name', 'last_name'))
        }),
        (None, {
            'fields': (('gender', 'dob', 'pob'),)
        }),
        ('Other options', {
            'classes': ('collapse',),
            'fields': (('org_ins', 'dept_name', 'dept_id',), ),
        }),
        ('Contact options', {
            'classes': ('collapse',),
            'fields': (('ofc_add', 'ofc_number',), ('nationality', 'fax', 'secondary_email')),
         }),
    )
    inlines = [DocumentInlineAdmin, EducationInlineAdmin, EmploymentInlineAdmin]#EnrollmentInline

    @admin.display(description='Name')
    def get_name(self, obj):
        return obj.user.name

    @admin.display(description='AVATAR')
    def image_tag(self, obj):
        return format_html('<img src="{0}" style="width: 100px; height:100px;" />'.format(obj.image.url))

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False

    # def save_formset(self, request, form, formset, change):
    #     instances = formset.save(commit=False)
    #     for instance in instances:
    #         instance.created_by = request.user
    #         instance.save()
    #     formset.save_m2m()


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    # def has_add_permission(self, request):
    #     return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # MAX_OBJECTS = 1
    #
    # def has_add_permission(self, request):
    #     if self.model.objects.count() >= MAX_OBJECTS:
    #         return False
    #     return super().has_add_permission(request)


admin.site.unregister(Group)

######
#
#
# @admin.action(description='Mark selected stories as published')
#     def make_published(self, request, queryset):
#         queryset.update(status='p')
#
#     @admin.action(description='Activate Users')
#     def activate_users(self, request, queryset):
#         #assert request.user.has_perm('auth.change_user')
#         cnt = queryset.filter(is_active=False).update(is_active=True)
#         self.message_user(request, 'Activated {} users.'.format(cnt))
#
#     # @admin.action(description='Assign Trainees')
#     # def assign_trainees(self, request, queryset):
#     #     can_assign_as_trainee = True
#     #     trainee = UserType.objects.get(type='TRAINEE')
#     #     types = [u.types.all() for u in queryset]
#     #     try:
#     #
#     #     for qs in types:
#     #         if trainee not in qs:
#     #             can_assign_as_trainee = False
#     #             continue
#     #     if can_assign_as_trainee:
#     #         pass
#     #     else:
#     #         self.add_message(request, "no", messages.ERROR)
#
#
#
#
#
#     #
#     # def get_actions(self, request):
#     #     actions = super().get_actions(request)
#     #     if not request.user.has_perm('auth.change_user'):
#     #         del actions['activate_users']
#     #     return actions