import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
import pandas as pd
from django.views.decorators.http import require_http_methods

from uploads.forms import FileUploadForm
import csv

from uploads.models import FileUpload
from users.models import UserProfile

User = get_user_model()


# def process_users_csv(obj):
#     with open(obj.file.path, 'r') as f:
#         reader = csv.reader(f)
#         for i, row in enumerate(reader):
#             if i == 0:
#                 pass
#             else:
#                 for r in row:
#                     print(r)
#                 # print(row)
#                 # print(row[0])
#                 # print(row[1])
#                 # print(row[2])


def process_users_csv(obj):
    csv_data = pd.read_csv(obj.file)
    print(csv_data.head())
    row_iter = csv_data.iterrows()
    objs = [
        User(
            email=row['email'],
            name=row['name'],
            password=make_password(row['password']),
        )
        for index, row in row_iter
    ]
    User.objects.bulk_create(objs, ignore_conflicts=True)


def upload_users(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save(commit=False)
            new_file.created_by = request.user
            new_file.save()
            process_users_csv(new_file)

            new_file.processed = True
            new_file.save()

            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "userListChanged": None,
                    "showMessage": f"bulk users added"
                })
            })
    else:
        form = FileUploadForm()
    return render(request, 'uploads/user_upload_form.html', {'form': form})


@staff_member_required
def all_uploads_list(request):
    if request.user.is_superuser:
        all_files = FileUpload.objects.all()
    else:
        all_files = FileUpload.objects.filter(created_by=request.user)
    paginator = Paginator(all_files, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'all_files': all_files,
        'page_obj': page_obj,
    }
    if request.htmx:
        return render(request, 'uploads/includes/all_files_list.html', context=context)
    return render(request, 'uploads/all_uploads.html', context=context)


@staff_member_required
def htmx_paginate_all_uploads(request):
    if request.user.is_superuser:
        all_files = FileUpload.objects.all()
    else:
        all_files = FileUpload.objects.filter(created_by=request.user)
    paginator = Paginator(all_files, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'all_files': all_files,
        'page_obj': page_obj,
    }
    return render(request, 'uploads/includes/all_files_loop.html', context=context)


@staff_member_required
@require_http_methods(['DELETE'])
def delete_uploaded_file(request, pk):
    file = get_object_or_404(FileUpload, pk=pk)
    file.delete()
    return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "fileListChanged": None,
                "showMessage": f"File deleted."
            })
        })