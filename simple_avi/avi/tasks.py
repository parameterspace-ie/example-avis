"""
GAVIP Example AVIS: Simple AVI

An example AVI pipeline is defined here, consisting of three tasks:

- DummyTask - demonstrates dependencies, but does nothing
- DownloadData - uses services.gacs.GacsQuery to run ADQL queries in GACS(-dev)
- ProcessData - generates a simple scatter plot with Bokeh from the downloaded data
@req: REQ-0006
@comp: AVI Web System
"""

import os
import time
import json
import logging
from django.conf import settings


import matplotlib
# Run without UI
matplotlib.use('Agg')
import numpy as np
from astropy.table import Table
import pandas_profiling
import pandas as pd

# Class used for creating pipeline tasks
from pipeline.classes import (
    AviTask,
    AviParameter, AviLocalTarget,
)

logger = logging.getLogger(__name__)

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
    outputFile = AviParameter()

    def output(self):
        return AviLocalTarget(os.path.join(
            settings.OUTPUT_PATH, 'simulatedData_%s.vot' % self.outputFile
        ))

    def requires(self):
        return self.task_dependency(DummyTask)


class ProcessData(AviTask):
    """
    This function requires a DownloadData class to be run. 
    We will obtain GACS data in this way.

    Once we have this data, we parse the VOTable. Then we 
    present it using pandas.
    """
    query = AviParameter()
    outputFile = AviParameter()

    def output(self):
        return AviLocalTarget(os.path.join(
            settings.OUTPUT_PATH, self.outputFile
        ))

    def requires(self):
        return self.task_dependency(DownloadData)

    def run(self):

        """
        Analyses the VOTable file containing the GACS-dev query results
        """
        logger.info('Input VOTable file: %s' % self.input().path)
        t = Table.read(self.input().path, format='votable')
        df = pd.DataFrame(np.ma.filled(t.as_array()), columns=t.colnames)

        gaiamagcols=['dec', 'dec_error', 'dist', 'phot_g_mean_flux', 'phot_g_mean_mag', 'ra', 'source_id']
        gaiadf = df[gaiamagcols]

        profile = pandas_profiling.ProfileReport(gaiadf)

        analysis_context = {'gacs_dfdescription': gaiadf.describe().to_html(classes='table table-striped table-bordered table-hover'),
                            'pandas_profiling': profile.html}

        # logger.debug('analysis_context %s' % analysis_context)
        # JSON will be the context used for the template
        with open(self.output().path, 'wb') as out:
            json.dump(analysis_context, out)
