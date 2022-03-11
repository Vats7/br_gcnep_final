from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from home.models import BaseModel, School, Course
from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from cms.models import Quiz, Assignment
from users.models import UserProfile, UserType


def validate_file_size(value):
    filesize = value.size

    if filesize > 5242880:
        raise ValidationError("The maximum file size that can be uploaded is 5MB")
    else:
        return value


class Training(BaseModel):
    TRAINING_TYPE = (
        ('WORKSHOP', 'Workshop'),
        ('PROGRAM', 'Program'),
        ('MEETING', 'Meeting'),
        ('OTHER', 'Other')
    )
    title = models.CharField(_('Title'), max_length=50)
    description = models.TextField(_('Description'), max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='trainings')
    training_type = models.CharField(
        choices=TRAINING_TYPE,
        max_length=10,
        verbose_name='Training Type',
        help_text="Please Select the relevant training type from the dropdown"
    )
    other = models.CharField(
        _('Type'),
        max_length=30,
        blank=True,
        help_text='Only required if Training Type is "OTHER"'
    )
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Enrollment',
        #related_name='all_attendees',
        through_fields=('training', 'user'),
    )
    main_image = models.ImageField(
        upload_to='trainings/main_image/',
        verbose_name='Image',
        help_text='Upload an Image(Flyer). Should be less than 5MB',
        validators=[validate_file_size, ],
    )
    quiz = models.ManyToManyField(Quiz, blank=True)
    assignment = models.ManyToManyField(Assignment, blank=True)
    content = models.CharField(max_length=100, blank=True)
    director = models.CharField(max_length=30, blank=True)
    coordinator = models.CharField(max_length=30, blank=True)
    start_at = models.DateTimeField(blank=True, null=True)###change
    end_at = models.DateTimeField(blank=True, null=True)####change
    #is_active = models.BooleanField(default=False)
    chime_id = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = ' Training'
        verbose_name_plural = ' Trainings'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_master_image_filename(self):
        return str(self.main_image)[str(self.main_image).index(f"training_main_image/{self.pk}/"):]

    def get_absolute_url(self):
        return reverse('lms:training_detail', kwargs={'pk': self.pk})

    @property
    def total_attendees(self):
        return self.attendees.all().count()

    @property
    def duration(self):
        if self.start_at and self.end_at is not None:
            return self.end_at - self.start_at
        return f"Time not set"

    @property
    def is_started(self):
        now = timezone.localtime(timezone.now())
        if now >= self.start_at:
            return True
        return False

    def clean(self):
        if self.start_at and self.end_at:
            # now = timezone.localtime(timezone.now())
            # if self.start_at <= now:
            #     raise ValidationError('Start Time can not be the current time')
            if self.start_at >= self.end_at:
                raise ValidationError('Start Time Can Not be more than or equal to end Time')
        if self.training_type == 'OTHER':
            if not self.other:
                raise ValidationError({'other': 'This field is required if Training Type is OTHER'})


class Enrollment(BaseModel):
    class Type(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        PRIMARY = 'PRIMARY', _('Primary Trainer')
        OTHER = 'OTHER', _('Other Trainer')
        TRAINEE = 'TRAINEE', _('Trainee')
        OBSERVER = 'OBSERVER', _('Observer')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrolled')
    user_unique_id = models.CharField(unique=True, max_length=15)#uuid.uuid4().hex[:13].upper()
    training = models.ForeignKey(Training, on_delete=models.CASCADE)
    permission = models.CharField(max_length=15, choices=Type.choices)
    training_status = models.BooleanField(default=False)
    notes = models.CharField(_('Optional Notes'), max_length=64, blank=True)
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    joined_at = models.DateTimeField(blank=True, null=True)
    attendee_id = models.CharField(max_length=200, blank=True)
    join_token = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = [['user', 'training']]
        verbose_name = 'Enrolment'
        verbose_name_plural = 'Enrolments'
        ordering = ['-created_at']

    def __str__(self):
        #return f"user----{self.user.user.name} training---{self.training.title}"
        return f"{self.user.email} is enrolled in {self.training.title}"

    def clean(self):
        trainer = UserType.objects.get(type='TRAINER')
        trainee = UserType.objects.get(type='TRAINEE')
        observer = UserType.objects.get(type='OBSERVER')
        user_types = self.user.types.all()
        if trainer not in user_types:
            if self.permission in ['PRIMARY', 'OTHER']:
                raise ValidationError('Selected User does not have required permission')

        if trainee not in user_types:
            if self.permission == 'TRAINEE':
                raise ValidationError('Selected User does not have required permission')

        if observer not in user_types:
            if self.permission == 'OBSERVER':
                raise ValidationError('Selected User does not have required permission')


