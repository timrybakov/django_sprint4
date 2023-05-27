from django.shortcuts import render


def tr_handler404(request, exception):
    """
    Обработка ошибки 404
    """
    return render(request, 'pages/404.html', status=404)


def tr_handler403(request, reason=''):
    """
    Обработка ошибки 403
    """
    return render(request, 'pages/403csrf.html', status=403)


def tr_handler500(request):
    """
    Обработка ошибки 500
    """
    return render(request, template_name='pages/500.html', status=500)
