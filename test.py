import unittest

from csv2lua import DataType
from csv2lua import ExportHelper


class TestCommon(unittest.TestCase):
    def test_exportHelper(self):
        print(ExportHelper.parseData("520", DataType.String))
        print(ExportHelper.parseData("520;521", DataType.IntArray))

    def test_mongen(self):
        import custom
        custom.mongen('csv/mongen.csv')