'''
GAVIP Example AVIS: Spark AVI

This pipeline demonstrates how a job can be submitted to a Spark cluster
'''
import hashlib
import json
import logging
import os
from operator import add
from random import random

# Classes used for creating pipeline tasks
from luigi.contrib.spark import PySparkTask
from pipeline.classes import AviTask, AviParameter, AviLocalTarget

from django.conf import settings

logger = logging.getLogger(__name__)

class RunSpark(AviTask, PySparkTask):
    """
    Runs an example Spark job. Note that multiple inheritance of both 
    AviTask and SparkSubmitTask/PySparkTask is required.

    'spark-submit' location is currently configured in /opt/gavip_avi/luigi.cfg,
    which should either:
    
    1) match a volume that is mounted to the Spark location when the AVI container is created

    or

    2) match a volume within the container (i.e. with a Spark template that builds on the Java template)
    """

    def __init__(self, *args, **kwargs):
        super(RunSpark, self).__init__(*args, **kwargs)
        # A typical Spark job will have multiple input parameters,
        # which can be used to generate a unique hash for the task outputs.
        # This simple task currently requires no parameters.
        param_values = 'SparkJob'
        self.output_file_prefix = hashlib.md5(param_values).hexdigest()
        logger.info('output_file_prefix: %s' % (self.output_file_prefix))

    def get_output_filename(self):
        return self.output_file_prefix + '_result'

    def output(self):
        return AviLocalTarget(os.path.join(settings.OUTPUT_PATH, self.get_output_filename()))
    
    def main(self, sc, *args):
        """
        Spark tasks implement a main() function, instead of the standard run() function used with AviTask.
        For now, print() calls should be made in this function, instead of using logger, as main() is 
        executed within Spark, outside of Django.

        Pi calculation, taken from examples/src/main/python/pi.py provided with Spark 1.6.0
        """
        print('Running Spark Job - Pi Calculation')
        
        partitions =  2
        n = 100000 * partitions

        def f(_):
            x = random() * 2 - 1
            y = random() * 2 - 1
            return 1 if x ** 2 + y ** 2 < 1 else 0

        count = sc.parallelize(range(1, n + 1), partitions).map(f).reduce(add)
        calculated_pi = (4.0 * count / n)
        print("Calculated Pi is roughly %f" % calculated_pi)

        # JSON output for subsequent analysis
        spark_result = {'pi': calculated_pi}
        with open(self.output().path, 'wb') as out:
            json.dump(spark_result, out)

        print('Completed Spark Job, result: %s' % spark_result)



