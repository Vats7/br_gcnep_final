import json
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from uploads.forms import FileUploadForm
import csv

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


