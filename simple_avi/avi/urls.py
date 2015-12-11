"""
GAVIP Example AVIS: Simple AVI

These URLs are used by the AVI web-interface.
"""
from django.conf.urls import patterns, url
from avi import views

urlpatterns = patterns(
    '',
    url(r'^$', views.main, name='main'), # note: these urls are prefixed with /avi/

    url(r'^run_query/$',
        views.run_query, name='run_query'),
    
    url(r'^job_list/$',
        views.job_list, name='job_list'),
    
    url(r'^job_data/(?P<job_id>[0-9]+)/$',
        views.job_data, name='job_data'),

    url(r'^result/(?P<job_id>[0-9]+)/$',
        views.job_result, name='job_result'),
    
    url(r'^public/result/(?P<job_id>[0-9]+)/(?P<celery_task_id>[a-z0-9-]+)/$',
        views.job_result_public, name='job_result_public'),
)
