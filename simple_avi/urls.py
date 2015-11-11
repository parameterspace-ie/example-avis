"""
These URLs are used by the AVI web-interface.
"""
from django.conf.urls import patterns, url
from avi import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    # TODO: Check Django convention for using name of post in
    # "name" or "url" w.r.t duplication of var
    url(r'^run_query/$',
        views.run_query, name='run_query'),
    
    url(r'^job/(?P<job_id>[0-9]+)/$',
        views.job_detail, name='job_page'),
    
    url(r'^status/(?P<job_id>[0-9]+)/$',
        views.job_status, name='job_status'),
    
    url(r'^job_summary/(?P<job_id>[0-9]+)/$',
        views.job_summary, name='job_summary'),
    
    url(r'^result/(?P<job_id>[0-9]+)/$',
        views.job_result, name='job_result'),
    
    url(r'^public/result/(?P<job_id>[0-9]+)/(?P<celery_task_id>[a-z0-9-]+)/$',
        views.job_result_public, name='job_result_public'),
)
