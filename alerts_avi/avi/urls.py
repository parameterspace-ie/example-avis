"""
GAVIP Example AVIS: Alerts AVI
"""
from avi import views, views_api
from plugins.urls import plugins_urls
from django.conf.urls import include, patterns, url
from rest_framework.urlpatterns import format_suffix_patterns


api_urls = [
    # API definitions
    url(r'^$',
        views_api.AlertsJobList.as_view(),
        name='alertsjob-list'),

    url(r'^(?P<pk>[0-9]+)/$',
        views_api.AlertsJobDetail.as_view(),
        name='alertsjob-detail'),

    url(r'^job_data/(?P<job_id>[0-9]+)/$',
        views_api.JobData.as_view(),
        name='api-job-data'),

    url(r'^view_jobs/$',
        views_api.ViewJobsList.as_view(),
        name='api-view-jobs'),

    url(r'^view_jobs/(?P<pk>[0-9]+)/$',
        views_api.ViewJobsListDetail.as_view(),
        name='api-view-jobs-detail'),

]

api_urls = format_suffix_patterns(api_urls)

urlpatterns = patterns(
    '',
    url(r'^$',
        views.main,
        name='main'),

    url(r'^api/',
        include(api_urls,
        namespace='api')),


    url(r'^job_list/',
        include(plugins_urls,
        namespace='plugins')),

    url(r'^run_query/$',
        views.run_query,
        name='run_query'),

    # url(r'^job_data/(?P<job_id>[0-9]+)/$',
    #     views.job_data,
    #     name='job_data'),

    url(r'^result/(?P<job_id>[0-9]+)/$',
        views.job_result,
        name='job_result'),

    url(r'^public/result/(?P<job_id>[0-9]+)/(?P<celery_task_id>[a-z0-9-]+)/$',
        views.job_result_public,
        name='job_result_public'),

    url(r'^view_for_checking_auth/$',
        views.view_for_checking_auth,
        name='view_for_checking_auth'),
)
