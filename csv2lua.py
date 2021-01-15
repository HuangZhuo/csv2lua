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
import string

with open("config.json") as f:
    Config = json.load(f)


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
                return '"%s"' % s
            elif ty == DataType.Int or ty == DataType.IntArray:
                assert s.isnumeric()
                return s
            else:
                return '"%s"' % s

        if DataType.isArrayType(ty):
            data = str.split(";")
            data = [parse(v) for v in data]
            return "{%s}" % ", ".join(data)
        else:
            return parse(str)

    @staticmethod
    def test():
        # print(ExportHelper.trim(" \t#76  "))
        # lines = [[], ["#123"], ["123", "45"]]
        # for line in lines:
        #     print(ExportHelper.isValidLine(line))
        print(ExportHelper.parseData("520", DataType.String))
        print(ExportHelper.parseData("520;521", DataType.Int))

        print("099".isnumeric())
        pass


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
            self._data = lines[self._dataLine - 1 :]
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
                    self._descs[i],
                    self._types[i],
                )
                f.writelines(tmp)

        def writeData(f, line):
            if not ExportHelper.isValidLine(line):
                return
            """
            [1] = {
                key = value
            }
            """
            assert line[0].isnumeric()
            tmp = []
            for i in range(len(line)):
                if len(self._keys[i]) == 0:
                    continue
                tmp.append(
                    '\t\t["%s"] = %s,\n'
                    % (self._keys[i], ExportHelper.parseData(line[i], self._types[i]))
                )
            # 默认第一列为表索引
            idx = line[0]
            f.writelines("\t[%s] = {\n" % idx)
            f.writelines("".join(tmp))
            f.writelines("\t},\n")

        self._keys = [ExportHelper.trim(v) for v in self._keys]
        self._types = [ExportHelper.trim(v) for v in self._types]
        self._descs = [ExportHelper.trim(v) for v in self._descs]
        with open(luafilename, "w", encoding="utf8") as f:
            # 注释区
            f.writelines("\n--[[\n")
            writeNoti(f)
            writeDesc(f)
            f.writelines("--]]\n\n")
            # 数据区
            f.writelines("return {\n")
            for v in self._data:
                writeData(f, v)
            f.writelines("}\n")


def main(argv):
    todo = []
    if len(argv) > 0:
        todo = argv
    else:
        todo = [v["name"] for v in Config["needConvert"]]
    for v in todo:
        filename = os.path.join(Config["csvDir"], v)
        print(filename)
        obj = CSV(filename)
        obj.exportLua(Config["outputDir"])
    # ExportHelper.test()


if __name__ == "__main__":
    print("Start....")
    main(sys.argv[1:])
    print("Finished!")
