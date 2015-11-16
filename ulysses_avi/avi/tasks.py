'''
TODO:

This AVI demonstrates the following:



'''

import hashlib
import json
import logging
import matplotlib
# Run without UI
matplotlib.use('Agg')
import os
import pandas as pd
import shlex
import subprocess

# Class used for creating pipeline tasks
from pipeline.classes import AviTask, AviParameter, AviLocalTarget

from django.conf import settings

logger = logging.getLogger(__name__)

gog_gbin_prefixes = ['mdbcu5calphotfovtransit',
                      'UMSuperNova',
                      'mdbcu5calspecfovtransit',
                      'mdbcu5calphotsource']



class RunUlysses(AviTask):
    """
    TODO
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
    TODO
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
        return self.task_dependency(RunUlysses, [self.spectra_input, 
                                                self.wavelength_input,
                                                self.num_noisy_spectra,
                                                self.g_mag,
                                                self.extinction,
                                                self.oversampling,
                                                self.conversion, 
                                                self.output_file_prefix])

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
        logger.info('ProcessUlyssesOutput, input directory: %s' % self.input().path)
        
        df = pd.read_csv(os.path.join(self.input().path, 'Ulysses_GaiaBPRP_noiseFreeSpectra.txt'), skiprows=8, sep='|')
        logger.info(df.describe())
        
        analysis_context = {}
        analysis_context['dfdescription'] = df.describe().to_html(classes='table table-striped table-bordered table-hover')

        analysis_context['bprp_data'] = df[[' GBP ', ' GRP ' ]].values.tolist()
        logger.info(analysis_context)
        # JSON will be the context used for the template
        with open(self.output().path, 'wb') as out:
            json.dump(analysis_context, out)

