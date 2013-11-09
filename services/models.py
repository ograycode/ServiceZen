import datetime
import urllib2
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.forms import ModelForm
from django.core.urlresolvers import reverse

class ServiceGroupModel(models.Model):
    """
    ServiceGroupModel holds services, so that you can have more than
    one physical service per group, e.g. two databases
    """
    name = models.CharField(max_length = 250)

    def get_absolute_url(self):
        return reverse('services:index')

    def __unicode__(self):
        return self.name

    def get_fields(self):
        """ Fields which are allowed to be updated """
        return ['name']

class ServiceModel(models.Model):
    """ServiceModel is the base model for each service"""

    #attributes
    name            = models.CharField(max_length = 250)
    is_up           = models.BooleanField(default = False)
    url             = models.CharField(max_length = 250, null = True, blank = True)
    health_url      = models.CharField(max_length = 250, null = True, blank = True)
    is_refresh_on   = models.BooleanField(default = False)
    created_on      = models.DateTimeField(default = timezone.now())
    service_group   = models.ForeignKey(ServiceGroupModel, related_name='services')

    def get_fields(self):
        """ Fields which are allowed to be updated """
        return ['name', 'is_up', 'url', 'health_url', 'is_refresh_on', 'service_group']

    def ping(self, force_ping = False):
        """ Checks the health of a given service, and creates a history to log the response """
        if force_ping or self.is_refresh_on:
            response_to_log = None
            self.is_up = False
            try:
                contents = urllib2.urlopen(self.health_url)
                if self._is_service_ok(contents):
                    self.is_up = True
                    response_to_log = self._get_response_to_log(contents)
            except Exception, e:
                response_to_log = 'Unable to ping'
            self.save()
            self._create_history(response_to_log, self.is_up)

    def _is_service_ok(self, contents):
        """ Determines if a service is ok or not, returning a boolean """
        return (contents.getcode() == 200) 

    def _get_response_to_log(self, contents):
        """ Extracts the response that will be logged in the service's history """
        return contents.getcode()

    def _create_history(self, response, is_up):
        """ Creates a history of a given response to the ping """
        s = ServiceHistoryModel(response=response, is_up=is_up, service=self, created_on=timezone.now())
        s.save()

    def get_absolute_url(self):
        return reverse('services:detail', args=(self.pk,))

class ServiceHistoryModel(models.Model):
    """ServiceHistoryModel is the history tracker for a ServiceModel"""
    created_on  = models.DateTimeField(default = timezone.now())
    response    = models.CharField(max_length = 250, null=True, blank=True)
    is_up       = models.BooleanField(default = False)
    service     = models.ForeignKey(ServiceModel, related_name='history')

    class Meta:
        ordering = ['-created_on']
        get_latest_by = 'created_on'