#!/usr/bin/env python3
# encoding:UTF-8
'''
    2022-02-18
    打开一个表格，将其中的itemid替换成中文名，保存时替换成id进行保存
'''
import sys
import os
import csv

VERSION = '0.0.3'

FILE_ITEM_DEF = 'itemdef.csv'
ITEM_DEF_ID_COL = 1
ITEM_DEF_NAME_COL = 4


def isValidLine(line):
    if len(line) == 0 or len(line[0]) == 0:
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


def subCell(cell, mapping):
    if cell in mapping:
        return mapping[cell]
    else:
        cells = cell.split(';')
        if len(cells) > 1:
            cells = [subCell(v, mapping) for v in cells]
            return ';'.join(cells)
        else:
            return cell


def getCopyFileName(filename):
    name, ext = os.path.splitext(filename)
    return f'{name}_copy{ext}'


def transfer(src, dest, mapping):
    newrows = list()
    with open(src, encoding='gbk') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 0 or not isValidLine(row[0]):
                # 不需要替换的数据，原样保留
                newrows.append(row)
            else:
                row = [subCell(v, mapping) for v in row]
                newrows.append(row)
    with open(dest, encoding='gbk', mode='w') as f:
        writer = csv.writer(f, lineterminator='\n')
        [writer.writerow(v) for v in newrows]
    return dest


def createCopy(filename, id2name):
    filecopy = getCopyFileName(filename)
    return transfer(filename, filecopy, id2name)


def saveFile(filename, id2name):
    name2id = {v: k for k, v in id2name.items()}
    filecopy = getCopyFileName(filename)
    return transfer(filecopy, filename, name2id)


def process(filename):
    if not os.path.exists(filename):
        print('文件不存在')
        return

    if not filename.endswith('.csv'):
        print('只支持.csv文件类型')
        return

    root = os.path.dirname(filename)
    itemdef = os.path.join(root, FILE_ITEM_DEF)
    if not os.path.exists(itemdef):
        os.startfile(filename)
        return

    # print(os.path.normpath(itemdef))
    id2name = loadItemdef(itemdef)
    # print(id2name)
    filecopy = createCopy(filename, id2name)
    filecopy = os.path.abspath(filecopy)
    filecopy = os.path.normpath(filecopy)
    # 开启一个进程打开 filecopy
    # os.system(f'start /wait {filecopy}')
    startEdit(filecopy)
    # 进程结束的时候将数据反写到 filename
    saveFile(filename, id2name)
    # 删除临时文件
    os.remove(filecopy)


def startEdit(filename):
    '''打开并等待文件编辑完成'''
    filename = os.path.abspath(filename)
    exe = './opencsv.cmd'
    if os.path.exists(exe):
        exe = os.path.abspath(exe)
        cmd = exe + ' "' + filename + '"'
        print('opencsv: ' + cmd)
        return os.system(cmd)
    else:
        return os.system(f'start /wait {filename}')


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print(f'version: {VERSION}')
    else:
        process(sys.argv[1])
    sys.exit(0)
