from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, AdminRenderer

from django.shortcuts import get_object_or_404
from django.conf import settings

from pipeline import manager
from avi.models import SparkJob
from avi.serializers import SparkJobSerializer, ViewJobsSerializer

import os
import json
import logging
logger = logging.getLogger(__name__)


# TODO: duplication

class SparkJobList(generics.ListCreateAPIView):
    queryset = SparkJob.objects.all()
    serializer_class = SparkJobSerializer
    renderer_classes = (JSONRenderer, AdminRenderer)


class SparkJobDetail(generics.RetrieveDestroyAPIView):
    queryset = SparkJob.objects.all()
    serializer_class = SparkJobSerializer
    renderer_classes = (JSONRenderer, AdminRenderer)


class JobData(APIView):

    def get(self, request, job_id):
        file_path = manager.get_pipeline_status(job_id)['output']
        job_data = get_default_context()
        with open(file_path, 'r') as out_file:
            job_data.update(json.load(out_file))
        logger.info('Returning job_data: %s' % job_data)

        return Response(job_data)


class ViewJobsList(generics.ListAPIView):
    queryset = SparkJob.objects.all()
    serializer_class = ViewJobsSerializer
    renderer_classes = (JSONRenderer, AdminRenderer)


class ViewJobsListDetail(generics.RetrieveAPIView):
    queryset = SparkJob.objects.all()
    serializer_class = ViewJobsSerializer
    renderer_classes = (JSONRenderer, AdminRenderer)
