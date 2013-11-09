from django.conf.urls import patterns, url
from services import views

urlpatterns = patterns('', 
    #/
    url(r'^$', views.IndexView.as_view(), name='index'),
    #/service/add
    url(r'^service/add/$', views.ServiceAdd.as_view(), name='add'),
    #/service/add/format=json
    url(r'^service/add.json$', views.ServiceJsonAddOrEdit.as_view(), name='json_add'),
    #/service/4
    url(r'^service/(?P<pk>\d+)/$', views.ServiceDetail.as_view(), name='detail'),
    #/service/4/edit
    url(r'^service/(?P<pk>\d+)/edit/$', views.ServiceEdit.as_view(), name='edit'),
    #/service/add/format=json
    url(r'^service/(?P<pk>\d+)/edit.json$', views.ServiceJsonAddOrEdit.as_view(), name='json_edit'),
    #/service/4/ping
    url(r'^service/(?P<pk>\d+)/ping/$', views.ping_view, name='ping'),
    #/service/4/delete
    url(r'^service/(?P<pk>\d+)/delete/$', views.ServiceDelete.as_view(), name='delete'),
    #/group/add
    url(r'^group/all/$', views.ServiceGroupList.as_view(), name='group_list'),
    #/group/add
    url(r'^group/add/$', views.ServiceGroupAdd.as_view(), name='group_add'),
    #/group/add/format=json
    url(r'^group/add.json$', views.ServiceGroupJsonAddOrEdit.as_view(), name='group_json_add'),
    #/group/4
    url(r'^group/(?P<pk>\d+)/$', views.ServiceGroupDetail.as_view(), name='group_detail'),
    #/group/4/edit
    url(r'^group/(?P<pk>\d+)/edit/$', views.ServiceGroupEdit.as_view(), name='group_edit'),
    #/group/4/edit/format=json
    url(r'^group/(?P<pk>\d+)/edit.json$', views.ServiceGroupJsonAddOrEdit.as_view(), name='group_json_edit'),
    #/group/4/delete
    url(r'^group/(?P<pk>\d+)/delete/$', views.ServiceGroupDelete.as_view(), name='group_delete'),
)