'''
GAVIP Example AVIS: Multiple Pipeline AVI

Django URLs and their views
'''

from django.conf.urls import patterns, url
from avi import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^run_ulysses$', views.run_ulysses, name='run_ulysses'),
    url(r'^run_gacsigsl$', views.run_gacsigsl, name='run_gacsigsl'),
                       
    url(r'^job_list/$', views.job_list, name='job_list'),
                       
    url(r'^result/(?P<job_id>[0-9]+)/$', views.job_result, name='job_result'),
    
    url(r'^public/result/(?P<job_id>[0-9]+)/(?P<celery_task_id>[a-z0-9-]+)/$',
        views.job_result_public, name='job_result_public'),

    url(r'^help/$', views.help_documentation, name='help'),
)
