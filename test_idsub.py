import unittest
import idsub


class TestIDSub(unittest.TestCase):
    def test_main(self):
        idsub.process('./csv_idsub/caiquanrankaward.csv')