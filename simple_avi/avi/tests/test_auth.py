from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


def failed_auth(self, response):
    # Status code
    self.assertEqual(response.status_code, 403)
    # Context
    self.assertIn('csrf_token',
                  response.context)
    self.assertIn('user',
                  response.context)
    self.assertIn('perms',
                  response.context)
    self.assertIn('DEFAULT_MESSAGE_LEVELS',
                  response.context)
    self.assertIn('messages',
                  response.context)
    self.assertIn('request',
                  response.context)
    # Templates
    self.assertTemplateUsed(response,
                            'avi_auth/not_authorised.html')
    self.assertTemplateUsed(response,
                            'base/base.html')
    self.assertTemplateUsed(response,
                            'base/head.html')

    # Content
    self.assertIn('src="/static/base/img/sad_gaia.png"',
                  response.content)
    self.assertIn('<h4>Access Denied</h4>',
                  response.content)


class AuthTestCase(TestCase):

    # Mocking up a user
    def setUp(self):
        self.user = User.objects.create_user(
            username='username',
            email='exampleATemail.com',
            password='password'
        )

    def tearDown(self):
        self.user.delete()


class AuthMainPageSimpleTestcase(TestCase):
    """
    Testing that a developer can run an AVI in ``Standalone" mode such that there are no role retrictions

    @test: CU9-GAVIP-SYS-7-4

    @description
    In this test it is checked that a developer can create an environment mode for an AVI such that they can use it with no role restrictions.

    @input
    None

    @output
    None

    @purpose
    The purpose of this test is to ensure that developers can restrict their AVIs by role, but work locally without any restrictions if they want.

    @items
    AVI framework

    @pass_criteria
    The AVI works with no role.

    @procedure
    A testing AVI with views restricted to some roles is used
    An environment mode is set so that roles are ignored
    It is checked that the AVI can be used with no user roles
    """
    # Simple test, checking that everything works fine
    # when tests are run with STANDALONE=True

    def setUp(self):
        settings.STANDALONE = True

    def test_main_page_is_ok_200_simple(self):
        response = self.client.get(reverse('avi:main'))
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        settings.STANDALONE = True


class AuthMainPageTestcase(TestCase):
    """
    Testing that a developer can run an AVI such that there are role retrictions

    @test: CU9-GAVIP-SYS-7-4

    @description
    In this test it is checked that a developer can create an environment mode for an AVI such that role restrictions are put in place.

    @input
    None

    @output
    None

    @purpose
    The purpose of this test is to ensure that developers can restrict their AVIs by role.

    @items
    AVI framework

    @pass_criteria
    The AVI does not work with no role, and works with a user who has a role.

    @procedure
    A testing AVI with views restricted to some roles is used
    An environment mode is set so that roles are not ignored
    It is checked that the AVI can not be used with no user roles
    It is checked that the AVI can be used by a user with appropriate roles
    """
    # The same test as above but with
    # STANDALONE=False

    def setUp(self):
        settings.STANDALONE = False

    def test_main_page_auth(self):
        response = self.client.get(reverse('avi:main'))

        failed_auth(self, response)
        # More content
        self.assertIn('<strong>Not logged in</strong>',
                      response.content)

    # The same test as above but with
    # a user_profile to give a token

    def test_main_page_with_token_auth(self):
        # Logging a user in and creating a session to get a token
        # and a role
        self.client.login(username='username',
                          password='password')

        session = self.client.session
        session['user_profile'] = {"roles": ["Scientist"]}
        session.save()

        response = self.client.get(reverse('avi:main'))
        #Status code
        self.assertEqual(response.status_code, 200)
        # Context
        self.assertIn('millis',
                      response.context)
        self.assertIn('standalone',
                      response.context)
        self.assertTrue(response.context['show_welcome'])
        self.assertFalse(response.context['standalone'])
        # Templates
        self.assertTemplateUsed(response,
                                'avi/main.html')
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
        # Content
        self.assertIn('Simple AVI', response.content)
        self.assertIn('SampleFile_%s.out' % response.context['millis'],
                      response.content)

    def tearDown(self):
        settings.STANDALONE = True


class BadRoleViewTestCase(AuthTestCase):
    """
    A user with the wrong role trying to access a resticted AVI view

    @test: CU9-GAVIP-SYS-7-6

    @description
    In this test users with inappropriate roles attempts to access an AVI view that is restricted

    @input
    None

    @output
    None

    @purpose
    The purpose of this test is to ensure that users cannot access AVI views that a developer has not permitted
them to access.

    @items
    AVI framework

    @pass_criteria
    The user is redirected to the correct page and if they were not permitted to access the AVI view
an error message appears.

    @procedure
    A testing AVI with views restricted to some roles is used
    A test user with an inappropriate role is mocked up and logged in
    The user attempts to access the AVI views that are restricted
    It is checked that they were not successful
and that they received the correct error message
    """

    def setUp(self):
        settings.STANDALONE = False

    # The same test as above but with an anonymous user
    # to test the minimum avi role requirements
    def test_main_page_with_anon_auth(self):
        # Logging a user in and creating a session to get a token,
        # but we can still set the user role to be anonymous
        self.client.login(username='username',
                          password='password')

        session = self.client.session
        session['user_profile'] = {"roles": ["Anonymous"]}
        session.save()

        response = self.client.get(reverse('avi:main'))

        failed_auth(self, response)
        # More content
        self.assertIn('<strong>Insufficient permissions</strong>',
                      response.content)

    # Testing the simple view that was created and requires the
    # role of Operator. In this test a user with the role of
    # Outreach attempts and fails to access this view

    def test_view_for_auth_bad_role(self):
        self.client.login(username='username',
                          password='password')

        session = self.client.session
        session['user_profile'] = {"roles": ["Outreach"]}
        session.save()

        response = self.client.get(reverse('avi:view_for_checking_auth'))

        failed_auth(self, response)
        self.assertIn('<strong>Insufficient permissions</strong>',
                      response.content)

    def tearDown(self):
        settings.STANDALONE = True


class GoodRoleViewTestCase(AuthTestCase):
    """
    A user with the correct role trying to access a resticted AVI view

    @test: CU9-GAVIP-SYS-7-6

    @description
    In this test users with appropriate roles attempts to access an AVI view that is restricted

    @input
    None

    @output
    None

    @purpose
    The purpose of this test is to ensure that users can access AVI views that a developer has permitted them to access.

    @items
    AVI framework

    @pass_criteria
    The user is redirected to the correct page.

    @procedure
    A testing AVI with views restricted to some roles is used
    A test user with the appropriate roles is mocked up and logged in
    The user attempts to access the AVI views that are restricted
    It is checked that they were successful
    """
    # Testing the simple view that was created and requires the
    # role of Operator. In this test a user with the role of
    # Operator attempts and succeeds in accessing this view

    def setUp(self):
        settings.STANDALONE = False

    def test_view_for_auth_good_role(self):
        self.client.login(username='username',
                          password='password')

        session = self.client.session
        session['user_profile'] = {"roles": ["Operator"]}
        session.save()

        response = self.client.get(reverse('avi:view_for_checking_auth'))
        # Status code
        self.assertEqual(response.status_code, 200)
        # Context
        self.assertIn('csrf_token',
                      response.context)
        # Templates
        self.assertTemplateUsed(response,
                                'avi/view_for_checking_auth.html')
        # Content
        self.assertEqual('This is a test html, to figure out if' +
                         ' authentication that depends on roles is working.',
                         response.content)

    def tearDown(self):
        settings.STANDALONE = True
