#!/usr/bin/env python3
# encoding:UTF-8
'''
    Joe 20201224
    定制化csv->lua导出工具
'''

import sys
import json
import csv
import os
import re
import colorama
from concurrent.futures import ThreadPoolExecutor, as_completed

colorama.init(autoreset=True)

with open('config.json', encoding='utf8') as f:
    Config = json.load(f)


def error(*args):
    tmp = '\t'.join([str(v) for v in args])
    print(colorama.Fore.LIGHTRED_EX + tmp)


def warning(*args):
    tmp = '\t'.join([str(v) for v in args])
    print(colorama.Fore.LIGHTYELLOW_EX + tmp)


class DataType:
    String = 'string'
    Int = 'int'
    Bool = 'bool'
    IntArray = 'int[]'
    StringArray = 'string[]'

    @staticmethod
    def isArrayType(ty):
        return ty.endswith('[]')


class ExportHelper:
    @staticmethod
    def trim(str):
        return str.strip().lstrip('#')

    def filterType(str):
        str = ExportHelper.trim(str)
        return str if len(str) > 0 else DataType.String

    def filterDesc(str):
        str = ExportHelper.trim(str)
        return str.replace('\n', '\\n')

    @staticmethod
    def isValidLine(line):
        if len(line) == 0:
            return False
        if len(line[0]) == 0:
            return False
        if line[0].startswith('#'):
            return False
        return True

    @staticmethod
    def parseData(str, ty=DataType.String):
        def parse(s):
            if ty == DataType.String or ty == DataType.StringArray:
                return f'"{s}"' if s.find('\n') < 0 else f'[[{s}]]'
            elif ty == DataType.Int or ty == DataType.IntArray:
                if not re.match(r'^\-?[0-9]+$', s):
                    raise ValueError(f'"{s}"不是数字类型')
                return s
            elif ty == DataType.Bool:
                sl = s.lower()
                if sl == 'true' or sl == 'false':
                    return sl
                else:
                    return f'"{s}"'
            else:
                return f'"{s}"'

        if DataType.isArrayType(ty):
            if len(str) == 0:
                return '{}'
            data = str.split(';')
            data = [parse(v) for v in data]
            return f'{{{", ".join(data)}}}'
        else:
            return parse(str)

    @staticmethod
    def keyPaser():
        rec = {}

        def paser(k):
            if not k.isnumeric():
                return f'"{k}"', None
            if rec.get(k):
                return None, '表格重复索引'
            rec[k] = True
            return k, None

        return paser


class CSV:
    def __init__(self, filename, cfg=None):
        self._filename = filename
        name = os.path.basename(filename)
        name = os.path.splitext(name)[0]
        self._name = name
        self._descLine = Config['descLine']
        self._keyLine = Config['keyLine']
        self._typeLine = Config['typeLine']
        self._dataLine = Config['dataLine']
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        with open(self._filename, encoding=Config['encoding']) as f:
            reader = csv.reader(f)
            lines = []
            for row in reader:
                lines.append(row)
            self._descs = lines[self._descLine - 1]
            self._keys = lines[self._keyLine - 1]
            self._types = lines[self._typeLine - 1]
            self._data = lines[self._dataLine - 1:]
        self._loaded = True

    def exportTerminal(self):
        self.load()
        print(self._descs)
        print(self._keys)
        print(self._types)
        for line in self._data:
            print(line)

    def exportLua(self, dir):
        try:
            self.load()
        except FileNotFoundError as e:
            return -1, '文件不存在'
        except Exception as e:
            return -1, {f'ERR[{self._name}.csv]: {repr(e)}'}

        if not os.path.exists(dir):
            os.makedirs(dir)
        luafilename = self._name + '.lua'
        luafilename = os.path.join(dir, luafilename)

        def writeNoti(f):
            if 'luaHeader' in Config:
                f.writelines(f'\t{Config["luaHeader"]}\n\n')

        def writeDesc(f):
            for i in range(len(self._keys)):
                if len(self._keys[i]) == 0:
                    continue
                tmp = '\t%-20s%-20s%s\n' % (
                    self._keys[i],
                    self._types[i],
                    self._descs[i],
                )
                f.writelines(tmp)

        def writeData(f, line, parseKey):
            if not ExportHelper.isValidLine(line):
                return
            '''
            [1] = {
                key = value
            }
            '''
            # 默认第一列为表索引
            idx, err = parseKey(line[0])
            if err:
                raise ValueError(f'{err}:{line[0]}')
            tmp = []
            for i in range(len(line)):
                if len(self._keys[i]) == 0:
                    continue
                tmp.append(f'\t\t["{self._keys[i]}"] = {ExportHelper.parseData(line[i], self._types[i])},\n')
            f.writelines(f'\t[{idx}] = {{\n')
            f.writelines(''.join(tmp))
            f.writelines('\t},\n')

        self._keys = [ExportHelper.trim(v) for v in self._keys]
        self._types = [ExportHelper.filterType(v) for v in self._types]
        self._descs = [ExportHelper.filterDesc(v) for v in self._descs]

        ret, err = 0, list()
        with open(luafilename, 'w', encoding='utf8') as f:
            # 注释区
            f.writelines('--[[\n')
            writeNoti(f)
            writeDesc(f)
            f.writelines('--]]\n\n')
            # 数据区
            f.writelines('return {\n')

            parseKey = ExportHelper.keyPaser()
            for v in self._data:
                try:
                    writeData(f, v, parseKey)
                except ValueError as e:
                    ret = -1
                    err.append(f'ERR[{self._name}.csv]: {repr(e)}\n{v}')
                    pass
            f.writelines('}\n')
        return ret, err


def process(filelist, onProgress=None):
    if len(filelist) == 0:
        return 0, None

    fails, errs = 0, list()
    with ThreadPoolExecutor(max_workers=8) as t:
        tasks = []
        for v in filelist:
            filename = os.path.join(Config['csvDir'], v)
            obj = CSV(filename)
            tasks.append(t.submit(obj.exportLua, Config['outputDir']))
        total, finished = len(tasks), 0
        for future in as_completed(tasks):
            ret, err = future.result()
            finished += 1
            if ret < 0:
                fails += 1
                errs.extend(err)
            if onProgress:
                onProgress(total, finished)
    return fails, errs


if __name__ == '__main__':
    fails, errs = process(sys.argv[1:])
    if fails > 0:
        for e in errs:
            error(e)
    else:
        print('Finished.')
    sys.exit(0)
