from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
import boto3
from home.admin import BaseAdmin
from . models import Training, Enrollment

User = get_user_model()
client = boto3.client(
    'chime-sdk-meetings',
    aws_access_key_id=settings.AWS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name='us-east-1'
)


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    classes = ['collapse']

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Training)
class TrainingAdmin(BaseAdmin):
    list_display = ('title', 'training_type', 'created_by', 'total_attendees', 'start_at', 'duration', 'image_tag',)
    fields = ('title', 'description', ('course', 'training_type', 'other'), ('main_image',), 'quiz', 'assignment',
              ('content', 'director', 'coordinator'), ('start_at', 'end_at'), ('unique_id', 'chime_id'),
              ('created_at', 'created_by', 'updated_at'),)
    # filter_horizontal = ['quiz', 'assignment']
    readonly_fields = ('unique_id', 'created_by', 'created_at', 'updated_at', 'image_tag', 'chime_id')
    search_fields = ['attendees']
    inlines = (EnrollmentInline, )
    autocomplete_fields = ['quiz', 'assignment']
    #actions = ['start_meeting', ]

    @admin.display(description='Flyer')
    def image_tag(self, obj):
        return format_html('<img src="{0}" style="width: 100px; height:100px;" />'.format(obj.main_image.url))

    @admin.display(description='Total Attendees')
    def total_attendees(self, obj):
        return obj.attendees.all().count()

    # @admin.action(description='Start Meeting')
    # def start_meeting(self, request, queryset):
    #     if queryset.count() != 1:
    #         self.message_user(request, 'Cannot Select multiple trainings', messages.ERROR)
    #     obj = queryset[0]
    #     attendees_ids = [u.unique_id for u in obj.attendees.all()]
    #     attendees = []
    #     for i in attendees_ids:
    #         attendees.append({
    #             'ExternalUserId': str(i)
    #         })
    #     print('FINAL ATTENDEES for API CALL')
    #     print(len(attendees))
    #     print(attendees)
    #
    #     res = client.create_meeting_with_attendees(
    #         MediaRegion='ap-south-1',
    #         ExternalMeetingId=str(obj.unique_id),
    #         MeetingFeatures={
    #             'Audio': {
    #                 'EchoReduction': 'AVAILABLE'
    #             }
    #         },
    #         Attendees=attendees
    #     )
    #     print('RESPONSE FROM CHIME')
    #     print(res['Meeting'])
    #     print(res['Attendees'])
    #     obj.chime_id = res['Meeting']['MeetingId']
    #     obj.save()
    #
    #     id_list = [i['ExternalUserId'] for i in res['Attendees']]
    #     print('EXTERUSERID LIST from chime')
    #     print(id_list)
    #
    #     info_list = [{k: v for k, v in d.items() if k != 'ExternalUserId'} for d in res['Attendees']]
    #     print('ExtraINFO LIST from chime')
    #     print(info_list)
    #
    #     req_dict = dict(zip(id_list, info_list))
    #     print('FINAL DICT')
    #     print(req_dict)
    #
    #     with transaction.atomic():
    #         for key, value in req_dict.items():
    #             Enrollment.objects.filter(user__unique_id=key).update(join_token=value['JoinToken'], attendee_id=value['AttendeeId'])


@admin.register(Enrollment)
class EnrollmentAdmin(BaseAdmin):
    list_display = ('user', 'training', 'permission')
    list_filter = ('training',)
    fields = (('training', 'permission', 'user'), ('start_at', 'end_at', 'joined_at'), 'notes', 'training_status',
              'unique_id', ('created_at', 'created_by', 'updated_at'), ('attendee_id', 'join_token'))
    search_fields = ['user', 'training']
    autocomplete_fields = ['user', 'training']
    readonly_fields = ('unique_id', 'created_by', 'created_at', 'updated_at', 'attendee_id', 'join_token')

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.permission == 'ADMIN':
            return False
        return True



