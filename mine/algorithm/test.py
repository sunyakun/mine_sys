import pandas

from unittest import TestCase
from . import kmeans


class TestAlgorithm(TestCase):

    def test_kmeans(self):
        ds = pandas.read_csv('D:\\home\\work\\mine\\data_set\\basketball2.csv')
        models = kmeans.entry(ds, {
            "name": "basketball",
            "axis": ["point", "opp_point"]
        })
        pass
