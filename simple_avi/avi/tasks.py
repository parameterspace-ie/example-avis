"""
GAVIP Example AVIS: Simple AVI

An example AVI pipeline is defined here, consisting of three tasks:

- DummyTask - demonstrates dependencies, but does nothing
- DownloadData - uses services.gacs.GacsQuery to run ADQL queries in GACS(-dev)
- ProcessData - generates a simple scatter plot with Bokeh from the downloaded data
"""

import os
import time
import json
from django.conf import settings

# Class used for creating pipeline tasks
from pipeline.classes import (
    AviTask,
    AviParameter, AviLocalTarget,
)

# Service enabling ADQL queries to be run in GACS(-dev)
# Queries are run asynchronously, but the service is restricted to anonymous users until ESAC CAS integration is possible.
import services.gacs as svc_gacs

# Library used for VOTable parsing
from astropy.io.votable import parse


class DummyTask(AviTask):
    """
    This is a sample task which has no dependencies. It only exists to further demonstrate dependency creation.
    """
    outputFile = AviParameter()

    def output(self):
        return AviLocalTarget(os.path.join(
            settings.OUTPUT_PATH, 'dummyData_%s.vot' % self.outputFile
        ))

    def run(self):
        time.sleep(3)
        with open(self.output().path, "w") as outFile:
            outFile.write("dummyStuff")


class DownloadData(svc_gacs.GacsQuery):
    """
    This task uses an AVI service, to obtain a data product from GACS.
    Notice that we do not define a 'run' function! It is defined by the 
    service class which we extend.

    See :class:`GacsQuery`
    """
    query = AviParameter()
    output_file = AviParameter()

    def output(self):
        return AviLocalTarget(os.path.join(
            settings.OUTPUT_PATH, 'simulatedData_%s.vot' % self.output_file
        ))

    def requires(self):
        return self.task_dependency(DummyTask, [self.output_file])


class ProcessData(AviTask):
    """
    This function requires a DownloadData class to be run. 
    We will obtain GACS data in this way.

    Once we have this data, we parse the VOTable. Then we 
    plot it using Bokeh.
    """
    query = AviParameter()
    outputFile = AviParameter()

    def output(self):
        return AviLocalTarget(os.path.join(
            settings.OUTPUT_PATH, self.outputFile
        ))

    def requires(self):
        return self.task_dependency(DownloadData, [self.query, self.outputFile])

    def run(self):
        # load the votable content from previous task
        votable = parse(self.input().path)
        data_arr = votable.get_first_table().array
        # Extract plot data
        mass = data_arr['mass']
        orbit_period = data_arr['orbit_period']
        
        # highcharts_data = zip(list_a, list_b)
        highcharts_data = {"data": map(lambda x,y:[x,y], mass, orbit_period)}

        with open(self.output().path, 'w') as out:
            json.dump(highcharts_data, out)
