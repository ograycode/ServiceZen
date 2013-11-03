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
				user = None
				token = None
				basic_auth = request.META.get('HTTP_AUTHORIZATION')

				if basic_auth:
					auth_method, auth_string = basic_auth.split(' ', 1)

					if auth_method.lower() == 'basic':
						auth_string = auth_string.strip().decode('base64')
						user, token = auth_string.split(':', 1)

				if not (user and token):
					try:
						json_request = json.loads(request.body)
						user = json_request['user']
						token = json_request['token']
					except Exception, e:
						print('Exception: ' + e.tostring)

				if user and token:
					user = authenticate(pk=user, token=token)
					if user:
						login(request, user)
						print('about to go in')
						return None
				else:
					return login_required(view_func)(request, *view_args, **view_kwargs)

		# Explicitly return None for all non-matching requests
		return None