from django.shortcuts import redirect
from django.urls import reverse

class PreventLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.path in [reverse('login_page'), reverse('register')]:
                return redirect(reverse('profile'))

        response = self.get_response(request)
        return response
