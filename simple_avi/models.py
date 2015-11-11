from django.db import models
from pipeline.models import AviJob


class DemoModel(AviJob):
    """
    This model is used to store the parameters for our pipeline.
    Notice that we have identical variable names here as is in
    the pipline itself.

    An AviJob model must contain all fields required by the intended
    pipeline class (ProcessData) in this case.
    """
    query = models.CharField(max_length=1000)
    outputFile = models.CharField(default="", max_length=100)
