"""
GAVIP Example AVIS: Alerts AVI
"""
import os
import datetime
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

from avi.models import AlertsJob
from gavip_avi.decorators import require_gavip_role  # use this to restrict access to views in an AVI
ROLES = settings.GAVIP_ROLES

from pipeline.models import AviJobRequest

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def main(request):
    """
    This view is the first view that the user sees
    We send a dictionary called a context, which contains 
    'millis' and 'standalone' variables.
    """
    context = {
        "today": datetime.datetime.today().strftime('%Y%m%d%H%M%S'),
        "standalone": False, # This stops the base template rendering the navbar on top
        "show_welcome": request.session.get('show_welcome', True)
    }
    request.session['show_welcome'] = False
    return render(request, 'avi/main.html', context)


@require_http_methods(["POST"])
def run_query(request):
    """
    This is called when the user submits their job parameters in
    their interface.

    We pull the parameters from the request POST parameters.

    We create an avi_job_request, which must be used to create
    the AlertsJob instance, so that the pipeline can excercise
    the pipeline correctly.

    We attach the job_request instance to th AlertsJob; this 
    extends the AviJob class, which is required for pipeline
    processing.

    We start the job using the job_request ID, and return the 
    ID to the user so they can view progress.
    """
    outfile = request.POST.get("outfile")

    job = AlertsJob.objects.create(
        outputFile=outfile
    )
    return JsonResponse({})


# def job_data(request, job_id):
#     job = get_object_or_404(AlertsJob, request_id=job_id)
#     file_path = os.path.join(settings.OUTPUT_PATH, job.outputFile)
#     with open(file_path, 'r') as outFile:
#         job_data = json.load(outFile)
#     # return JsonResponse(job_data)
#     raise Exception(job_data)
#     return render(request, 'avi/panel_result.html', {'out_data': job_data})

# def job_data(request, job_id):
#     job = get_object_or_404(AlertsJob, request_id=job_id)
#     file_path = os.path.join(settings.OUTPUT_PATH, job.outputFile)
#     with open(file_path, 'r') as outFile:
#         job_data = outFile.read()
#     return render_to_response('avi/_result.html', {'test_plot', job_data})

# @require_http_methods(["GET"])
# def job_data(request, job_id):
#     job = get_object_or_404(AlertsJob, request_id=job_id)
#     file_path = os.path.join(settings.OUTPUT_PATH, job.outputFile)
#     with open(file_path, 'r') as outFile:
#         # job_data = json.load(outFile)
#         job_data = outFile.read()
#     return render(request, 'avi/panel_result.html', {'job_data': job_data})


@require_http_methods(["GET"])
def job_result(request, job_id):
    job = get_object_or_404(AlertsJob, request_id=job_id)
    file_path = os.path.join(settings.OUTPUT_PATH, job.outputFile)
    with open(file_path, 'r') as outFile:
        # job_data = json.load(outFile)
        job_data = outFile.read()
    return render(request, 'avi/job_result.html', {'job_id': job_id, 'job_data': job_data})


@require_http_methods(["GET"])
def job_result_public(request, job_id, celery_task_id):
    """
    @req: REQ-0035
    @comp: AVI Authentication and Authorization
    """
    job = get_object_or_404(AlertsJob, request_id=job_id)
    if celery_task_id == job.request.celery_task_id:
        return job_result(request, job_id)
    else:
        raise ObjectDoesNotExist("Invalid public URL")


@require_gavip_role([ROLES.OP])
def view_for_checking_auth(request):
    """ A view for testing avi Authorization"""
    return render(request, 'avi/view_for_checking_auth.html')
