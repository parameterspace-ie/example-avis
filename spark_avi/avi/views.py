"""
GAVIP Example AVIS: Spark AVI

Django view functions
"""

import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from django.utils import formats

from pipeline import manager

from avi.models import SparkJob

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_default_context():
    return {}


@require_http_methods(["GET"])
def job_result(request, job_id):
    """
    TODO: duplication
    """
    file_path = manager.get_pipeline_status(job_id)['output']
    context = get_default_context()
    with open(file_path, 'r') as out_file:
        context.update(json.load(out_file))
    logger.info('Returning context: %s' % context)
    return render(request, 'avi/index.html', context=context)


@require_http_methods(["GET"])
def job_result_public(request, job_id, celery_task_id):
    """
    TODO: duplication
    """
    job = get_object_or_404(SparkJob, request_id=job_id)
    if celery_task_id == job.request.celery_task_id:
        return job_result(request, job_id)
    else:
        raise ObjectDoesNotExist("Invalid public URL")
        


