#!/usr/bin/env python3
# encoding:UTF-8
'''
    2022-02-18
    打开一个表格，将其中的itemid替换成中文名，保存时替换成id进行保存
'''
import sys
import os
import csv

VERSION = '0.0.1'

FILE_ITEM_DEF = 'itemdef.csv'
ITEM_DEF_ID_COL = 1
ITEM_DEF_NAME_COL = 4


def isValidLine(line):
    if len(line) == 0:
        return False
    if len(line[0]) == 0:
        return False
    if line[0].startswith('#'):
        return False
    return True


def loadItemdef(src_file):
    '''加载itemdef的id和name'''
    id2name = {}
    with open(src_file, encoding='gbk') as f:
        reader = csv.reader(f)
        reader = filter(isValidLine, reader)
        for row in reader:
            id, name = row[0], row[3]
            id2name[id.strip()] = name
    return id2name


def subCell(cell, id2name):
    if cell in id2name:
        return id2name[cell]
    else:
        cells = cell.split(';')
        if len(cells) > 1:
            cells = [subCell(v, id2name) for v in cells]
            return ';'.join(cells)
        else:
            return cell


def getCopyFileName(filename):
    name, ext = os.path.splitext(filename)
    return f'{name}_copy{ext}'


def createCopy(filename, id2name):
    '''
    创建一个副本表，针对每一个cell
    基本替换规则：
    1. cell是数字
    2. cell是以`;`分割的数组，数组元素是数字
    '''
    newrows = list()
    with open(filename, encoding='gbk') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 0 or not isValidLine(row[0]):
                # 不需要替换的数据，原样保留
                newrows.append(row)
            else:
                row = [subCell(v, id2name) for v in row]
                newrows.append(row)
    filecopy = getCopyFileName(filename)
    with open(filecopy, encoding='gbk', mode='w') as f:
        writer = csv.writer(f, lineterminator='\n')
        [writer.writerow(v) for v in newrows]
    return filecopy


def saveFile(filename, id2name):
    name2id = {v: k for k, v in id2name.items()}
    filecopy = getCopyFileName(filename)
    newrows = list()
    with open(filecopy, encoding='gbk') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 0 or not isValidLine(row[0]):
                # 不需要替换的数据，原样保留
                newrows.append(row)
            else:
                row = [subCell(v, name2id) for v in row]
                newrows.append(row)
    with open(filename, encoding='gbk', mode='w') as f:
        writer = csv.writer(f, lineterminator='\n')
        [writer.writerow(v) for v in newrows]
    return filename


def process(filename):
    root = os.path.dirname(filename)
    itemdef = os.path.join(root, FILE_ITEM_DEF)
    # print(os.path.normpath(itemdef))
    id2name = loadItemdef(itemdef)
    # print(id2name)
    filecopy = createCopy(filename, id2name)
    # 开启一个进程打开 filecopy
    filecopy = os.path.abspath(filecopy)
    filecopy = os.path.normpath(filecopy)
    # print(filecopy)
    os.system(f'start /wait {filecopy}')
    # 进程结束的时候将数据反写到 filename
    saveFile(filename, id2name)
    os.remove(filecopy)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print(VERSION)
    else:
        process(sys.argv[1])
    sys.exit(0)
