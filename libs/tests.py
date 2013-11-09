from django.test import TestCase
from login_required_middleware import RequireLoginMiddleware

class GetParamsMock(object):

    def __init__(self, parent_request):
        self.parent_request = parent_request

    def get(self, string):
        if string == 'user':
            return self.parent_request.user
        elif string == 'token':
            return self.parent_request.token
        return None
        
class RequestMock(object):
    def __init__(self, method):
        self.method = method
        self.user = 'user1'
        self.token = 'token1'
        self.body = '{"user":"'+self.user+'", "token": "'+self.token+'"}'
        self.GET = GetParamsMock(self)

class LoginRequredMiddlewareTests(TestCase):

    def assert_user_and_token_found_on(self, method):
        request = RequestMock(method)
        user_token_tuple = RequireLoginMiddleware()._get_api_user_and_token(request)
        self.assertEqual(user_token_tuple[0], request.user)
        self.assertEqual(user_token_tuple[1], request.token)

    def test_user_and_token_extraction(self):
        self.assert_user_and_token_found_on('GET')
        self.assert_user_and_token_found_on('POST')
        self.assert_user_and_token_found_on('PUT')
        self.assert_user_and_token_found_on('DELETE')