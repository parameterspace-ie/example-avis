"""
GAVIP Example AVIS: Alerts AVI

Django models used by the AVI pipeline
"""

from django.db import models
from pipeline.models import AviJob


class AlertsJob(AviJob):
    """
    This model is used to store the parameters for the AVI pipeline.
    Notice that it contains identical field names here as is the variables in
    the pipeline itself.

    An AviJob model must contain all fields required by the intended
    pipeline class (ProcessData) in this case.
    """
    outputFile = models.CharField(default="", max_length=100)
    pipeline_task = "PlotData"

    def get_absolute_url(self):
        return "%i/" % self.pk
