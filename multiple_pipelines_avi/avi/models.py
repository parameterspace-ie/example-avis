'''
GAVIP Example AVIS: Multiple Pipeline AVI

Django models used by the AVI pipelines
'''


from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from pipeline.models import AviJob


class NoisySpectraJob(AviJob):

    """
    Model to be used for recording Ulysses parameters
    """

    # TODO: add validators
    spectra_input = models.CharField(max_length=100, default='data/input/marcs/*LR.spectra')
    wavelength_input = models.CharField(max_length=100, default='data/input/wavelengthLR.dat')
    num_noisy_spectra = models.IntegerField(default=1)
    MAX_GMAG = 20.0
    MIN_GMAG = 1.0
    g_mag = models.FloatField(default=17.0, validators = [MinValueValidator(MIN_GMAG), MaxValueValidator(MAX_GMAG)])
    extinction = models.IntegerField(default=1)
    oversampling = models.IntegerField(default=1)
    conversion = models.IntegerField(default=2)
    pipeline_task = "AnalyseUlyssesOutput"

    def __unicode__(self):              # __unicode__ on Python 2
        return 'Noisy Spectra Job: spectra input: %s, wavelength input: %s, number of noisy spectra: %d, G Mag: %.2f, extinction: %d, oversampling: %d, conversion: %d, state: %s' \
                                    % (self.spectra_input, 
                                       self.wavelength_input, 
                                       self.num_noisy_spectra,
                                       self.g_mag,
                                       self.extinction,
                                       self.oversampling,
                                       self.conversion,
                                       self.request.pipeline_state.state)




class GacsIgslAnalysisJob(AviJob):

    """
    Model to be used for recording GACS IGSL Query parameter
    """

    # TODO: add validators
    query = models.CharField(max_length=500, default="select top 100000 * from public.igsl_source where aux_ogle = 'True' and rand(1) <= 0.1;")
    pipeline_task = "AnalyseGacsIgslOutput"

    def __unicode__(self):              # __unicode__ on Python 2
        return 'GACS IGSL Analysis Job: query: %s, state: %s' \
                                    % (self.query, 
                                       self.request.pipeline_state.state)
