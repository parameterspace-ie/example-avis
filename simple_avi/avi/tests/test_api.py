"""
@test: CU9-GAVIP-SYS-1-8
@test: CU9-GAVIP-SYS-5-2
"""

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
client = APIClient()

import os

from avi.models import DemoModel

Query = "SELECT DISTANCE(POINT('ICRS',alpha,delta), POINT('ICRS',266.41683,-29.00781)) AS dist, * FROM public.g10_mw  WHERE 1=CONTAINS(POINT('ICRS',alpha,delta),CIRCLE('ICRS',266.41683,-29.00781, 0.08333333)) ORDER BY dist ASC"
data = {'query': Query,
        'outputFile': 'foo.out', }


class DemoModelAPITest(APITestCase):

    def setUp(self):
        with open('/data/output/foobar.out', 'a') as f:
            f.write('{"foobar": [[1.0, 0.0], [1.1, 0.1]]}')

        job_model = DemoModel.objects.create(query=Query,
                                             outputFile='foobar.out')
        job_model_2 = DemoModel.objects.create(query=Query,
                                               outputFile="barfoo.out")

    def tearDown(self):
        DemoModel.objects.all().delete()

        os.remove('/data/output/foobar.out')

    def test_get_demomodel(self):
        """
        Checking api list of demomodels
        """

        url = reverse('avi:api:demomodel-list')

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(Query, response.content)
        self.assertIn('foobar.out', response.content)
        self.assertIn('barfoo.out', response.content)

    def test_create_demomodel(self):
        """
        Creating a new DemoModel object.
        """

        url = reverse('avi:api:demomodel-list')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(DemoModel.objects.count(), 3)
        self.assertEqual(DemoModel.objects.get(id=3).query, Query)
        self.assertEqual(DemoModel.objects.get(id=3).outputFile, 'foo.out')

        self.assertIn(Query, response.content)
        self.assertNotIn('foobar.out', response.content)
        self.assertIn('foo.out', response.content)

    def test_demomodel_detail_api(self):
        """
        Checking api detail of one demomodel.
        """

        url = reverse('avi:api:demomodel-detail', args=(1,))

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(Query, response.content)
        self.assertIn('foobar.out', response.content)
        self.assertNotIn('barfoo.out', response.content)

    def test_demomodel_detail_delete(self):
        """
        Deleting a DemoModel object.
        """

        self.assertEqual(DemoModel.objects.count(), 2)
        url = reverse('avi:api:demomodel-detail', args=(1,))

        response = self.client.delete(url)

        self.assertEqual(DemoModel.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_job_data(self):
        """
        Checking job data api
        """

        url = reverse('avi:api:api-job-data', args=(1,))

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # self.assertIn('[2.0,20263885.09694212]', response.content)

    def test_get_view_jobs(self):
        """
        Checking view jobs api
        """

        url = reverse('avi:api:api-view-jobs')

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(DemoModel.objects.get(id=1).request.result_path,
                      response.content)
        # Public result path commented out while the logic for public results
        # are being rewritten - Dan
        # self.assertIn(DemoModel.objects.get(id=2).request.public_result_path,
        #               response.content)

    def test_get_view_jobs_detail(self):
        """
        Checking view jobs detail api
        """

        url = reverse('avi:api:api-view-jobs-detail', args=(1,))

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(DemoModel.objects.get(id=1).request.result_path,
                      response.content)
        # self.assertNotIn(DemoModel.objects.get(id=2).request.public_result_path,
        #                  response.content)
