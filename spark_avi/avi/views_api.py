"""
GAVIP Example AVIS: Spark AVI

REST AVI views
"""
import os
import json
import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, AdminRenderer

from pipeline import manager
from avi.models import SparkJob
from avi.serializers import SparkJobSerializer, ViewJobsSerializer

logger = logging.getLogger(__name__)

class SparkJobList(generics.ListCreateAPIView):
    queryset = SparkJob.objects.all()
    serializer_class = SparkJobSerializer
    renderer_classes = (JSONRenderer, AdminRenderer)


class SparkJobDetail(generics.RetrieveDestroyAPIView):
    queryset = SparkJob.objects.all()
    serializer_class = SparkJobSerializer
    renderer_classes = (JSONRenderer, AdminRenderer)


class JobResult(APIView):

    def get(self, request, job_id):
        """
        Returns the JSON result for a job.
        """
        file_path = manager.get_pipeline_status(job_id)['output']
        with open(file_path, 'r') as out_file:
            job_result = json.load(out_file)
        logger.info('Returning job_result: %s' % job_result)

        return Response(job_result)


class JobResultPublic(JobResult):

    def get(self, request, job_id, celery_task_id):
        """
        Returns the JSON result for a job. This is a public wrapper around the 
        standard job result view.
        """
        job = get_object_or_404(SparkJob, request_id=job_id)
        if celery_task_id == job.request.celery_task_id:
            return super(JobResultPublic, self).get(request, job_id)
        else:
            raise ObjectDoesNotExist("Invalid public URL")


class ViewJobsList(generics.ListAPIView):
    queryset = SparkJob.objects.all()
    serializer_class = ViewJobsSerializer
    renderer_classes = (JSONRenderer, AdminRenderer)


class ViewJobsListDetail(generics.RetrieveAPIView):
    queryset = SparkJob.objects.all()
    serializer_class = ViewJobsSerializer
    renderer_classes = (JSONRenderer, AdminRenderer)
