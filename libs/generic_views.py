import json
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView
from django.views.generic.list import BaseListView, MultipleObjectMixin
from services.models import ServiceModel, ServiceGroupModel
from django.core import serializers

#Generic views

class GenericDeleteView(object):
    """ 
    Implements a generic delete view to be inherited
    Note that the implementing class needs to declare it's model
    """
    def redirect_to(self):
        return reverse('services:index')

    def delete_obj(self, pk):
        obj = get_object_or_404(self.model, pk=pk)
        obj.delete()
        return redirect(self.redirect_to())

    def delete(self, request, pk):
        return self.delete_obj(pk)

    def get(self, request, pk):
        return self.delete_obj(pk)

class JsonRenderView(object):
    """ Renders a django model directly to json """
    def render_to_json(self, model_data):
        data = serializers.serialize('json', model_data)
        return HttpResponse(data, mimetype="application/json")

class HybridDetailView(JsonRenderView, SingleObjectTemplateResponseMixin, BaseDetailView):
    """ Provides a detail view that will also return json if requested """

    def render_to_response(self, context):
        if self.request.GET.get('format') == 'json':
            return self.render_to_json([self.get_object()])
        else:
            return super(HybridDetailView, self).render_to_response(context)

class HybridListView(JsonRenderView, generic.ListView, MultipleObjectMixin):
    """ Provides a list view that will return json if resquested """
    def render_to_response(self, context):
        if self.request.GET.get('format') == 'json':
            return self.render_to_json(self.get_queryset())
        else: 
            return super(HybridListView, self).render_to_response(context)

class HybridCreateView(generic.edit.CreateView):
    """ Create view place holder for when it will return json if requseted """
    pass

class GenericJsonCreateOrEditView(JsonRenderView):
    """ 
    A generic create or edit based upon post or put.
    Note that the implementing class needs to provide a model.
    The model must also provide a method called get_fields which
    returns a string array of fields that are allowed to be updated.
    """

    def put(self, request, pk=None):
        return self.post(request, pk)

    def post(self, request, pk=None):
        obj = None
        if pk is not None:
            obj = get_object_or_404(self.model, pk=pk)
        else:
            obj = self.model()
        json_data = json.loads(request.body)['fields']
        for field in obj.get_fields():
            if field in json_data:
                data = self.manipulate_data(field, json_data[field])
                setattr(obj, field, data)
        obj.save()
        return self.render_to_json([obj])

    def manipulate_data(self, field, data):
        """ 
        Is called before the attribute is set.
        Normally just returns the data, but if special handling is needed,
        overwrite this method and implement it.
        """
        return data;