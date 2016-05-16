'''
GAVIP Example AVIS: Multiple Pipeline AVI

Forms for the pipeline job models
'''

from django.forms import ModelForm

from avi.models import GacsIgslAnalysisJob, NoisySpectraJob


class NoisySpectraJobForm(ModelForm):
    """
    Form used to start Ulysses jobs
    
    """
    class Meta:
        model = NoisySpectraJob
        exclude = ['request', 'expected_runtime']
        

class GacsIgslAnalysisJobForm(ModelForm):
    """
    Form used to start GACS-dev IGSL jobs
    
    """
    class Meta:
        model = GacsIgslAnalysisJob
        exclude = ['request', 'expected_runtime']
        