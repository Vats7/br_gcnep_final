from django.http import JsonResponse, HttpResponseBadRequest

from cms.models import Quiz


def ajax_quiz(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'GET':
            term = request.GET.get('term')
            all_quizzes = Quiz.objects.filter(title__icontains=term)
            response = list(all_quizzes.values())
            print(response)
            return JsonResponse(response, safe=False)#false bcoz JsonResponse needs a dict and we are pasiing list
        return JsonResponse({'status': 'Invalid request bcoz only GET is allowed '}, status=400)
    return HttpResponseBadRequest('Invalid request (only ajax allowed)')
