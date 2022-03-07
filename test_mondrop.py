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

    def test_applyMondrop(self):
        mondrop.applyMondrop(DIR_CSV, ['10086'])


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

    def test_split(self):
        arr = [1, 2, 3, 4, 5, 6]
        print(arr[:3], arr[3:])  # [1, 2, 3] [4, 5, 6]
        print(arr[3:3], arr[3:4])  # [] [4]

    def test_find(self):
        # https://pythonspot.com/array-find/
        x = ["Moon", "Earth", "Jupiter", "Neptune", "Earth", "Venus"]
        get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]
        print(get_indexes("Earth", x))

    def test_walk(self):
        # https://stackoverflow.com/questions/32544835/python-create-dictionary-using-dict-with-integer-keys
        a = ['a', 'b', 'c', 'd']
        for i, v in enumerate(a):
            print(i, v)

        # 移除中间元素
        b = []
        b.append(a.pop(1))
        b.append(a.pop(1))
        print(a, b)

        # 中间插入元素
        c = ['F', 'F', 'K']
        for i, v in enumerate(c):
            a.insert(1 + i, v)
        print(a)

        # 错误：遍历删除
        # for v in a:
        #     if v == 'F':
        #         a.remove(v)
        # print(a)

        # 正确：遍历删除
        idx = 0
        while (idx < len(a)):
            if a[idx] == 'F':
                a.pop(idx)
            else:
                idx += 1
        print(a)