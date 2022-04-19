import uuid
from io import BytesIO
from PIL import Image
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from home.models import BaseModel, School, Department
from users.validators import validate_file_size #validate_is_jpg_or_png


def user_directory_path(instance, filename):
    return 'users/user_{0}/{1}'.format(instance.user.id, filename)


class UserType(models.Model):

    class Type(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        MODERATOR = 'MODERATOR', _('Moderator')
        TRAINER = 'TRAINER', _('Trainer')
        TRAINEE = 'TRAINEE', _('Trainee')
        OBSERVER = 'OBSERVER', _('Observer')

    type = models.CharField(
        max_length=15,
        choices=Type.choices,
    )

    class Meta:
        verbose_name = 'User Type'
        verbose_name_plural = 'User Types'

    def __str__(self):
        return self.type


class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))

        if not name:
            raise ValueError(_('The Name must be set'))

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, name, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(_('Email Address'), unique=True, max_length=50)
    name = models.CharField(_('Full Name'), max_length=50)
    is_staff = models.BooleanField(default=False)
    is_mod = models.BooleanField(
        default=False,
        verbose_name='Moderator',
        help_text="Is this a Moderator Account?"
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name='Admin',
        help_text="Is this an Administrator Account?",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active User',
        help_text="All users are ACTIVE by default. "
                  "Turn this OFF to SUSPEND the user. "
                  "Suspended users can not Login in the system.",
    )

    types = models.ManyToManyField(UserType)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['name',]
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    objects = CustomUserManager()

    class Meta:
        verbose_name = '   User Management'
        verbose_name_plural = '   User Management'
        ordering = ['-id']

    def __str__(self):
        return self.email

    def clean(self):
        if self.is_mod and self.is_superuser:
            raise ValidationError({'is_mod': 'Select Only One'})

    def save(self, *args, **kwargs):
        if not self.id:
            if self.is_mod or self.is_superuser:
                self.is_staff = True
        super().save(*args, **kwargs)


class ModeratorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='mod_profile')
    first_name = models.CharField(_('First Name'), max_length=30, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=30, blank=True)
    designation = models.CharField(_('Designation'), max_length=50, blank=True)
    unit = models.CharField(_('Unit'), max_length=30, blank=True)

    class Meta:
        verbose_name = '  Moderator Profile'
        verbose_name_plural = '  Moderator Profiles'

    def __str__(self):
        return self.user.email


class UserProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='users', blank=True, null=True)
    #department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(_('First Name'), max_length=30, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=30, blank=True)
    image = models.ImageField(
        upload_to=user_directory_path,
        verbose_name='Image',
        help_text='Upload an Image. Should be less than 5MB',
        validators=[validate_file_size, ],
        blank=True,
    )
    gender = models.CharField(_('Gender'), max_length=50, choices=Gender.choices, blank=True)
    dob = models.DateField(_('Date-Of-Birth'), blank=True, null=True)
    pob = models.CharField(_('Place-Of-Birth'), max_length=30, blank=True, null=True)#change
    org_ins = models.CharField(_('Organisation/Institute'), max_length=50, blank=True)
    dept_name = models.CharField(_('Department Name'), max_length=30, blank=True)
    dept_id = models.CharField(_('Department Id'), max_length=20, blank=True)
    ofc_add = models.CharField(_('Office Address'), max_length=100, blank=True)
    ofc_number = models.CharField(_('Office Contact Number'), max_length=20, blank=True)
    nationality = models.TextField(_('Nationality'), max_length=100, blank=True)
    fax = models.CharField(_('FAX Number'), max_length=30, blank=True)
    secondary_email = models.EmailField(_('Secondary Email Address'), blank=True)

    class Meta:
        verbose_name = ' Trainer/Trainee/Observer Profile'
        verbose_name_plural = ' Trainer/Trainee/Observer Profiles'
        ordering = ['-id']

    def __str__(self):
        return self.user.email

    # def get_thumbnail(self):
    #     if self.thumbnail:
    #         return self.thumbnail.url
    #     else:
    #         if self.image:
    #             self.thumbnail = self.make_thumbnail(self.image)
    #             self.save()
    #             return self.thumbnail.url
    #         else:
    #             return ''

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)
        thumbnail = File(thumb_io, name=image.name)

        return thumbnail


class Education(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='educations')

    institute = models.CharField(_('Name and Place of Institute'), max_length=200,)
    field_of_study = models.CharField(_('Field of Study'), max_length=50,)
    degree = models.CharField(_('Diploma or Degree'), max_length=70,)
    start = models.DateField(_('From'))
    end = models.DateField(_('To'))

    def __str__(self):
        return self.user.user.name


class Employment(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='employments')

    employer = models.CharField(_('Name of Employer'), max_length=200, )
    place = models.CharField(_('Place'), max_length=50, )
    title = models.CharField(_('Title or Position'), max_length=50, )
    description = models.TextField(_('Description'), max_length=200, )
    start = models.DateField(_('From'))
    end = models.DateField(_('To'))

    def __str__(self):
        return self.user.user.name


class Document(BaseModel):
    class Type(models.TextChoices):
        SIGNATURE = 'SIGNATURE', _('Signature')
        PASSPORT = 'PASSPORT', _('Passport')
        VISA = 'VISA', _('Visa')
        APPROVAL = 'APPROVAL', _('Approval')
        #AV = 'AV', _('AudioVideo')

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='documents')
    type = models.CharField(
        max_length=15,
        choices=Type.choices,
    )
    file = models.FileField(
        upload_to=user_directory_path,
        verbose_name='Upload File',
        validators=[validate_file_size, ]
        #help_text='Upload upto 4 images (.jpg or .png)',
        # validators=[validate_file_size, FileExtensionValidator(allowed_extensions=['jpg', 'png'])],
    )

    def __str__(self):
        return self.user.user.name


# class Education(BaseModel):
#     user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, unique=True, related_name='educations')
#
#     ins1 = models.CharField(_('Name and Place of Institute'), max_length=200,)
#     study_f1 = models.CharField(_('Field of Study'), max_length=50,)
#     degree1 = models.CharField(_('Diploma or Degree'), max_length=70,)
#     from1 = models.DateField(_('From'))
#     to1 = models.DateField(_('To'))
#
#     ins2 = models.CharField(_('Name and Place of Institute'), max_length=200, )
#     study_f2 = models.CharField(_('Field of Study'), max_length=50,)
#     degree2 = models.CharField(_('Diploma or Degree'), max_length=70,)
#     from2 = models.DateField(_('From'))
#     to2 = models.DateField(_('To'))
#
#     ins3 = models.CharField(_('Name and Place of Institute'), max_length=200,)
#     study_f3 = models.CharField(_('Field of Study'), max_length=50,)
#     degree3 = models.CharField(_('Diploma or Degree'), max_length=70,)
#     from3 = models.DateField(_('From'))
#     to3 = models.DateField(_('To'))
#
#     @property
#     def total(self):
#         return (self.to1 - self.from1) + (self.to2 - self.from2) + (self.to3 - self.from3)
#
#     def clean(self):
#         if self.to1 and self.from1 and self.to2 and self.from2 and self.to3 and self.from3:
#             if self.to1 >= self.from1:
#                 raise ValidationError({'to1': 'Cannot be later than from1'})
#             if self.to2 >= self.from2:
#                 raise ValidationError({'to1': 'Cannot be later than from2'})
#             if self.to3 >= self.from3:
#                 raise ValidationError({'to1': 'Cannot be later than from3'})
#
#
# class Employment(BaseModel):
#     user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, unique=True, related_name='employments')
#
#     emp1 = models.CharField(_('Name of Employer'), max_length=200,)
#     place1 = models.CharField(_('Place'), max_length=50,)
#     title1 = models.CharField(_('Title or Position'), max_length=50,)
#     desc1 = models.TextField(_('Description'), max_length=200,)
#     from1 = models.DateField(_('From'))
#     to1 = models.DateField(_('To'))
#
#     emp2 = models.CharField(_('Name of Employer'), max_length=200,)
#     place2 = models.CharField(_('Place'), max_length=50,)
#     title2 = models.CharField(_('Title or Position'), max_length=50,)
#     desc2 = models.TextField(_('Description'), max_length=200,)
#     from2 = models.DateField(_('From'))
#     to2 = models.DateField(_('To'))
#
#     emp3 = models.CharField(_('Name of Employer'), max_length=200,)
#     place3 = models.CharField(_('Place'), max_length=50,)
#     title3 = models.CharField(_('Title or Position'), max_length=50,)
#     desc3 = models.TextField(_('Description'), max_length=200,)
#     from3 = models.DateField(_('From'))
#     to3 = models.DateField(_('to'))
#
#     @property
#     def total(self):
#         return (self.to1 - self.from1) + (self.to2 - self.from2) + (self.to3 - self.from3)
#
#     def clean(self):
#         if self.to1 and self.from1 and self.to2 and self.from2 and self.to3 and self.from3:
#             if self.to1 >= self.from1:
#                 raise ValidationError({'to1': 'Cannot be later than from1'})
#             if self.to2 >= self.from2:
#                 raise ValidationError({'to2': 'Cannot be later than from2'})
#             if self.to3 >= self.from3:
#                 raise ValidationError({'to3': 'Cannot be later than from3'})
#
#
# class Document(BaseModel):
#     user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='documents')
#     sig_1 = models.ImageField(
#         upload_to=user_directory_path,
#         verbose_name='Signature Image',
#         help_text='Upload a photo with your Signature. Should be less than 5MB',
#         validators=[validate_file_size, ],
#     )
#     pass_1 = models.ImageField(
#         upload_to=user_directory_path,
#         verbose_name='Passport Front Image',
#         help_text='Upload an Image of the front page of your Passport. Should be less than 5MB',
#         validators=[validate_file_size, ],
#         blank=True,
#     )
#     pass_2 = models.ImageField(
#         upload_to=user_directory_path,
#         verbose_name='Passport Back Image',
#         help_text='Upload an Image of the Last page of your Passport. Should be less than 5MB',
#         validators=[validate_file_size, ],
#         blank=True,
#     )
#     visa_1 = models.ImageField(
#         upload_to=user_directory_path,
#         verbose_name='Visa Image 1',
#         help_text='Upload an Image of the Visa. Should be less than 5MB',
#         validators=[validate_file_size, ],
#         blank=True,
#     )
#     visa_2 = models.ImageField(
#         upload_to=user_directory_path,
#         verbose_name='Visa Image 2',
#         help_text='Upload another Image of the Visa. Should be less than 5MB',
#         validators=[validate_file_size, ],
#         blank=True,
#     )
#     approval_1 = models.ImageField(
#         upload_to=user_directory_path,
#         verbose_name='Approval 2',
#         help_text='Upload another Image of the Visa. Should be less than 5MB',
#         validators=[validate_file_size, ],
#         blank=True,
#     )
#     approval_2 = models.ImageField(
#         upload_to=user_directory_path,
#         verbose_name='Approval 2',
#         help_text='Upload another Image of the Visa. Should be less than 5MB',
#         validators=[validate_file_size, ],
#         blank=True,
#     )
#     audio_video = models.FileField(
#         upload_to=user_directory_path,
#         verbose_name='Audio/Video',
#         help_text='Upload Images/Audio/Video Files',
#         validators=[validate_file_size, ],
#         blank=True,
#     )
#
#     def __str__(self):
#         return self.user.name




