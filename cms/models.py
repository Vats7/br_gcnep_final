from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from home.models import BaseModel


class QuizCategory(BaseModel):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Quiz Category'
        verbose_name_plural = 'Quiz Categories'

    def __str__(self):
        return self.title


class Question(BaseModel):
    question = models.TextField(_('Question'), unique=True)
    op1 = models.CharField(_('Option 1'), max_length=500)
    op2 = models.CharField(_('Option 2'), max_length=500, blank=True)
    op3 = models.CharField(_('Option 3'), max_length=500, blank=True)
    op4 = models.CharField(_('Option 4'), max_length=500, blank=True)
    correct_answer = models.CharField(
        _('Correct Answer'),
        max_length=500,
        help_text=''
    )
    marks = models.PositiveIntegerField(_('Marks'), default=5)
    explanation = models.TextField(
        _('Explanation'),
        blank=True,
        help_text='Explain your Answer if needed. This is an OPTIONAL field.'
    )

    def __str__(self):
        return self.question

    def clean(self):
        all_options = [self.op1, self.op2, self.op3, self.op4]
        if self.correct_answer not in all_options:
            raise ValidationError('At least one of the Options should be the same as Correct Answer')


class Quiz(BaseModel):
    class Difficulty(models.TextChoices):
        BEGINNER = 'BEGINNER', 'Beginner'
        INTERMEDIATE = 'INTERMEDIATE', 'Intermediate'
        ADVANCE = 'ADVANCE', 'Advance'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLIC = 'PUBLIC', 'Public'
        CLOSE = 'CLOSE', 'Close'

    #trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE)
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True, null=True)
    status = models.CharField(_('Status'), max_length=15, choices=Status.choices, default='DRAFT')
    difficulty = models.CharField(_('Difficulty Level'), max_length=15, choices=Difficulty.choices)
    questions = models.ManyToManyField(Question)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at']

    @property
    def total_questions(self):
        return len(self.questions.all())

    @property
    def total_marks(self):
        return sum([q.marks for q in self.questions.all()])

    def __str__(self):
        return self.title


class Assignment(BaseModel):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    #trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    def __str__(self):
        return self.title




