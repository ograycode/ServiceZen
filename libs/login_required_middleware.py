import re
import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login


class RequireLoginMiddleware(object):
    """
    Middleware component that wraps the login_required decorator around
    matching URL patterns. To use, add the class to MIDDLEWARE_CLASSES and
    define LOGIN_REQUIRED_URLS and LOGIN_REQUIRED_URLS_EXCEPTIONS in your
    settings.py. For example:
    ------
    LOGIN_REQUIRED_URLS = (
        r'/topsecret/(.*)$',
    )
    LOGIN_REQUIRED_URLS_EXCEPTIONS = (
        r'/topsecret/login(.*)$',
        r'/topsecret/logout(.*)$',
    )
    ------
    LOGIN_REQUIRED_URLS is where you define URL patterns; each pattern must
    be a valid regex.

    LOGIN_REQUIRED_URLS_EXCEPTIONS is, conversely, where you explicitly
    define any exceptions (like login and logout URLs).
    """
    def __init__(self):
        self.required = tuple(re.compile(url) for url in settings.LOGIN_REQUIRED_URLS)
        self.exceptions = tuple(re.compile(url) for url in settings.LOGIN_REQUIRED_URLS_EXCEPTIONS)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # No need to process URLs if user already logged in
        if request.user.is_authenticated():
            return None

        # An exception match should immediately return None
        for url in self.exceptions:
            if url.match(request.path):
                return None

        # Requests matching a restricted URL pattern are returned
        # wrapped with the login_required decorator
        for url in self.required:
            if url.match(request.path):
                user_token_tuple = self._get_api_user_and_token(request)
                user = user_token_tuple[0]
                token = user_token_tuple[1]

                if user and token:
                    user = authenticate(pk=user, token=token)
                    if user:
                        login(request, user)
                        return None
                    else: 
                        return login_required(view_func)(request, *view_args, **view_kwargs)
                else:
                    return login_required(view_func)(request, *view_args, **view_kwargs)

        # Explicitly return None for all non-matching requests
        return None

    def _get_api_user_and_token(self, request):
        user = None
        token = None

        if request.method == 'GET':
            user = request.GET.get('user')
            token = request.GET.get('token')
        else:
            try:
                json_params = json.loads(request.body)
                user = json_params['user']
                token = json_params['token']
            except Exception, e:
                pass
                
        return user, token