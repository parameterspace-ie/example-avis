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
import logging

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods

from pipeline import manager
from avi.models import DemoModel
# from gavip_avi.decorators import require_gavip_role  # use this to restrict access to views in an AVI

logger = logging.getLogger(__name__)

def get_default_context():
    """
    'millis' is used to populate an output file name parameter
    'standalone' is used to show a convenient toolbar for users
    """ 
    return {
        "millis": int(round(time.time() * 1000)),
        "standalone": settings.STANDALONE # STANDALONE will be true in this case
    }


@require_http_methods(["GET"])
def index(request):
    """
    This view is the first view that the user sees
    We send a dictionary called a context, which contains 
    'millis' and 'standalone' variables.
    """
    return render(request, 'avi/index.html', context=get_default_context())


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
    outfile = request.POST["outfile"]
    adql_query = request.POST["query"]

    job_model = DemoModel.objects.create(
        query=adql_query,
        outputFile=outfile
    )
    job_task = manager.create_avi_job_task(request, job_model, "ProcessData")

    manager.start_avi_job(job_task.job_id)

    return redirect('avi:job_page', job_id=job_task.job_id)


@require_http_methods(["GET"])
def job_detail(request, job_id):
    """
    This view is used to show a job progress window using a job ID
    """
    job = get_object_or_404(DemoModel, request_id=job_id)
    context=get_default_context()
    context['job'] = job
    return render(request, 'avi/job_progress.html', context=context)


@require_http_methods(["GET"])
def job_status(request, job_id):
    """
    This view returns a JSON job status to JavaScript in the browser.
    We can use that to update a progress bar. 
    """
    get_object_or_404(DemoModel, request_id=job_id)
    status_data = manager.get_pipeline_status(job_id)
    return JsonResponse(status_data)


@require_http_methods(["GET"])
def job_summary(request, job_id):
    """
    This view is used when a job is complete to give some 
    detail of the results themselves, as well as provide 
    a button to view the results.
    """
    job = get_object_or_404(DemoModel, request_id=job_id)
    # Create the result context
    file_path = os.path.join(settings.OUTPUT_PATH, job.outputFile)
    file_size = float(os.path.getsize(file_path)) / 1048576
    file_mod_time = time.ctime(os.path.getmtime(file_path))

    # include the URL for the final job
    result_url = reverse('avi:job_result',
                         kwargs={'job_id': job_id})
    context = get_default_context()
    context.update({
        'resultURL': result_url,
        'filePath': file_path,
        'fileSize': file_size,
        'fileModTime': file_mod_time
    })
    return render(request, 'avi/job_summary.html', context=context)


@require_http_methods(["GET"])
def job_result(request, job_id):
    job = get_object_or_404(DemoModel, request_id=job_id)
    # The output file of our job is a file containing a bokeh plot
    # So open the file, and extract the content.
    file_path = os.path.join(settings.OUTPUT_PATH, job.outputFile)
    with open(file_path, 'r') as outFile:
        file_content = outFile.read()
    context=get_default_context()
    context['bokehPlot'] = file_content
    return render(request, 'avi/job_result.html', context=context)


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
