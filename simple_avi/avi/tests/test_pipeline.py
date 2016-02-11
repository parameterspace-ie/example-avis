from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

import os
import time
import datetime

import avi.tasks as avi_tasks
from avi.models import DemoModel, TestModel

# Parameters used in several tests
TESTFILE = '/data/output/test.txt'
TMPTESTFILE = '/data/output/tmptest.txt'
NOW = str(datetime.datetime.now())


class PipelineTestCase(TestCase):

    """Base class for running pipeline tests"""

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/pipeline/tests')
        middleware = SessionMiddleware()
        middleware.process_request(self.request)
        self.request.session.save()

        if not os.path.exists(os.path.dirname(TESTFILE)):
            os.makedirs(os.path.dirname(TESTFILE))

        with open(TESTFILE, 'a') as f:
            f.write(NOW + '\n')
        time.sleep(1)

    def tearDown(self):
        del self.factory, self.request
        os.remove(TESTFILE)


class InstanceTest(TestCase):

    """Instantiate some really simple AviTasks"""

    def testBasic(self):
        dummy1 = avi_tasks.EmptyTask(1)
        dummy2 = avi_tasks.EmptyTask(2)
        dummy1b = avi_tasks.EmptyTask(1)

        self.assertNotEqual(dummy1, dummy2)
        self.assertEqual(dummy1, dummy1b)

    def testOneParameter(self):
        dummy_1 = avi_tasks.TaskWithParameter(1, 1)
        dummy_2 = avi_tasks.TaskWithParameter(1, 2)
        dummy_3 = avi_tasks.TaskWithParameter(2, 1)
        dummy_1b = avi_tasks.TaskWithParameter(1, 1)

        self.assertNotEqual(dummy_1, dummy_2)
        self.assertNotEqual(dummy_2, dummy_3)
        self.assertEqual(dummy_1, dummy_1b)


class RunTest(PipelineTestCase):

    """Run a really simple AviTask manually and using Luigi"""

    def testCreateFileNoPipe(self):
        time.sleep(1)
        now = str(datetime.datetime.now())

        dummy = avi_tasks.TaskAppendToFile(1, now, TESTFILE)
        dummy.run()

        # See if it worked!
        self.assertTrue(os.path.isfile(TESTFILE))
        with open(TESTFILE, 'r') as f:
            testline = f.readlines()[-1]
        self.assertEqual(testline.strip('\n'), now)

    def testCreateFilePipe(self):
        """
        No Test failures but no output method leads to the following
        error:
          File "/opt/gavip_avi/pipeline/tasks.py", line 58, in run_luigi
            complete_task(task)
          File "/opt/gavip_avi/pipeline/events.py", line 106, in complete_task
            pipeline_state.output = task.output().path
        AttributeError: 'list' object has no attribute 'path'
        ----
        This may not be the case anymore (dan)
        """
        time.sleep(1)
        tmp_test_file = "%s.pipetest" % TESTFILE # WTF. HOW IS THIS FILE BEING MODIFIED?!
        # I RAN SPECIFICALLY THIS TEST, AND SOMETHING ELSE CHANGED THE FILE!
        # MODE=testing python manage.py test avi.tests.test_pipeline:RunTest.testCreateFilePipe
        # Go ahead.. Try it without adding .pipetest to the filename
        # Ahhh this test.. I don't know what I have done anymore.
        # Sorry to Author. Good luck fixing this mess.
        nowval = "xxx %s" % datetime.datetime.now()
        if os.path.exists(tmp_test_file):
            os.remove(tmp_test_file)
        job_model = TestModel.objects.create(now=nowval, testfile=tmp_test_file,
                                             pipeline_task="TaskAppendToFile")

        # Test if it worked!
        self.assertTrue(os.path.isfile(tmp_test_file))
        with open(tmp_test_file, 'r') as f:
            testcontent = f.readlines()
            testline = testcontent[-1]
        self.assertEqual(testline.strip('\n'), nowval)
        os.remove(tmp_test_file)



class OutputTest(PipelineTestCase):

    """Test AviTask with and without output method"""

    def test_with_output_task(self):
        time.sleep(1)
        now = str(datetime.datetime.now())

        job_model = TestModel.objects.create(now=now, testfile=TESTFILE,
                                             pipeline_task="TaskOutput")

        # Test if it worked!
        self.assertTrue(os.path.isfile(TESTFILE))
        with open(TESTFILE, 'r') as f:
            testline = f.readlines()[-1]
        self.assertNotEqual(testline.strip('\n'), now)

    def test_without_output_task(self):
        time.sleep(1)
        now = str(datetime.datetime.now())

        job_model = TestModel.objects.create(now=now, testfile=TMPTESTFILE,
                                             pipeline_task="TaskOutput")

        # Test if it worked!
        self.assertTrue(os.path.isfile(TMPTESTFILE))
        with open(TMPTESTFILE, 'r') as f:
            testline = f.readlines()[-1]
        self.assertEqual(testline.strip('\n'), now)
        time.sleep(1)
        os.remove(TMPTESTFILE)


class CurrentTasksTest(PipelineTestCase):

    """Test the tasks which run in the AVI template"""

    def test_process_data(self):
        query = "SELECT DISTANCE(POINT('ICRS',alpha,delta), POINT('ICRS',266.41683,-29.00781)) AS dist, * FROM public.g10_mw  WHERE 1=CONTAINS(POINT('ICRS',alpha,delta),CIRCLE('ICRS',266.41683,-29.00781, 0.08333333)) ORDER BY dist ASC"
        outputFile = 'test'

        job_model = DemoModel.objects.create(query=query,
                                             outputFile=outputFile)

        self.assertTrue(os.path.isfile('/data/output/dummyData_test.vot') and
                        os.path.isfile('/data/output/simulatedData_test.vot'))


class DependencyTest(PipelineTestCase):

    """Running AviTask which depends on another
    IMPORTANT: output method must exist and return a file which the run
    method creates
    """

    def test_dependent_task(self):
        time.sleep(1)
        now = str(datetime.datetime.now())

        job_model = TestModel.objects.create(now=now, testfile=TMPTESTFILE,
                                             pipeline_task="TaskDependent")

        # Test if it worked!
        self.assertTrue(os.path.isfile(TMPTESTFILE))
        with open(TMPTESTFILE, 'r') as f:
            testline = f.readlines()[-1]
        self.assertEqual(testline.strip('\n'), now)
        time.sleep(1)
        os.remove(TMPTESTFILE)
