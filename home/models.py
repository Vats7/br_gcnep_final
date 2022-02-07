import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext as _


class BaseModel(models.Model):
    unique_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class School(BaseModel):
    name = models.CharField(_('Name'), max_length=200)

    def __str__(self):
        return self.name


class Department(BaseModel):
    name = models.CharField(_('Name'), max_length=200)

    def __str__(self):
        return self.name


class Course(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    title = models.CharField(_('Title'), max_length=200)
    syllabus = models.TextField(_('Syllabus'), blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# class PostQuerySet(models.QuerySet):
#     def search(self, query=None):
#         qs = self
#         if query is not None:
#             or_lookup_with_q = (
#                 Q(title__icontains=query) |
#                 Q(description__icontains=query) |
#                 Q(slug__icontains=query)
#             )
#
#             qs = qs.filter(or_lookup_with_q).distinct()
#         return qs
#
#
# class PostManager(models.Manager):
#     def get_queryset(self, *args, **kwargs):
#         return PostQuerySet(self.model, using=self._db)
#
#     def search(self, query=None):
#         return self.get_queryset().search(query=query)
#
# class Post(models.Model):
#