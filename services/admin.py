from django.contrib import admin
from services.models import ServiceModel, ServiceGroupModel

admin.site.register(ServiceModel)
admin.site.register(ServiceGroupModel)