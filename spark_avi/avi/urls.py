"""
GAVIP Example AVIS: Spark AVI

These URLs are used by the AVI web-interface.
"""
from django.conf.urls import include, patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from plugins.urls import plugins_urls
from avi import views_api

api_urls = [
    # API definitions
    url(r'^$', views_api.SparkJobList.as_view(), name='sparkjob_list'),

    url(r'^(?P<pk>[0-9]+)/$', views_api.SparkJobDetail.as_view(), name='sparkjob_detail'),

    url(r'^view_jobs/$', views_api.ViewJobsList.as_view(), name='api_view_jobs'),

    url(r'^view_jobs/(?P<pk>[0-9]+)/$', views_api.ViewJobsListDetail.as_view(), name='api_view_jobs_detail'),
]

api_urls = format_suffix_patterns(api_urls)

urlpatterns = patterns(
    '',
    url(r'^api/', include(api_urls, namespace='api')),

    url(r'^job_list/', include(plugins_urls, namespace='plugins')),

    # URLs with the next two names are required
    url(r'^result/(?P<job_id>[0-9]+)/$', views_api.JobResult.as_view(), name='job_result'),

    url(r'^public/result/(?P<job_id>[0-9]+)/(?P<celery_task_id>[a-z0-9-]+)/$', views_api.JobResultPublic.as_view(), name='job_result_public'),
)
