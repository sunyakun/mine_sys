from django.test import TestCase
from mine.algorithm.common import training
from mine.algorithm.C45.interface import entry


# Create your tests here.
class TestMine(TestCase):
    def setUp(self):
        super().setUp()
        self.data_fp = open('D:\\home\\work\\mine\\data_set\\Play_Golf.csv')
        self.cfg = {
            "name": "play golf",
            "preprocess_columns": ["Temperature", "Humidity"],
            "result_column": "Play"
        }

        def clean_fp():
            self.data_fp.close()
        self.addCleanup(clean_fp)

    def test_training(self):
        future = training(self.data_fp, self.cfg)
        assert future.exception() is None

    def test_entry(self):
        models = entry(self.data_fp, self.cfg)
