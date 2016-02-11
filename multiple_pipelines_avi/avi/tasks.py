'''
GAVIP Example AVIS: Multiple Pipeline AVI

This pipeline demonstrates how (DPAC) tools written in Java may be called from AVI pipelines.
'''

from astropy.table import Table
import hashlib
import json
import logging
import matplotlib
# Run without UI
matplotlib.use('Agg')
import numpy as np
import operator
import os
import pandas as pd
import shlex
from sklearn.cluster import KMeans
import subprocess

# Class used for creating pipeline tasks
from pipeline.classes import AviTask, AviParameter, AviLocalTarget
from services.gacs import GacsQuery


from django.conf import settings

logger = logging.getLogger(__name__)


class RunUlysses(AviTask):
    """
    Runs Ulysses using parameters similar to an example in its README file.
    """
    spectra_input = AviParameter()
    wavelength_input = AviParameter()
    num_noisy_spectra = AviParameter()
    g_mag = AviParameter()
    extinction = AviParameter()
    oversampling = AviParameter()
    conversion = AviParameter()
    output_file_prefix = AviParameter()

    def get_output_filename(self):
        return self.output_file_prefix + '_ulyssesoutput'

    def output(self):
        return AviLocalTarget(os.path.join(settings.OUTPUT_PATH, self.get_output_filename()))

    def run(self):
        os.makedirs(self.output().path)
        ulysses_cmd = 'nice -n 19 java -jar dist/ulysses.jar -o %s -f "%s" -w %s -n %d -G %d -A %d -oversamp %d -conversion %d 2>&1' % (self.output().path,
                                                                                                                                        self.spectra_input, 
                                                                                                                                        self.wavelength_input, 
                                                                                                                                        self.num_noisy_spectra, 
                                                                                                                                        self.g_mag, 
                                                                                                                                        self.extinction, 
                                                                                                                                        self.oversampling, 
                                                                                                                                        self.conversion)
        logger.info('Ulysses command: %s' % ulysses_cmd)
        
        # CWD is currently assumed to exist - will be a shared host:container Docker volume
        fp = subprocess.Popen(shlex.split(ulysses_cmd), bufsize=-1, stdout=subprocess.PIPE, cwd='/opt/ulysses').stdout
        while True:
            line = fp.readline()
            if not line:
                break
            # Just log any output here
            logger.info(line.strip())
        

class AnalyseUlyssesOutput(AviTask):
    """
    Some cursory analysis of one of the Ulysses output files
    """
    spectra_input = AviParameter()
    wavelength_input = AviParameter()
    num_noisy_spectra = AviParameter()
    g_mag = AviParameter()
    extinction = AviParameter()
    oversampling = AviParameter()
    conversion = AviParameter()

    def __init__(self, *args, **kwargs):
        super(AnalyseUlyssesOutput, self).__init__(*args, **kwargs)
        param_values = '%s_%s_%d_%.2f_%d_%d_%d' % (self.spectra_input,
                                                   self.wavelength_input,
                                                   self.num_noisy_spectra,
                                                   self.g_mag,
                                                   self.extinction,
                                                   self.oversampling,
                                                   self.conversion)
        self.output_file_prefix = hashlib.md5(param_values).hexdigest()
        logger.info('output_file_prefix: %s' % (self.output_file_prefix))

    def get_output_filename(self):
        return self.output_file_prefix + '_analysed'

    def output(self):
        return AviLocalTarget(os.path.join(settings.OUTPUT_PATH, self.get_output_filename()))

    def requires(self):
        return self.task_dependency(RunUlysses, output_file_prefix=self.output_file_prefix)

    def run(self):
        """
        Expected Ulysses files in the output directory:
        
        Ulysses_GaiaBPRP_meanSpecWavelength.gbin
        Ulysses_GaiaBPRP_meanSpecWavelength.txt
        Ulysses_GaiaBPRP_noiseFreeSpectra.gbin
        Ulysses_GaiaBPRP_noiseFreeSpectra.txt
        Ulysses_GaiaBPRP_noisySpectra001.gbin
        Ulysses_GaiaBPRP_noisySpectra001.txt
        Ulysses_GaiaBPRP_UMPhoto.gbin
        """
        logger.info('input directory: %s' % self.input().path)
        
        df = pd.read_csv(os.path.join(self.input().path, 'Ulysses_GaiaBPRP_noiseFreeSpectra.txt'), skiprows=8, sep='|')
        logger.info(df.describe())
        
        # Create Highchart series and include it in the results context
        hc_series = [{
            'name': 'Noise Free Spectra',
            'showInLegend': False,
            'color': 'rgba(223, 83, 83, .5)',
            'data': df[[' GBP ', ' GRP ' ]].values.tolist()
        }]
        
        analysis_context = {'ulysses_result': True,
                            'ulysses_dfdescription': df.describe().to_html(classes='table table-striped table-bordered table-hover'),
                            'ulysses_hc_series': hc_series
                            }

        logger.debug(analysis_context)
        # JSON will be the context used for the template
        with open(self.output().path, 'wb') as out:
            json.dump(analysis_context, out)



class ExecuteQuery(GacsQuery):
    """
    Uses the AVI Framework GACS service to execute the query
    """
    query = AviParameter()
    output_file_prefix = AviParameter()

    def get_output_filename(self):
        return self.output_file_prefix + '_gacsoutput.vot'

    def output(self):
        return AviLocalTarget(os.path.join(settings.OUTPUT_PATH, self.get_output_filename()))


class AnalyseGacsIgslOutput(AviTask):
    """
    Some cursory analysis of the the VOTable output by GACS.
    """
    query = AviParameter()

    def __init__(self, *args, **kwargs):
        super(AnalyseGacsIgslOutput, self).__init__(*args, **kwargs)
        self.output_file_prefix = hashlib.md5(self.query).hexdigest()
        logger.info('output_file_prefix: %s' % (self.output_file_prefix))

    def get_output_filename(self):
        return self.output_file_prefix + '_analysed'

    def output(self):
        return AviLocalTarget(os.path.join(settings.OUTPUT_PATH, self.get_output_filename()))

    def requires(self):
        return self.task_dependency(ExecuteQuery, output_file_prefix=self.output_file_prefix)

    def run(self):
        """
        Analyses the VOTable file containing the GACS-dev query results
        """
        logger.info('Input VOTable file: %s' % self.input().path)
        t = Table.read(self.input().path, format='votable')
        df = pd.DataFrame(np.ma.filled(t.as_array()), columns=t.colnames)
        gaiamagcols=['mag_bj', 'mag_g', 'mag_grvs', 'mag_rf']
        gaiadf = df[gaiamagcols]
        cluster_pred = KMeans(n_clusters=4).fit_predict(gaiadf)
         
        # From colorbrewer2.org
        cluster_colours = {0:(123,50,148,.5),
                           1:(194,165,207,.5),
                           2:(166,219,160,.5),
                           3:(0,136,55,.5)}
        
        # Currently sampling 100 points per cluster to minimise highcharts Javascript activity in the template
        hc_series = [{'name': 'Cluster %d' % cluster, 'showInLegend': True, 'color':'rgba(%s)' % ','.join([str(x) for x in colour]), 'data':gaiadf[['mag_bj', 'mag_g']][cluster_pred==cluster].sample(n=100).values.tolist()} for cluster,colour in sorted(cluster_colours.iteritems(), key=operator.itemgetter(0))]
        analysis_context = {'gacs_result': True,
                            'gacs_dfdescription': gaiadf.describe().to_html(classes='table table-striped table-bordered table-hover'),
                            'gacs_hc_series': hc_series
                            }

        logger.debug(analysis_context)
        # JSON will be the context used for the template
        with open(self.output().path, 'wb') as out:
            json.dump(analysis_context, out)


