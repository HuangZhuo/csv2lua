import unittest
import mondrop
from os import path

DIR_CSV = 'csv_mondrop'
DIR_TXT = 'csv_mondrop/mondrop'


class TestMondrop(unittest.TestCase):
    def test_loadTxtFiles(self):
        print(mondrop.loadTxtFiles(DIR_TXT))

    def test_loadDropsAndItems(self):
        print(mondrop.loadDropsAndItems(DIR_TXT))

    def test_readCSV(self):
        mondrop.readCSV(path.join(DIR_CSV, 'mondef.csv'))

    def test_editMondef(self):
        mondrop.editMondef(path.join(DIR_CSV, 'mondef.csv'))

    def test_subCellEx(self):
        mapping = {
            '你好': '1',
            '再见': '2',
        }
        print(mondrop.subCellEx('你', mapping))
        print(mondrop.subCellEx('你好', mapping))
        print(mondrop.subCellEx('你好;再见', mapping))
        print(mondrop.subCellEx('你好;再见;董小姐', mapping))


class TestBasic(unittest.TestCase):
    def test_findall(self):
        import re
        from mondrop import PTN_TXT_CELL
        print(re.findall(PTN_TXT_CELL, '你好;再见;'))

    def test_set(self):
        def func(s):
            s.add(1)

        s = set()
        func(s)
        print(s)