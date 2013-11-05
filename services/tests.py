import json
from django.test import TestCase
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from services.models import ServiceModel, ServiceGroupModel, ServiceHistoryModel

#Helper methods
def create_group(name = 'group1'):
	group = ServiceGroupModel(name=name)
	group.save()
	return group

def create_service(health_url='http://www.google.com/'):
	s = ServiceModel(name='service1', health_url=health_url, service_group=create_group())
	s.save()
	return s

def create_json_url(url):
	return url + '?format=json'

def standard_view_assertions(self, response):
	self.assertEqual(response.status_code, 200)

def create_user(user_name='john', user_password='johnpassword', email='lennon@thebeatles.com'):
	from django.contrib.auth.models import User
	user = None
	try:
		user = User.objects.get(pk = 1)
	except Exception, e:
		user = User.objects.create_user(user_name, email, user_password)
	user.save()
	return user

def login(self):
	user_name = 'john'
	user_password = 'johnpassword'
	user = create_user(user_name=user_name, user_password=user_password)
	self.client.login(username=user_name, password=user_password)

class ServiceHistoryModelTests(TestCase):
	def test_service_history_defaults(self):
		h = ServiceHistoryModel(response='none', service=create_service())
		h.save()
		self.assertEqual(h.is_up, False)

class ServiceModelTests(TestCase):

	def test_ping_success (self):
		s = create_service()
		s.ping(force_ping = True)
		self.assertEqual(s.is_up, True)

	def test_ping_failure (self):
		s = create_service(health_url='http://www.google.com/404')
		s.ping(force_ping = True)
		self.assertEqual(s.is_up, False)

	def test_force_ping (self):
		"""
		Tests the force_ping override of ServiceModel.ping
		ServiceModel.is_refresh_up defaults to false as does force_ping
		"""
		s = create_service()
		s.ping() #force_ping defaults to false
		self.assertEqual(s.is_up, False) #assume google.com is up

	def test_service_history_is_created_after_ping(self):
		s = create_service()
		s.ping(force_ping = True)
		self.assertEqual(s.history.count(), 1)

	def test_get_absolute_url(self):
		s = create_service()
		self.assertEqual(s.get_absolute_url(), reverse('services:detail', args=(s.pk,)))

class ServiceViewTests(TestCase):

	def setUp(self):
		login(self)

	def test_index_with_no_services (self):
		response = self.client.get(reverse('services:index'))
		standard_view_assertions(self, response)
		self.assertContains(response, 'no services')
		self.assertQuerysetEqual(response.context['services'], [])

	def test_detail_view (self):
		s = ServiceModel(name = 'detailviewtest', service_group=create_group())
		s.save()
		response = self.client.get(reverse('services:detail', args=(s.pk,)))
		standard_view_assertions(self, response)
		self.assertContains(response, 'detailviewtest')

	def test_detail_with_no_history_view (self):
		s = ServiceModel(name = 'detailviewtest', service_group=create_group())
		s.save()
		response = self.client.get(reverse('services:detail', args=(s.pk,)))
		standard_view_assertions(self, response)
		self.assertContains(response, 'detailviewtest')
		self.assertContains(response, 'no history available')

	def test_detail_with_history_view (self):
		s = ServiceModel(name = 'detailviewtest', service_group=create_group())
		s.ping(force_ping = True)
		response = self.client.get(reverse('services:detail', args=(s.pk,)))
		standard_view_assertions(self, response)
		self.assertContains(response, 'detailviewtest')
		self.assertContains(response, 'Time')

	def test_form_view(self):
		response = self.client.get(reverse('services:add'))
		standard_view_assertions(self, response)

	def test_ping_view(self):
		s = create_service()
		response = self.client.get(reverse('services:ping', args=(s.pk,)), follow=True) #redirects to index page
		standard_view_assertions(self, response)
		self.assertContains(response, s.name)

	def test_delete_view(self):
		s1 = create_service()
		s2 = create_service()
		response = self.client.delete(reverse('services:delete', args=(s2.pk,)), follow=True)
		standard_view_assertions(self, response)
		try:
			ServiceModel.objects.get(id=s2.pk)
		except Exception, e:
			pass
		else: # pragma: no cover
			self.assertEqual(True, False) #if hit, service model was found, so fail the test

class ServiceJsonViewTests(TestCase):
	user = None
	token = None 

	def append_login_info(self, json_data):
		json_data = json.loads(json_data)
		json_data['user'] = self.user
		json_data['token'] = self.token
		return json.dumps(json_data)

	def setUp(self):
		if not(self.user and self.token):
			user_name = 'john'
			user_password = 'johnpassword'
			user = create_user(user_name=user_name, user_password=user_password)
			response = self.client.post('/token/new.json',
			content_type='application/x-www-form-urlencoded',
			data='username=' + user_name + '&password=' + user_password)
			json_response = json.loads(response.content)
			self.user = json_response['user']
			self.token = json_response['token']

	def test_index_with_no_services_json(self):
		response = self.client.get(create_json_url(reverse('services:index')))
		standard_view_assertions(self, response)
		self.assertEqual(response.content, '[]')

	def test_detail_view_json(self):
		s = create_service()
		url = create_json_url(reverse('services:detail', args=(s.pk,))) + '&user=' + str(self.user) + '&token=' + self.token
		response = self.client.get(url)
		jsonModelOriginal = serializers.serialize('json', [s])
		standard_view_assertions(self, response)
		self.assertEqual(jsonModelOriginal, response.content)

	def test_json_add(self):
		create_group()
		data = self.append_login_info('{"fields":{"name":"test", "service_group": 1}}')
		response = self.client.post(reverse('services:json_add'),
			content_type='application/json', 
			data=data)
		standard_view_assertions(self, response)
		json_response = json.loads(response.content)[0]
		self.assertEqual(json_response['pk'],1)
		self.assertEqual(json_response['fields']['name'], 'test')
		self.assertEqual(json_response['fields']['service_group'], 1)

	def test_json_edit(self):
		s = create_service()
		data = self.append_login_info('{"fields":{"name":"test"}}')
		response = self.client.post(reverse('services:json_edit', args=(s.pk,)),
			content_type='application/json',
			data=data)
		standard_view_assertions(self, response)
		json_response = json.loads(response.content)[0]
		self.assertEqual(json_response['fields']['name'], 'test')


class ServiceGroupModelTests(TestCase):
	def test_get_absolute_url(self):
		g = create_group()
		self.assertEqual(g.get_absolute_url(), reverse('services:index'))

class ServiceGroupViewTests(TestCase):

	def setUp(self):
		login(self)

	def test_list_view(self):
		s = create_service()
		g = s.service_group
		response = self.client.get(reverse('services:group_list'))
		standard_view_assertions(self, response)
		self.assertContains(response, g.name)

	def test_json_list_view(self):
		s = create_service()
		g = s.service_group
		response = self.client.get(create_json_url(reverse('services:group_list')))
		standard_view_assertions(self, response)
		self.assertContains(response, '"fields": {"name": "'+g.name+'"}')

	def test_form_view(self):
		response = self.client.get(reverse('services:group_add'))
		standard_view_assertions(self, response)

	def test_detail_view(self):
		s = create_service()
		group = s.service_group
		response = self.client.get(reverse('services:group_detail', args=(group.pk,)))
		standard_view_assertions(self, response)
		self.assertContains(response, s.name)
		self.assertContains(response, group.name)

	def test_json_edit(self):
		s = create_service()
		group = s.service_group
		group.name = 'changed'
		response = self.client.post(reverse('services:group_json_edit', args=(group.pk,)), 
			content_type='application/json', 
			data='{"fields":{"name":"changed"}, "pk":2}')
		standard_view_assertions(self, response)
		json_response = json.loads(response.content)
		self.assertEqual(json_response[0]['fields']['name'], group.name)
		self.assertEqual(json_response[0]['pk'], group.pk)

	def test_json_add(self):
		response = self.client.post(reverse('services:group_json_add'),
			content_type='application/json',
			data='{"fields":{"name":"changed"}, "pk":2}')
		standard_view_assertions(self, response)
		json_response = json.loads(response.content)
		self.assertEqual(json_response[0]['fields']['name'], 'changed')
		self.assertEqual(json_response[0]['pk'], 1)

	def test_delete_view(self):
		g1 = create_group()
		g2 = create_group()
		response = self.client.delete(reverse('services:group_delete', args=(g2.pk,)), follow = True)
		standard_view_assertions(self, response)
		self.assertEqual(ServiceGroupModel.objects.get(id=g1.pk).pk, g1.pk)
		try:
			ServiceGroupModel.objects.get(id=g2.pk)
		except Exception, e:
			pass
		else: # pragma: no cover
			self.assertEqual(True, False) #if hit, service group model was found, so fail the test