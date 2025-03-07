from django.test import TestCase
from django.urls import reverse
from .models import YourModel  # Replace with your actual model

class AmmonizioniTests(TestCase):

    def setUp(self):
        # Set up any initial data for your tests here
        self.model_instance = YourModel.objects.create(field1='value1', field2='value2')  # Adjust fields as necessary

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/your-url/')  # Replace with your actual URL
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('your_view_name'))  # Replace with your actual view name
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        response = self.client.get(reverse('your_view_name'))  # Replace with your actual view name
        self.assertTemplateUsed(response, 'ammonizioni/index.html')

    def test_model_creation(self):
        self.assertEqual(self.model_instance.field1, 'value1')  # Adjust fields as necessary
        self.assertEqual(self.model_instance.field2, 'value2')  # Adjust fields as necessary

    def test_form_submission(self):
        response = self.client.post(reverse('your_view_name'), {'field1': 'new_value1', 'field2': 'new_value2'})  # Adjust fields as necessary
        self.assertEqual(response.status_code, 302)  # Assuming a redirect after successful form submission
        self.assertTrue(YourModel.objects.filter(field1='new_value1').exists())  # Adjust fields as necessary