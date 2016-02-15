"""
GAVIP Example AVIS: Multiple Pipeline AVI

All Django view functions
"""

from collections import defaultdict
from itertools import chain
import json
import time
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.views.decorators.http import require_http_methods
from django.utils import formats

from pipeline import manager

from avi.forms import GacsIgslAnalysisJobForm, NoisySpectraJobForm
from avi.models import GacsIgslAnalysisJob, NoisySpectraJob

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_default_context():
    return {'gacsform': GacsIgslAnalysisJobForm(),
            'spectraform' : NoisySpectraJobForm()}


@require_http_methods(["GET"])
def index(request):
    """
    There are multiple pipelines in this AVI.
    By default, the index view contains the form where the user can specify the Run Ulysses parameters
    for the corresponding pipeline.
    
    We send a dictionary called a context, which contains 
    'millis' and 'standalone' variables.
    """
    context = get_default_context()
    context.update({
        "millis": int(round(time.time() * 1000)),
        "standalone": False, # This stops the base template rendering the navbar on top
        "show_welcome": request.session.get('show_welcome', True)
    })
    request.session['show_welcome'] = False
    
    return render(request, 'avi/index.html', context=context)


@require_http_methods(["POST"])
def run_ulysses(request):
    """
    Starts the Ulysses pipeline

    TODO - minor issue in rendering for invalid forms
    """
    logger.info('request.POST: %s', str(request.POST))

    form = NoisySpectraJobForm(request.POST)
        
    if form.is_valid():
        job_model = form.save()
        logger.info('Ulysses pipeline job has been successfully created')
    else:
        logger.error('Ulysses input parameters form is invalid')

    return redirect('%s#job-tab' % resolve_url('avi:index'))


@require_http_methods(["POST"])
def run_gacsigsl(request):
    """
    Starts the GACS-dev IGSL pipeline
    
    TODO - minor issue in rendering for invalid forms
    """
    logger.info('request.POST: %s', str(request.POST))

    form = GacsIgslAnalysisJobForm(request.POST)
    if form.is_valid():
        form.save()
        logger.info('IGSL pipeline job has been successfully created')
    else:
        logger.error('IGSL input parameters form is invalid')

    return redirect('%s#job-tab' % resolve_url('avi:index'))


@require_http_methods(["GET"])
def job_list(request):
    """
    This view is used to return all job progress
    """
    jsondata = defaultdict(list)
    for job in sorted(list(chain.from_iterable([NoisySpectraJob.objects.all(), GacsIgslAnalysisJob.objects.all()])), key=lambda j:j.request.created, reverse=True):
        jsondata['data'].append(serialize_job(job))
    return JsonResponse(jsondata)


def serialize_job(job):
    logger.debug('Will serialize job: %s' % job)
    logger.debug('last_active: %s' %formats.date_format(job.request.pipeline_state.last_activity_time, "SHORT_DATETIME_FORMAT"))
    data = {
        "job_id": job.request.job_id,
        "task_name": job.request.task_name,
        "created": formats.date_format(job.request.created, "SHORT_DATETIME_FORMAT"),
        "last_active": formats.date_format(job.request.pipeline_state.last_activity_time, "SHORT_DATETIME_FORMAT"),

        "result_path": job.request.result_path,
        "public_result_path": job.request.public_result_path,
        
        "state": job.request.pipeline_state.state,
        "progress": job.request.pipeline_state.progress,
        "exception": job.request.pipeline_state.exception,
    }
    return data


@require_http_methods(["GET"])
def job_result(request, job_id):
    file_path = manager.get_pipeline_status(job_id)['output']
    context = get_default_context()
    with open(file_path, 'r') as out_file:
        context.update(json.load(out_file))
    logger.info('Returning context: %s' % context)
    return render(request, 'avi/index.html', context=context)


@require_http_methods(["GET"])
def job_result_public(request, job_id, celery_task_id):
    """
    TODO: add support for both pipelines - currently only works for Ulysses pipelines
    """
    job = get_object_or_404(NoisySpectraJob, request_id=job_id)
    if celery_task_id == job.request.celery_task_id:
        return job_result(request, job_id)
    else:
        raise ObjectDoesNotExist("Invalid public URL")
        

@require_http_methods(["GET"])
def help_documentation(request):
    """
    Render AVI Help Documentation
    """
    return render(request, 'avi/help.html', context={})

