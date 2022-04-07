import json
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from cms.forms import AssignmentForm, QuizForm, QuestionForm, QuizCategoryForm, ExcelForm
from cms.models import Quiz, Assignment, Question
from users.models import UserType
from django.db.models import Q
import pandas as pd


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
def all_questions_list(request):
    if request.user.is_staff:
        questions = Question.objects.all()
    else:
        questions = Question.objects.filter(created_by=request.user)

    paginator = Paginator(questions, 10)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'questions': questions,
        'page_obj': page_obj
    }
    if request.htmx:
        return render(request, 'cms/includes/all_questions_list.html', context=context)
    return render(request, 'cms/all_questions.html', context=context)


def htmx_paginate_questions(request):
    if request.user.is_staff:
        questions = Question.objects.all()
    else:
        questions = Question.objects.filter(created_by=request.user)

    paginator = Paginator(questions, 10)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'questions': questions,
        'page_obj': page_obj
    }
    return render(request, 'cms/includes/questions_loop.html', context=context)


def search_all_questions(request):
    if request.method == 'GET':
        url_parameter = request.GET.get("query")
        if request.user.is_superuser:
            questions = Question.objects.filter(
                Q(question__icontains=url_parameter)# | Q(description__icontains=url_parameter)
            )
            context = {
                'questions': questions
            }
        else:
            questions = Question.objects.filter(
                Q(question__icontains=url_parameter) & Q(created_by=request.user)
            )
            context = {
                'questions': questions
            }
        return render(request, 'cms/includes/all_questions_list.html', context=context)


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
def create_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            ques = form.save(commit=False)
            ques.created_by = request.user
            ques.save()
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "questionListChanged": None,
                    "showMessage": f"question added."
                })
            })
    else:
        form = QuestionForm()
    return render(request, 'cms/includes/add_question_form.html', {'form': form})


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
def update_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('cms:all_questions_list')
    else:
        form = QuestionForm(instance=question)
    return render(request, 'cms/create_question.html', {'form': form, 'question': question})


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
@require_http_methods(['DELETE'])
def delete_question(request, pk):
    if request.user.is_staff:
        question = get_object_or_404(Question, pk=pk)
    else:
        question = get_object_or_404(Question, pk=pk, created_by=request.user)
    question.delete()
    return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "questionListChanged": None,
                "showMessage": f"question deleted."
            })
        })


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
def upload_questions(request):
    if request.method == 'POST':
        form = ExcelForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES.get('file')
            # file = request.FILES['file']
            csv_data = pd.read_csv(file)
            print(csv_data.head())
            row_iter = csv_data.iterrows()
            objs = [
                Question(
                    question=row['question'],
                    op1=row['op1'],
                    op2=row['op2'],
                    op3=row['op3'],
                    op4=row['op4'],
                    correct_answer=row['correct_answer'],
                    marks=row['marks'],
                    explanation=row['explanation'],
                    created_by=request.user,
                )
                for index, row in row_iter
            ]
            Question.objects.bulk_create(objs)
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "questionListChanged": None,
                    "showMessage": f"question added."
                })
            })
    else:
        form = ExcelForm()
    return render(request, 'cms/import_questions.html', {'form': form})


##########################################################################
##########################################################################
##########################################################################


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
def create_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "assignmentListChanged": None,
                    "showMessage": 'assignment added'
                    # "showMessage": f"{assignment.title} added."
                })
            })
    else:
        form = AssignmentForm()
    return render(request, 'cms/includes/add_assignment_form.html', {'form': form})


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
def all_assignments_list(request):
    if request.user.is_staff:
        assignments = Assignment.objects.all()
    else:
        assignments = Assignment.objects.filter(created_by=request.user)

    paginator = Paginator(assignments, 8)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'assignments': assignments,
        'page_obj': page_obj,
    }
    if request.htmx:
        return render(request, 'cms/includes/all_assignments_list.html', context=context)
    return render(request, 'cms/all_assignments.html', context=context)


def htmx_paginate_assignments(request):
    if request.user.is_staff:
        assignments = Assignment.objects.all()
    else:
        assignments = Assignment.objects.filter(created_by=request.user)

    paginator = Paginator(assignments, 8)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'assignments': assignments,
        'page_obj': page_obj,
    }
    return render(request, 'cms/includes/assignments_loop.html', context=context)


@user_passes_test(lambda u: UserType.objects.get(type='TRAINEE') in u.types.all())
def my_assignments_list(request):
    trainings = request.user.training_set.all().prefetch_related('assignment')
    assignment_list = [list(t.assignment.all()) for t in trainings]
    assignments = list(set([item for elem in assignment_list for item in elem]))
    print(assignments)
    paginator = Paginator(assignments, 4)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'assignments': assignments,
        'page_obj': page_obj,
    }
    if request.htmx:
        return render(request, 'cms/includes/all_assignments_list.html', context)
    return render(request, 'cms/my_assignments.html', context)


def htmx_paginate_my_assignments(request):
    trainings = request.user.training_set.all().prefetch_related('assignment')
    assignment_list = [list(t.assignment.all()) for t in trainings]
    assignments = list(set([item for elem in assignment_list for item in elem]))
    print(assignments)
    paginator = Paginator(assignments, 4)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'assignments': assignments,
        'page_obj': page_obj,
    }
    return render(request, 'cms/includes/my_assignments_loop.html', context=context)


def all_assignments_search(request):
    if request.method == 'GET':
        url_parameter = request.GET.get("query")
        assignments = Assignment.objects.filter(
            Q(title__icontains=url_parameter) | Q(description__icontains=url_parameter)
        )
        context = {
            'assignments': assignments
        }
        return render(request, 'cms/includes/all_assignments_search_results.html', context=context)


def my_assignments_search(request):
    if request.method == 'GET':
        url_parameter = request.GET.get("query")
        trainings = request.user.training_set.all().prefetch_related('assignment')
        assignment_list = \
            [list(t.assignment.filter(
                Q(title__icontains=url_parameter) | Q(description__icontains=url_parameter)
            )) for t in trainings]
        assignments = set([item for elem in assignment_list for item in elem])

        context = {
            'assignments': assignments
        }
        return render(request, 'cms/includes/all_assignments_search_results.html', context=context)


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
@require_http_methods(['DELETE'])
def delete_assignment(request, pk):
    if request.user.is_staff:
        assignment = get_object_or_404(Assignment, pk=pk)
    else:
        assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    assignment.delete()
    return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "assignmentListChanged": None,
                "showMessage": f"assignment deleted."
            })
        })


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
def update_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            return redirect('cms:all_assignments_list')
            # return HttpResponse(
            #     status=204,
            #     headers={
            #         'HX-Trigger': json.dumps({
            #             "assignmentListChanged": None,
            #             "showMessage": f"{assignment.title} updated."
            #         })
            #     }
            # )
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, 'cms/create_assignment.html', {
        'form': form,
        'assignment': assignment,
    })



##########################################################################
##########################################################################
##########################################################################


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
def update_quiz(request, pk):
    if request.user.is_staff:
        quiz = get_object_or_404(Quiz, pk=pk)
    else:
        quiz = get_object_or_404(Quiz, pk=pk, created_by=request.user)

    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect('cms:all_quizzes')
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'cms/create_quiz.html', {'form': form})


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
def create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()
            form.save_m2m()
            return redirect('cms:all_quizzes')
    else:
        form = QuizForm()
    return render(request, 'cms/create_quiz.html', {'form': form})


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
@require_http_methods(['DELETE'])
def delete_quiz(request, pk):
    if request.user.is_staff:
        quiz = get_object_or_404(Quiz, pk=pk)
    else:
        quiz = get_object_or_404(Quiz, pk=pk, created_by=request.user)
    quiz.delete()
    return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "quizListChanged": None,
                "showMessage": f"quiz deleted."
            })
        })


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types)
def create_quiz_category(request):
    if request.method == 'POST':
        form = QuizCategoryForm(request.POST)
        if form.is_valid():
            qc = form.save(commit=False)
            qc.created_by = request.user
            qc.save()
            messages.success(request, 'Quiz Category Created')
            return redirect('cms:all_quizzes')
    else:
        form = QuizCategoryForm()
    return render(request, 'cms/create_quiz.html', {'form': form})


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
def all_quizzes_list(request):
    if request.user.is_staff:
        quizzes = Quiz.objects.all()
    else:
        quizzes = Quiz.objects.filter(created_by=request.user)

    paginator = Paginator(quizzes, 3)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'quizzes': quizzes,
        'page_obj': page_obj
    }
    if request.htmx:
        return render(request, 'cms/includes/all_quizzes_list.html', context=context)
    return render(request, 'cms/all_quizzes.html', context=context)


def htmx_paginate_quizzes(request):
    if request.user.is_staff:
        quizzes = Quiz.objects.all()
    else:
        quizzes = Quiz.objects.filter(created_by=request.user)

    paginator = Paginator(quizzes, 3)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'quizzes': quizzes,
        'page_obj': page_obj,
    }
    return render(request, 'cms/includes/quizzes_loop.html', context=context)


@user_passes_test(lambda u: UserType.objects.get(type='TRAINEE') in u.types.all())
def my_quizzes_list(request):
    trainings = request.user.training_set.all().prefetch_related('quiz')
    quizzes_list = [list(t.quiz.all()) for t in trainings]
    quizzes = list(set([item for elem in quizzes_list for item in elem]))
    print(quizzes)
    paginator = Paginator(quizzes, 3)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'quizzes': quizzes,
        'page_obj': page_obj,
    }
    if request.htmx:
        return render(request, 'cms/includes/all_quizzes_list.html', context)
    return render(request, 'cms/my_quizzes.html', context)


def htmx_paginate_my_quizzes(request):
    trainings = request.user.training_set.all().prefetch_related('assignment')
    quizzes_list = [list(t.quiz.all()) for t in trainings]
    quizzes = list(set([item for elem in quizzes_list for item in elem]))
    print(quizzes)
    paginator = Paginator(quizzes, 3)  # Show 25 contacts per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'quizzes': quizzes,
        'page_obj': page_obj,
    }
    return render(request, 'cms/includes/my_quizzes_loop.html', context=context)


def all_quizzes_search(request):
    if request.method == 'GET':
        url_parameter = request.GET.get("query")
        quizzes = Quiz.objects.filter(
            Q(title__icontains=url_parameter) | Q(description__icontains=url_parameter)
        )
        context = {
            'quizzes': quizzes
        }
        return render(request, 'cms/includes/all_quizzes_list.html', context=context)


def my_quizzes_search(request):
    if request.method == 'GET':
        url_parameter = request.GET.get("query")
        trainings = request.user.training_set.all().prefetch_related('assignment')
        quizzes_list = \
            [list(t.quiz.filter(
                Q(title__icontains=url_parameter) | Q(description__icontains=url_parameter)
            )) for t in trainings]
        quizzes = set([item for elem in quizzes_list for item in elem])

        context = {
            'quizzes': quizzes
        }
        return render(request, 'cms/includes/all_quizzes_list.html', context=context)
