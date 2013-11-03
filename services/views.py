import json
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView
from django.views.generic.list import BaseListView, MultipleObjectMixin
from services.models import ServiceModel, ServiceGroupModel
from django.core import serializers
from libs.generic_views import GenericDeleteView, JsonRenderView, HybridDetailView, HybridListView, HybridCreateView, GenericJsonCreateOrEditView

#ServiceModel based views

class ServiceModelBaseView(object):
	""" Provides the base view for all service model based views """
	model = ServiceModel

class ServiceFormViewBase(ServiceModelBaseView):
	""" The base of AddView and EditView for ServiceModel """
	template_name = 'services/form.html'

class IndexView(HybridListView):
	""" Both the index and listview of ServiceModel """
	template_name = 'services/list.html'
	context_object_name = 'services'

	def get_queryset(self):
		return ServiceModel.objects.all()

class ServiceDelete(ServiceModelBaseView, GenericDeleteView, generic.base.View):
	""" Handles the deletion of a service """
	pass

class ServiceDetail(ServiceModelBaseView, HybridDetailView):
	""" The detailview of ServiceModel, where more info is shown """
	template_name = 'services/detail.html'
	context_object_name = 'service'

class ServiceAdd(ServiceFormViewBase, HybridCreateView):
	""" The view that shows a new form for ServiceModel """
	pass

class ServiceEdit(ServiceFormViewBase, generic.edit.UpdateView):
	""" The view that allows the user to edit ServiceModel """
	pass

class ServiceJsonAddOrEdit(ServiceModelBaseView, GenericJsonCreateOrEditView, generic.base.View):
	""" Handles the adding or editing of a service model that came from a json post """
	def manipulate_data(self, field, data):
		if field is 'service_group':
			group = get_object_or_404(ServiceGroupModel, pk = data)
			return group
		else:
			return data

def ping_view(request, pk):
	""" Pings the health_url of a ServiceModel """
	service = get_object_or_404(ServiceModel, pk=pk)
	service.ping(force_ping = True)
	return redirect(reverse('services:index'))

#ServiceGroupModel based views

class ServiceGroupViewBase():
	""" Provides the base for all service group class views """
	model = ServiceGroupModel

class ServiceGroupFormViewBase(ServiceGroupViewBase):
	""" The base for ServiceGroupModel's AddView and EditView """
	template_name = 'service_groups/form.html'

class ServiceGroupAdd(ServiceGroupFormViewBase, generic.edit.CreateView):
	""" The new form view for ServiceGroupModel """
	pass

class ServiceGroupEdit(ServiceGroupFormViewBase, generic.edit.UpdateView):
	""" The edit view for ServiceGroupModel """
	pass

class ServiceGroupJsonAddOrEdit(ServiceGroupViewBase, GenericJsonCreateOrEditView, generic.base.View):
	""" Creates or edits a service group that was posted with json contents """
	pass

class ServiceGroupDetail(ServiceGroupViewBase, HybridDetailView):
	""" Gives the user more information about a ServiceGroupModel """
	template_name = 'service_groups/detail.html'
	context_object_name = 'service_group'

class ServiceGroupDelete(ServiceGroupViewBase, GenericDeleteView, generic.base.View):
	""" Handles the delete of service groups and their associated services """
	pass