from django.conf.urls import patterns, url
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from accounts import views

urlpatterns = patterns('', 
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
)