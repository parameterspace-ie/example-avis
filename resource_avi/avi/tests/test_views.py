"""
@test: CU9-GAVIP-SYS-5-5
@test: CU9-GAVIP-SYS-5-7
"""
from django.test import TestCase
from avi.models import DemoModel
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

from pipeline.models import AviJobRequest, PipeState

import os

# Create your tests here.


class ModelAVIViewsTestcase(TestCase):
    """
    Testing the simple AVI views

    @test: CU9-GAVIP-SYS-5-8

    @description
    In this test an the views created by a developer for an AVI are checked to see if they are working as expected.

    @input
    None

    @output
    None

    @purpose
    The purpose of this test is to ensure that AVI developers can create their own page views with html, js and css styling.

    @items
    AVI framework

    @pass_criteria
    Views work as expected.

    @procedure
    A testing AVI with custom views is used
    It is tested that the correct results are returned
    """

    def setUp(self):
        settings.STANDALONE = True

        with open('/data/output/outputfile', 'a') as f:
            f.write('{"foobar": [[1.0, 0.0], [1.1, 0.1]]}')

        job_id = DemoModel.objects.create(
            query='query',
            outputFile='outputfile'
        ).id
        # After the object is created, celery will immediately
        # start processing the job. Changing it's data
        # So get it AGAIN after creation.
        self.job = DemoModel.objects.get(id=job_id)

    def tearDown(self):
        settings.STANDALONE = True

        os.remove('/data/output/outputfile')

        DemoModel.objects.all().delete()

    def test_main_page_is_ok_200(self):
        response = self.client.get(reverse('avi:index'))
        self.assertEqual(response.status_code, 200)

    def test_main_page_recieves_expected_context(self):
        response = self.client.get(reverse('avi:index'))

        self.assertIn('millis',
                      response.context)
        self.assertIn('standalone',
                      response.context)

    def test_main_page_returns_expected_content(self):
        response = self.client.get(reverse('avi:index'))

        self.assertTemplateUsed(response,
                                'avi/index.html')
        self.assertTemplateUsed(response,
                                'base/base.html')
        self.assertTemplateUsed(response,
                                'avi/avi_welcome.html')
        self.assertTemplateUsed(response,
                                'avi/avi_sidenav.html')
        self.assertTemplateUsed(response,
                                'avi/panel_enter_query.html')
        self.assertTemplateUsed(response,
                                'avi/panel_job_list.html')
        self.assertTemplateUsed(response,
                                'avi/panel_result.html')
        self.assertTemplateUsed(response,
                                'avi/panel_help.html')

        self.assertIn('Simple AVI',
                      response.content)
        self.assertIn('SampleFile_%s.out' % response.context['millis'],
                      response.content)


class ModelAVIQueryViewsTestcase(TestCase):

    """
    Testing custom query for the simple AVI

    @test: CU9-GAVIP-SYS-5-7

    @description
    In this test an AVI user supplies custom parameters to the AVI once it is deployed in GAVIP.

    @input
    Custom parameters

    @output
    Expected results

    @purpose
    The purpose of this test is to ensure that AVI users can supply custom parameters to the AVI
once it is deployed in GAVIP.

    @items
    AVI framework

    @pass_criteria
    Custom parameters are supplied to the AVI and the expected outcome is reached.

    @procedure
    A testing AVI is used to send a custom query
    It is tested that the correct results are returned
    """

    def setUp(self):
        settings.STANDALONE = True

        with open('/data/output/outputfile', 'a') as f:
            f.write('{"foobar": [[1.0, 0.0], [1.1, 0.1]]}')

        job_id = DemoModel.objects.create(
            query='query',
            outputFile='outputfile'
        ).id
        # After the object is created, celery will immediately
        # start processing the job. Changing it's data
        # So get it AGAIN after creation.
        self.job = DemoModel.objects.get(id=job_id)

    def tearDown(self):
        settings.STANDALONE = True

        os.remove('/data/output/outputfile')

        DemoModel.objects.all().delete()


    def test_run_query_page_get_ok_200(self):
        # /avi/run_query/

        query = "SELECT DISTANCE(POINT('ICRS',ra,dec), POINT('ICRS',266.41683,-29.00781)) AS dist, * FROM public.gaia_source  WHERE 1=CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',266.41683,-29.00781, 0.08333333)) ORDER BY dist ASC"
        outputFile = 'SampleFile_1451901076099.out'

        response = self.client.post(reverse('avi:run_query'),
                                    {'query': query,
                                     'outfile': outputFile})
        # Status code
        self.assertEqual(response.status_code, 200)
        # Context
        self.assertIsNone(response.context)
        # Content
        self.assertEqual('{}',
                         response.content)

    def test_non_existent_job_pages_404(self):

        ## /avi/status/1000/
        resp_job_data = self.client.get(reverse('avi:job_data', args=(1000,)))
        self.assertEqual(resp_job_data.status_code, 404)

    def test_existing_job_pages_are_ok_200(self):

        self.job = DemoModel.objects.get()

        # /avi/job_list/
        resp_job_page = self.client.get(reverse('avi:plugins:jobrequest_list'))
        self.assertEqual(resp_job_page.status_code, 200)
        # /avi/job_data/###/
        resp_job_data = self.client.get(reverse('avi:job_data',
                                        args=(self.job.id,)))
        self.assertEqual(resp_job_data.status_code, 200)

        #/avi/result/###/
        resp_job_result = self.client.get(reverse('avi:job_result',
                                                  args=(self.job.id,)))
        self.assertEqual(resp_job_result.status_code, 200)

    def test_job_list_page_recieves_expected_context(self):

        # /avi/job_list/
        resp_job_page = self.client.get(reverse('avi:plugins:jobrequest_list'))
        self.assertIsNone(resp_job_page.context)

    def test_job_list_page_returns_expected_content(self):

        # /avi/job_list/
        resp_job_page = self.client.get(reverse('avi:plugins:jobrequest_list'))

        # No templates used to render the response

        self.assertIn(self.job.request.result_path,
                      resp_job_page.content)
        self.assertIn(self.job.request.pipeline_state.state,
                      resp_job_page.content)
        self.assertIn(self.job.request.public_result_path,
                      resp_job_page.content)
        self.assertIn('%s' % self.job.request_id,
                      resp_job_page.content)

        # reformatted_date = self.job.request.created.strftime('%m/%d/%Y %-I')
        # self.assertIn('%s' % reformatted_date,
        #               resp_job_page.content)

        self.assertIn('%s' % self.job.request.pipeline_state.progress,
                      resp_job_page.content)
        self.assertIn(self.job.request.pipeline_state.exception,
                      resp_job_page.content)

    def test_job_data_page_recieves_expected_context(self):

        self.job = DemoModel.objects.get()
        # /avi/job_data/###/
        resp_job_data = self.client.get(reverse('avi:job_data',
                                        args=(self.job.id,)))
        self.assertIsNone(resp_job_data.context)

    def test_job_data_page_returns_expected_content(self):

        # No templates used to render the response

        self.job = DemoModel.objects.get()
        response = self.client.get(reverse('avi:job_data',
                                           args=(self.job.id,)))
        self.assertIn('{"foobar":[[1.0,0.0],[1.1,0.1]]}',
                      response.content)

    def test_job_result_page_recieves_expected_context(self):

        self.job = DemoModel.objects.get()
        #/avi/result/###/
        resp_job_result = self.client.get(reverse('avi:job_result',
                                                  args=(self.job.id,)))
        self.assertIn('job_id',
                      resp_job_result.context)
        self.assertEqual('1',
                         resp_job_result.context['job_id'])

    def test_job_result_page_returns_expected_content(self):

        self.job = DemoModel.objects.get()
        response = self.client.get(reverse('avi:job_result',
                                           args=(self.job.id,)))

        self.assertTemplateUsed(response,
                                'avi/job_result.html')
        self.assertTemplateUsed(response,
                                'base/base.html')
        self.assertTemplateUsed(response,
                                'avi/panel_result.html')

        self.assertIn('GAVIP Example AVIs: Simple AVI'
                      + ' (Result %s)' % self.job.id,
                      response.content)
        self.assertIn('Result view help',
                      response.content)
