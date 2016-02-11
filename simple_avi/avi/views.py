"""
GAVIP Example AVIS: Simple AVI

@req: SOW-FUN-010
@req: SOW-FUN-040
@req: SOW-FUN-046
@req: SOW-INT-001
@comp: AVI Web System

This is a simple example AVI which demonstrates usage of the GAVIP AVI framework

Here in views.py, you can define any type of functions to handle 
HTTP requests. Any of these functions can be used to create an 
AVI query from your AVI interface.
"""
import os
import time
import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.core import serializers
from django.utils import formats
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods

from pipeline import manager
from avi.models import DemoModel
# from gavip_avi.decorators import require_gavip_role  # use this to restrict access to views in an AVI

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def main(request):
    """
    This view is the first view that the user sees
    We send a dictionary called a context, which contains 
    'millis' and 'standalone' variables.
    """
    context = {
        "millis": int(round(time.time() * 1000)),
        "standalone": False, # This stops the base template rendering the navbar on top
        "show_welcome": request.session.get('show_welcome', True)
    }
    request.session['show_welcome'] = False
    return render(request, 'avi/index.html', context)


@require_http_methods(["POST"])
def run_query(request):
    """
    This is called when the user submits their job parameters in
    their interface.

    We pull the parameters from the request POST parameters.

    We create an avi_job_request, which must be used to create
    the DemoModel instance, so that the pipeline can excercise
    the pipeline correctly.

    We attach the job_request instance to th DemoModel; this 
    extends the AviJob class, which is required for pipeline
    processing.

    We start the job using the job_request ID, and return the 
    ID to the user so they can view progress.
    """
    outfile = request.POST.get("outfile")
    adql_query = request.POST.get("query")

    job_model = DemoModel.objects.create(
        query=adql_query,
        outputFile=outfile
    )
    job_task = manager.create_avi_job_task(request, job_model, "ProcessData")
    manager.start_avi_job(job_task.job_id)
    return JsonResponse({'job': job_task.job_id})


@require_http_methods(["GET"])
def job_list(request):
    """
    This view is used to return all job progress
    """
    jobs = DemoModel.objects.all()
    jsondata = {
        "data": []
    }
    for job in jobs:
        jsondata['data'].append(serialize_job(job))
    return JsonResponse(jsondata)


def serialize_job(job):
    logger.debug(job)
    data = {
        "job_id": job.request.job_id,
        "created": formats.date_format(job.request.created, "SHORT_DATETIME_FORMAT"),

        "result_path": job.request.result_path,
        "public_result_path": job.request.public_result_path,
        
        "state": job.request.pipeline_state.state,
        "progress": job.request.pipeline_state.progress,
        "exception": job.request.pipeline_state.exception,
        "dependency_graph": job.request.pipeline_state.dependency_graph,
        "completed": formats.date_format(job.request.pipeline_state.last_activity_time, "SHORT_DATETIME_FORMAT")
    }
    return data


@require_http_methods(["GET"])
def job_data(request, job_id):
    job = get_object_or_404(DemoModel, request_id=job_id)
    file_path = os.path.join(settings.OUTPUT_PATH, job.outputFile)
    with open(file_path, 'r') as outFile:
        job_data = json.load(outFile)
    return JsonResponse(job_data)


@require_http_methods(["GET"])
def job_result(request, job_id):
    return render(request, 'avi/job_result.html', {'job_id': job_id})


@require_http_methods(["GET"])
def job_result_public(request, job_id, celery_task_id):
    """
    @req: REQ-0035
    @comp: AVI Authentication and Authorization
    """
    job = get_object_or_404(DemoModel, request_id=job_id)
    if celery_task_id == job.request.celery_task_id:
        return job_result(request, job_id)
    else:
        raise ObjectDoesNotExist("Invalid public URL")
