from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

import os
import time
import datetime

import avi.tasks as avi_tasks
from avi.models import DemoModel

from pipeline import manager
from pipeline.models import AviJobRequest


class CurrentTasksTest(TestCase):

    """Test the tasks which run in Simple AVI"""

    def test_process_data(self):
        query = "SELECT DISTANCE(POINT('ICRS',ra,dec), POINT('ICRS',266.41683,-29.00781)) AS dist, * FROM public.gaia_source  WHERE 1=CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',266.41683,-29.00781, 0.08333333)) ORDER BY dist ASC"
        outputFile = 'test'

        job_model = DemoModel.objects.create(query=query,
                                             outputFile=outputFile)

        self.assertTrue(os.path.isfile('/data/output/dummyData_test.vot') and
                        os.path.isfile('/data/output/simulatedData_test.vot') and
                        os.path.isfile('/data/output/test'))
