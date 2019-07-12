from django.test import TestCase
from super_dash.utils import del_cache

# Create your tests here.
class SuperDashTest(TestCase):

    def test_del_model_cache(self):
        del_cache('name')
