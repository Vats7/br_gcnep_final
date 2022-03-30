from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from cms.forms import AssignmentForm, QuizForm, QuestionForm, QuizCategoryForm
from cms.models import Quiz, Assignment, Question
from users.models import UserType


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types)
def create_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            return redirect('cms:all_assignments')
    else:
        form = AssignmentForm()
    return render(request, 'cms/create_assignment.html', {'form': form})


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
def all_assignments(request):
    if request.user.is_staff:
        assignments = Assignment.objects.all()
    else:
        assignments = Assignment.objects.filter(created_by=request.user)

    context = {
        'assignments': assignments,
        'form': AssignmentForm()
    }
    return render(request, 'cms/all_assignments.html', context=context)


@user_passes_test(lambda u: UserType.objects.get(type='TRAINEE') in u.types.all())
def my_assignments(request):
    trainings = request.user.training_set.all().prefetch_related('assignment')
    assignment_list = [list(t.quiz.all()) for t in trainings]
    assignments = set([item for elem in assignment_list for item in elem])
    print(assignments)
    return render(request, 'cms/my_assignments.html', context={'assignments': assignments})


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types)
def create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()
            return redirect('cms:all_quizzes')
    else:
        form = QuizForm()
    return render(request, 'cms/create_quiz.html', {'form': form})


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
def all_quizzes(request):
    if request.user.is_staff:
        quizzes = Quiz.objects.all()
    else:
        quizzes = Quiz.objects.filter(created_by=request.user)
    print(quizzes)
    context = {
        'quizzes': quizzes,
        'form': QuizCategoryForm()
    }
    return render(request, 'cms/all_quizzes.html', context=context)


@user_passes_test(lambda u: UserType.objects.get(type='TRAINEE') in u.types.all())
def my_quizzes(request):
    trainings = request.user.training_set.all().prefetch_related('quiz')
    quizzes_list = [list(t.quiz.all()) for t in trainings]
    quizzes = set([item for elem in quizzes_list for item in elem])
    print(quizzes)
    return render(request, 'cms/my_quizzes.html', context={'quizzes': quizzes})


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types.all())
def all_questions(request):
    if request.user.is_staff:
        questions = Question.objects.all()
    else:
        questions = Question.objects.filter(created_by=request.user)
    context = {
        'questions': questions,
        'form': QuestionForm()
    }
    return render(request, 'cms/all_questions.html', context=context)


@user_passes_test(lambda u: u.is_staff or UserType.objects.get(type='TRAINER') in u.types)
def create_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            ques = form.save(commit=False)
            ques.created_by = request.user
            ques.save()
            return redirect('cms:all_questions')
    else:
        form = QuestionForm()
    return render(request, 'cms/create_question.html', {'form': form})
