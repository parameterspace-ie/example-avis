"""
GAVIP Example AVIS: Alerts AVI
"""
import os
import logging

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from avi.models import AlertsJob

ROLES = settings.GAVIP_ROLES

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def job_result(request, job_id):
    job = get_object_or_404(AlertsJob, request_id=job_id)
    file_path = os.path.join(settings.OUTPUT_PATH, job.outputFile)
    with open(file_path, 'r') as outFile:
        # job_data = json.load(outFile)
        job_data = outFile.read()
    return render(request, 'avi/job_result.html', {'job_id': job_id,
                  'job_data': job_data})
