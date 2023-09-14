from django.test import TestCase
from django.shortcuts import reverse


class LandingPageTest(TestCase):

    def test_get(self):
        # TODO test response from landing page
        response = self.client.get(reverse('landing-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name="landing_page.html")