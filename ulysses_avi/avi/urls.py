from django.conf.urls import patterns, url
from avi import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
                       
    url(r'^job_list/$', views.job_list, name='job_list'),
                       
    # TODO: refactor this so that the public view is a framework function
    url(r'^job_data/(?P<job_id>[0-9]+)/$', views.job_data, name='job_data'),

    url(r'^result/(?P<job_id>[0-9]+)/$', views.job_result, name='job_result'),
    
    url(r'^public/result/(?P<job_id>[0-9]+)/(?P<celery_task_id>[a-z0-9-]+)/$',
        views.job_result_public, name='job_result_public'),

    url(r'^help/$', views.help_documentation, name='help'),
)
