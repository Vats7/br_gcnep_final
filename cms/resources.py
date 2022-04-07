from import_export import resources
from .models import Question
from import_export import fields
from import_export import widgets


class QuestionResource(resources.ModelResource):
    created_by = fields.Field(
        column_name='created_by',
        attribute='created_by',
        widget=widgets.ForeignKeyWidget(Question, "created_by"))

    class Meta:
        model = Question
        fields = ('id', 'question', 'op1', 'op2', 'op3', 'op4',
                  'correct_answer', 'marks', 'explanation', 'created_at',
                  'created_by', 'updated_at', 'unique_id')
