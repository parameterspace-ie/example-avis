"""
All forms for the avi app
"""

from django.forms import ModelForm

from avi.models import NoisySpectraJob


class NoisySpectraJobForm(ModelForm):
    """
    Form used to start Ulysses jobs
    
    """
    class Meta:
        model = NoisySpectraJob
        exclude = ['request']
        
        