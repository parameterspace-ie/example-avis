'''
GAVIP Example AVIS: Spark AVI

Django models used by the AVI pipelines
'''


from django.db import models
from pipeline.models import AviJob


class SparkJob(AviJob):
    """
    Model to be used for recording Spark job parameters
    """
    pipeline_task = "RunSpark"

    def __unicode__(self):              # __unicode__ on Python 2
        return 'Spark Job: state: %s' % (self.request.pipeline_state.state)


