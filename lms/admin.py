from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.utils.translation import ngettext
import boto3
import botocore
from home.admin import BaseAdmin
from . models import Training, Enrollment

User = get_user_model()
client = boto3.client('chime-sdk-meetings')


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Training)
class TrainingAdmin(BaseAdmin):
    list_display = ('title', 'training_type', 'created_by', 'start_at', 'duration', 'image_tag',)
    fields = ('title', 'description', ('course', 'training_type', 'other'), ('main_image',), 'quiz', 'assignment',
              ('content', 'director', 'coordinator'), ('start_at', 'end_at'), 'unique_id',
              ('created_at', 'created_by', 'updated_at'),)
    # filter_horizontal = ['quiz', 'assignment']
    readonly_fields = ('unique_id', 'created_by', 'created_at', 'updated_at', 'image_tag')
    search_fields = ['attendees']
    inlines = (EnrollmentInline, )
    autocomplete_fields = ['quiz', 'assignment']
    actions = ['start_meeting', ]

    @admin.display(description='Flyer')
    def image_tag(self, obj):
        return format_html('<img src="{0}" style="width: 100px; height:100px;" />'.format(obj.main_image.url))

    @admin.action(description='Start Meeting')
    def start_meeting(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, 'Cannot Select multiple trainings', messages.ERROR)
        #updated = queryset.update(is_active=True)
        obj = queryset[0]
        admin_mod = [{
            'ExternalUserId': str(obj.created_by.unique_id),
        }]
        attendees_ids = [u.user.unique_id for u in obj.attendees.all()]
        attendees = []
        for idx in attendees_ids:
            attendees.append({
                'ExternalUserId': str(idx),
            })
        final = admin_mod + attendees
        print(final)

        # res = client.create_meeting_with_attendees(
        #     MediaRegion='ap-south-1',
        #     ExternalMeetingId=str(obj.unique_id),
        #     MeetingFeatures={
        #         'Audio': {
        #             'EchoReduction': 'AVAILABLE'
        #         }
        #     },
        #     Attendees=final
        # )
        # print(res)


@admin.register(Enrollment)
class EnrollmentAdmin(BaseAdmin):
    fields = (('training', 'permission', 'user'), ('start_at', 'end_at', 'joined_at'), 'notes', 'training_status',)
    search_fields = ['user', 'training']
    autocomplete_fields = ['user', 'training']
    readonly_fields = ('user_unique_id', 'unique_id', 'created_by', 'created_at', 'updated_at',)

