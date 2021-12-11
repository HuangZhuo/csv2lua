#!/usr/bin/env python3
# encoding:UTF-8
"""
    Joe 20201224
    定制化csv->lua导出工具
    1. 支持配置文件
    2. 支持跳过空行，忽略'#'开头的行
    3. 支持单元格内由';'分隔创建数组

"""

import sys
import json
import csv
import os
import re
import colorama

colorama.init(autoreset=True)

with open("config.json") as f:
    Config = json.load(f)


def error(*args):
    tmp = '\t'.join([str(v) for v in args])
    print(colorama.Fore.RED + tmp)


def warning(*args):
    tmp = '\t'.join([str(v) for v in args])
    print(colorama.Fore.YELLOW + tmp)


class DataType:
    String = "string"
    Int = "int"
    Bool = "bool"
    IntArray = "int[]"
    StringArray = "string[]"

    @staticmethod
    def isArrayType(ty):
        return ty.endswith("[]")


class ExportHelper:
    @staticmethod
    def trim(str):
        return str.strip().lstrip("#")

    def filterType(str):
        str = ExportHelper.trim(str)
        return str if len(str) > 0 else DataType.String

    def filterDesc(str):
        str = ExportHelper.trim(str)
        return str.replace("\n", "\\n")

    @staticmethod
    def isValidLine(line):
        if len(line) == 0:
            return False
        if len(line[0]) == 0:
            return False
        if line[0].startswith("#"):
            return False
        return True

    @staticmethod
    def parseData(str, ty=DataType.String):
        def parse(s):
            if ty == DataType.String or ty == DataType.StringArray:
                return f'"{s}"' if s.find('\n') < 0 else f'[[{s}]]'
            elif ty == DataType.Int or ty == DataType.IntArray:
                if not re.match(r'^\-?[0-9]+$', s):
                    raise ValueError("'{}'不是数字类型".format(s))
                return s
            elif ty == DataType.Bool:
                sl = s.lower()
                if sl == 'true' or sl == 'false':
                    return sl
                else:
                    # warning("'{}'不是正确的布尔类型" .format(s))
                    return '"%s"' % s
            else:
                return '"%s"' % s

        if DataType.isArrayType(ty):
            if len(str) == 0:
                return "{}"
            data = str.split(";")
            data = [parse(v) for v in data]
            return "{%s}" % ", ".join(data)
        else:
            return parse(str)

    @staticmethod
    def keyPaser():
        rec = {}

        def paser(k):
            if not k.isnumeric():
                # return None, '表格序号索引不是数字类型'
                return f'"{k}"', None
            if rec.get(k):
                return None, '表格重复ID|索引'
            rec[k] = True
            return k, None

        return paser


class CSV:
    def __init__(self, filename, cfg=None):
        self._filename = filename
        name = os.path.basename(filename)
        name = os.path.splitext(name)[0]
        self._name = name
        self._descLine = Config["descLine"]
        self._keyLine = Config["keyLine"]
        self._typeLine = Config["typeLine"]
        self._dataLine = Config["dataLine"]
        self.preload()
        pass

    def preload(self):
        with open(self._filename, encoding=Config["encoding"]) as f:
            reader = csv.reader(f)
            lines = []
            for row in reader:
                lines.append(row)
            self._descs = lines[self._descLine - 1]
            self._keys = lines[self._keyLine - 1]
            self._types = lines[self._typeLine - 1]
            self._data = lines[self._dataLine - 1:]
        pass

    def exportTerminal(self):
        self.preload()
        print(self._descs)
        print(self._keys)
        print(self._types)
        for line in self._data:
            print(line)
        pass

    def exportLua(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)
        luafilename = self._name + os.path.extsep + "lua"
        luafilename = os.path.join(dir, luafilename)

        # print(luafilename)

        def writeNoti(f):
            f.writelines("\t这个文件是由【csv2lua】工具导出，不要手动修改直接提交！\n\n")

        def writeDesc(f):
            for i in range(len(self._keys)):
                if len(self._keys[i]) == 0:
                    continue
                tmp = "\t%-20s%-20s%s\n" % (
                    self._keys[i],
                    self._types[i],
                    self._descs[i],
                )
                f.writelines(tmp)

        def writeData(f, line, parseKey):
            if not ExportHelper.isValidLine(line):
                return
            """
            [1] = {
                key = value
            }
            """
            # 默认第一列为表索引
            idx, err = parseKey(line[0])
            if err:
                raise ValueError("{}：{}".format(err, line[0]))
            tmp = []
            for i in range(len(line)):
                if len(self._keys[i]) == 0:
                    continue
                tmp.append('\t\t["%s"] = %s,\n' % (self._keys[i], ExportHelper.parseData(line[i], self._types[i])))
            f.writelines("\t[%s] = {\n" % idx)
            f.writelines("".join(tmp))
            f.writelines("\t},\n")

        self._keys = [ExportHelper.trim(v) for v in self._keys]
        self._types = [ExportHelper.filterType(v) for v in self._types]
        self._descs = [ExportHelper.filterDesc(v) for v in self._descs]
        with open(luafilename, "w", encoding="utf8") as f:
            # 注释区
            f.writelines("--[[\n")
            writeNoti(f)
            writeDesc(f)
            f.writelines("--]]\n\n")
            # 数据区
            f.writelines("return {\n")

            parseKey = ExportHelper.keyPaser()
            for v in self._data:
                try:
                    writeData(f, v, parseKey)
                except ValueError as e:
                    error(repr(e))
                    error("出错行:", v)
                    warning("忽略出错行导出")
                    pass
            f.writelines("}\n")


def main(argv):
    todo = []
    if len(argv) > 0:
        todo = argv
    else:
        todo = [v["name"] for v in Config["needConvert"]]
    for v in todo:
        filename = os.path.join(Config["csvDir"], v)
        print("parse:", filename)
        obj = CSV(filename)
        obj.exportLua(Config["outputDir"])


if __name__ == "__main__":
    main(sys.argv[1:])
