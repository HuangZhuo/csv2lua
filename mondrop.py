#!/usr/bin/env python3
# encoding:UTF-8
'''
    2022-03-04
    处理怪物掉落
    概念：
    掉落配置：<xx爆率>_<id>.txt
    物品组：<xx掉落组>_<id>.txt
'''
import csv
import os
import re
import sys
from copy import copy
from enum import Enum

from idsub import getCopyFileName, isValidLine, loadItemdef

VERSION = '0.0.1'

DIR_TXT = 'mondrop'  # 文本配置文件路径
FILE_MONDEF = 'mondef.csv'
FILE_MONDROP = 'mondrop.csv'
FILE_DROPPLUS = 'dropplus.csv'
FILE_ITEMDEF = 'itemdef.csv'
COL_MONDEF_DROP = 33  # mondef drop 配置列
PTN_TXT_FILES = r'([\u4e00-\u9fa5]+)_([1-9]\d+).txt'
PTN_TXT_CELL = r'([\u4e00-\u9fa5]+);?'

# mondrop 配置列
COL_MONDROP_ID = 2
COL_MONDROP_ITEM = 5
COL_MONDROP_ITEM_GROUP = 6
COL_MONDROP_PROP = 7
COL_MONDROP_BIND = 8
COL_MONDROP_VCOIN = 12
COL_MONDROP_DESC = 13


class Data:
    '''
    数据对象，将常用数据缓存，并且避免参数传递
    '''
    _dir = None
    _itemdef = None
    _itemdef_r = None
    drops = None
    drops_r = None
    itemgroups = None
    itemgroups_r = None

    @staticmethod
    def init(dir):
        Data._dir = dir
        Data._itemdef = loadItemdef(os.path.join(dir, FILE_ITEMDEF))
        Data._itemdef_r = Data.R(Data._itemdef)
        Data.reloadTxt()

    @staticmethod
    def getItemId(name):
        if name in Data._itemdef_r:
            return Data._itemdef_r[name]
        return 0

    @staticmethod
    def reloadTxt():
        dir_txt = os.path.join(Data._dir, DIR_TXT)
        Data.drops, Data.itemgroups = loadDropsAndItems(dir_txt)
        Data.drops_r = Data.R(Data.drops)
        Data.itemgroups_r = Data.R(Data.itemgroups)

    @staticmethod
    def getDropTxtFile(id):
        dir_txt = os.path.join(Data._dir, DIR_TXT)
        return os.path.join(dir_txt, f'{Data.drops[id]}_{id}.txt')

    @staticmethod
    def getItemGroupId(name):
        if name in Data.itemgroups_r:
            return Data.itemgroups_r[name]
        return 0

    @staticmethod
    def R(d):
        return {v: k for k, v in d.items()}


class DropType(str, Enum):
    '''掉落配置-掉落类型'''
    VCOIN = '元宝'
    ITEM = '物品'
    ITEM_GROUP = '掉落组'


def loadTxtFiles(dir):
    '''返回自定义配置文件列表
    文件名格式：<中文名称>_<id>.txt
    '''
    ret = list()
    for f in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, f)):
            continue
        m = re.match(PTN_TXT_FILES, f)
        if m:
            ret.append(m.groups())
    return ret


def checkTxtFiles(dir):
    '''检查文本配置文件格式'''
    raise NotImplementedError


def loadDropsAndItems(dir):
    '''返回掉落配置（xx爆率） 和 物品组（xx掉落组）
    '''
    drops, items = dict(), dict()
    for item in loadTxtFiles(dir):
        if item[0].endswith('爆率'):
            drops[item[1]] = item[0]
        if item[0].endswith('掉落组'):
            items[item[1]] = item[0]
    return drops, items


def loadDropTxt(filename):
    '''文件内容：<概率,类型,数量|名称>
    1/3,元宝,100
    1,物品,50金币
    1,掉落组,一阶掉落组
    '''
    ret = readCSV(filename)
    return ret


def readCSV(filename):
    rows = list()
    with open(filename, encoding='gbk') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    return rows


def subCellEx(cell, mapping, _recs=None):
    if cell in mapping:
        if None != _recs:
            _recs.add(cell)
        return mapping[cell]
    else:
        cells = cell.split(';')
        if len(cells) > 1:
            cells = [subCellEx(v, mapping, _recs) for v in cells]
            return ';'.join(cells)
        else:
            return cell


def editMondef(filename):
    dir = os.path.dirname(filename)
    Data.init(dir)

    # 1. 生成临时文件用于编辑
    lines = readCSV(filename)
    filecopy = getCopyFileName(filename)
    with open(filecopy, encoding='gbk', mode='w') as f:
        writer = csv.writer(f, lineterminator='\n')
        for line in lines:
            line[COL_MONDEF_DROP - 1] = subCellEx(line[COL_MONDEF_DROP - 1], Data.drops)
            writer.writerow(line)
    os.system(f'start /wait {filecopy}')

    # 2. 保存临时文件，生成需要修改的掉落id集合
    Data.reloadTxt()
    lines = readCSV(filecopy)
    recs = set()
    with open(filename, encoding='gbk', mode='w') as f:
        writer = csv.writer(f, lineterminator='\n')
        for line in lines:
            tmp = subCellEx(line[COL_MONDEF_DROP - 1], Data.drops_r, recs)
            # todo: 检查单元格格式

            line[COL_MONDEF_DROP - 1] = tmp
            writer.writerow(line)

    if len(recs) > 0:
        # 需要编辑 mondrop
        ids = [Data.drops_r[v] for v in recs]
        applyMondrop(dir, ids)

    # 3. remove copy file
    if not os.path.samefile(filename, filecopy):
        os.remove(filecopy)


def applyMondrop(dir, ids):
    filename = os.path.join(dir, FILE_MONDROP)
    ids.sort()

    mondrop = readCSV(filename)
    mondrop_head, mondrop_data = mondrop[:3], mondrop[3:]
    for id in ids:
        txt_file = Data.getDropTxtFile(id)
        txt_data = loadDropTxt(txt_file)
        mergeMondrop(mondrop_data, id, txt_data)

    # 重新设置第一列索引
    for i, v in enumerate(mondrop_data):
        # v[0] = i + 1
        break

    with open(filename, encoding='gbk', mode='w') as f:
        writer = csv.writer(f, lineterminator='\n')
        [writer.writerow(line) for line in mondrop_head]
        [writer.writerow(line) for line in mondrop_data]


def mergeMondrop(data, id, txt_data):
    '''将txt文件内数据合并到表格数据'''
    old = []
    idx = 0  # 新数据插入位置
    while (idx < len(data)):
        if data[idx][COL_MONDROP_ID - 1] == id:
            old.append(data.pop(idx))
        else:
            # 这里要求id连续出现
            if (len(old)) > 0:
                break
            idx += 1

    # todo: try keep old cfg in other cols

    # 找到新的插入位置
    if len(old) == 0:
        idx = 0
        nid = int(id)
        while (idx < len(data)):
            if (isValidLine(data[idx]) and int(data[idx][1]) > nid):
                break
            else:
                idx += 1

    # 插入数据
    template = data[0]  # 第一行作为模板数据
    for i, v in enumerate(txt_data):
        line = genMondropLine(template, id, v)
        data.insert(idx + i, line)


def genMondropLine(template, id, txt_line):
    '''根据模板行，创建新行数据'''
    line = copy(template)
    line[COL_MONDROP_ITEM - 1] = 0
    line[COL_MONDROP_ITEM_GROUP - 1] = 0
    line[COL_MONDROP_PROP - 1] = 0
    line[COL_MONDROP_BIND - 1] = 0
    line[COL_MONDROP_VCOIN - 1] = 0
    line[COL_MONDROP_DESC - 1] = ''
    prop, ty, n = txt_line  # n=num|name
    prop = min(10000, int(eval(prop) * 10000))
    # print(prop, ty, n)
    ty = DropType(ty)
    if ty == DropType.ITEM:
        line[COL_MONDROP_ITEM - 1] = Data.getItemId(n)
    elif ty == DropType.ITEM_GROUP:
        line[COL_MONDROP_ITEM_GROUP - 1] = Data.getItemGroupId(n)
    elif ty == DropType.VCOIN:
        line[COL_MONDROP_VCOIN - 1] = n
    line[COL_MONDROP_ID - 1] = id
    line[COL_MONDROP_PROP - 1] = str(prop)
    return line


def applyDropplus(dir, ids):
    pass


def process(filename):
    if not os.path.exists(filename):
        print('文件不存在')
        return

    if not filename.endswith('.csv'):
        print('只支持.csv文件类型')
        return


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print(f'version: {VERSION}')
    else:
        process(sys.argv[1])
    sys.exit(0)
