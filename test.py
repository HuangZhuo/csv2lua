from cgi import test
import unittest

from csv2lua import process
from csv2lua import DataType
from csv2lua import ExportHelper


class TestMain(unittest.TestCase):
    def test_main(self):
        ret, errs = process(['test.csv'])
        self.assertEqual(ret, 0)


class TestCommon(unittest.TestCase):
    def test_exportHelper(self):
        print(ExportHelper.parseData("520", DataType.String))
        print(ExportHelper.parseData("520;521", DataType.IntArray))

    def test_fstring(self):
        s = 1
        print(f'"{s}"')

    def test_slice(self):
        a = [1]
        print(a[1:])