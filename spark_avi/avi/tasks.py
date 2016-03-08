'''
GAVIP Example AVIS: Spark AVI

This pipeline demonstrates how a job can be submitted to a Spark cluster
'''

import hashlib
import json
import logging
import operator
import os
import subprocess

# Class used for creating pipeline tasks
from pipeline.classes import AviTask, AviParameter, AviLocalTarget

from django.conf import settings

logger = logging.getLogger(__name__)

class RunSpark(AviTask):
    """
    Run one of the example Spark jobs
    """

    def __init__(self, *args, **kwargs):
        super(RunSpark, self).__init__(*args, **kwargs)
        param_values = 'TODO'
        self.output_file_prefix = hashlib.md5(param_values).hexdigest()
        logger.info('output_file_prefix: %s' % (self.output_file_prefix))

    def get_output_filename(self):
        return self.output_file_prefix + '_result'

    def output(self):
        return AviLocalTarget(os.path.join(settings.OUTPUT_PATH, self.get_output_filename()))

    def run(self):
        """
        Simple wordcount - TODO: add URL
        """
        logger.info('Running Spark Job')
        
        analysis_context = {'result': True,
                            }

        logger.debug(analysis_context)
        # JSON will be the context used for the template
        with open(self.output().path, 'wb') as out:
            json.dump(analysis_context, out)



