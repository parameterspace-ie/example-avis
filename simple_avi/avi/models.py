"""
GAVIP Example AVIS: Simple AVI

Django models used by the AVI pipeline
@req: REQ-0006
@comp: AVI Web System
"""

from django.db import models
from pipeline.models import AviJob


class DemoModel(AviJob):
    """
    This model is used to store the parameters for the AVI pipeline.
    Notice that it contains identical field names here as is the variables in
    the pipeline itself.

    An AviJob model must contain all fields required by the intended
    pipeline class (ProcessData) in this case.
    """
    query = models.CharField(max_length=1000)
    outputFile = models.CharField(default="", max_length=100)
    pipeline_task = "ProcessData"

    def get_absolute_url(self):
        return "%i/" % self.pk
