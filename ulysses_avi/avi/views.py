from collections import defaultdict
import json
import time
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.views.decorators.http import require_http_methods
from django.utils import formats

from pipeline import manager

from avi.forms import NoisySpectraJobForm
from avi.models import NoisySpectraJob

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def index(request):
    """
    For this Ulysses AVI, there is a single "Run Ulysses" pipeline that encapsulates a single
    execution based on an example from the README.
    Therefore, the index view contains the form where the user can specify the run parameters.
    
    We send a dictionary called a context, which contains 
    'millis' and 'standalone' variables.
    """
    context = {
        "millis": int(round(time.time() * 1000)),
        "standalone": False, # This stops the base template rendering the navbar on top
        "show_welcome": request.session.get('show_welcome', True)
    }
    request.session['show_welcome'] = False
    
    logger.info('Request method: ' + request.method)
    if request.method == 'POST':
        logger.info('request.POST: %s', str(request.POST))

        form = NoisySpectraJobForm(request.POST)
        
        if form.is_valid():
            job_model = form.instance
            
        job_task = manager.create_avi_job_task(request, job_model, 'AnalyseUlyssesOutput')
        # Start the pipeline
        manager.start_avi_job(job_task.job_id)

        return redirect('%s#job-tab' % resolve_url('avi:index'))

    else:
        form = NoisySpectraJobForm()
        context['form'] = form
        return render(request, 'avi/index.html', context=context)


@require_http_methods(["GET"])
def job_list(request):
    """
    This view is used to return all job progress
    """
    jobs = NoisySpectraJob.objects.all()
    jsondata = defaultdict(list)
    for job in jobs:
        logger.debug('Found job in db: %s' % job)
        jsondata['data'].append(serialize_job(job))
    return JsonResponse(jsondata)


def serialize_job(job):
    logger.debug('Will serialize job: %s' % (str(job)))
    logger.debug('last_active: %s' %formats.date_format(job.request.pipeline_state.last_activity_time, "SHORT_DATETIME_FORMAT"))
    data = {
        "job_id": job.request.job_id,
        "created": formats.date_format(job.request.created, "SHORT_DATETIME_FORMAT"),
        "last_active": formats.date_format(job.request.pipeline_state.last_activity_time, "SHORT_DATETIME_FORMAT"),

        "result_path": job.request.result_path,
        "public_result_path": job.request.public_result_path,
        
        "state": job.request.pipeline_state.state,
        "progress": job.request.pipeline_state.progress,
        "exception": job.request.pipeline_state.exception,
        "dependency_graph": job.request.pipeline_state.dependency_graph
    }
    return data


@require_http_methods(["GET"])
def job_data(request, job_id):
    file_path = manager.get_pipeline_status(job_id)['result']
    with open(file_path, 'r') as out_file:
        analysis_context = json.load(out_file)
    analysis_context['testfield'] = 'TEST'
    logger.info('analysis_context XXX: %s' % (analysis_context))
#     return JsonResponse(analysis_context)
    return render(request, 'avi/index.html', context=analysis_context)
#     return redirect('%s#result-tab' % resolve_url('avi:index'))


@require_http_methods(["GET"])
def job_result(request, job_id):
    return render(request, 'avi/job_result.html', {'job_id': job_id})


@require_http_methods(["GET"])
def job_result_public(request, job_id, celery_task_id):
    """
    @req: REQ-0035
    @comp: AVI Authentication and Authorization
    """
    job = get_object_or_404(NoisySpectraJob, request_id=job_id)
    if celery_task_id == job.request.celery_task_id:
        return job_result(request, job_id)
    else:
        raise ObjectDoesNotExist("Invalid public URL")
        

@require_http_methods(["GET"])
def help_documentation(request):
    """
    Ulysses AVI Help Documentation
    """
    return render(request, 'avi/help.html', context={})

