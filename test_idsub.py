import unittest
import idsub


class TestIDSub(unittest.TestCase):
    def test_main(self):
        idsub.process('./csv_idsub/caiquanrankaward.csv')

    def test_startEdit(self):
        idsub.startEdit('./csv_idsub/caiquanrankaward.csv')
        print('finished!')

    def test_what_the_fuck_shell(self):
        import platform
        print(platform.version())
        import os
        print(os.environ)
