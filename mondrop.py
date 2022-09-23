#!/usr/bin/env python3
# encoding:UTF-8
'''
    2022-03-04
    *处理怪物掉落*
    掉落配置：${DIR_DROP_TXT}/<id>_<xx爆率>.txt
    物品组：${DIR_GROUP_TXT}/<id>_<xx掉落组>.txt

    *版本历史*
    v0.0.2  第一版策划反馈修改
    v0.0.3  在WPS新窗口打开文件
    v0.0.4  支持绑定物品
    v0.0.5  扩展配置其它列
    v0.0.6  命令行参数，爆率配置，异常输出
    v0.0.7  掉落配置异常输出具体位置

    *计划*
'''
import argparse
import csv
import os
import re
import sys
import traceback
from copy import copy
from enum import Enum

from idsub import getCopyFileName, isValidLine, loadItemdef, startEdit

VERSION = '0.0.7'

DIR_DROP_TXT = 'mondrop'  # 文本配置文件路径
DIR_GROUP_TXT = 'mondrop/groups'  # 文本配置文件路径
FILE_MONDEF = 'mondef.csv'
FILE_MONDROP = 'mondrop.csv'
FILE_DROPPLUS = 'dropplus.csv'
FILE_ITEMDEF = 'itemdef.csv'
COL_MONDEF_DROP = 33  # mondef drop 配置列
PTN_TXT_FILES = r'([1-9]\d+)_(.*).txt'
PTN_TXT_CELL = r'([\u4e00-\u9fa5]+);?'
PTN_COL_VALUE = r'[Cc]([1-9]\d*)=(.+)'
DROP_RATIO = 10000  # 怪物爆率比例

# mondrop 配置列
COL_MONDROP_ID = 2
COL_MONDROP_ITEM = 5
COL_MONDROP_ITEM_GROUP = 6
COL_MONDROP_PROP = 7
COL_MONDROP_BIND = 8  # 是否绑定
COL_MONDROP_BELONG_TIME = 9  # 归属时间
COL_MONDROP_VCOIN = 12
COL_MONDROP_DESC = 13

# dropplus 配置列
COL_DROPPLUS_ID = 2
COL_DROPPLUS_ITEM = 3
COL_DROPPLUS_DESC = 4


class Data:
    '''
    数据对象，将常用数据缓存，并且避免参数传递
    '''
    _dir = None
    _dir_drop_txt = None
    _dir_group_txt = None
    _itemdef = None
    _itemdef_r = None
    drops = None
    drops_r = None
    itemgroups = None
    itemgroups_r = None

    @staticmethod
    def check(dir):
        return  os.path.exists(os.path.join(dir, FILE_MONDEF)) \
            and os.path.exists(os.path.join(dir, FILE_MONDROP)) \
            and os.path.exists(os.path.join(dir, FILE_DROPPLUS)) \
            and os.path.exists(os.path.join(dir, FILE_ITEMDEF))

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
    def getItemName(id):
        if id in Data._itemdef:
            return Data._itemdef[id]
        return '未知物品'

    @staticmethod
    def reloadTxt():
        Data._dir_drop_txt = os.path.join(Data._dir, DIR_DROP_TXT)
        Data._dir_group_txt = os.path.join(Data._dir, DIR_GROUP_TXT)

        Data.drops = loadTxtFiles(Data._dir_drop_txt)
        Data.itemgroups = loadTxtFiles(Data._dir_group_txt)
        Data.drops_r = Data.R(Data.drops)
        Data.itemgroups_r = Data.R(Data.itemgroups)

    @staticmethod
    def loadDropTxt(id):
        '''文件内容：<概率,类型,数量|名称>
        1/3,元宝,100
        1,物品,50金币
        1,掉落组,一阶掉落组
        '''
        id = str(id)
        filename = os.path.join(Data._dir_drop_txt, f'{id}_{Data.drops[id]}.txt')
        ret = readCSV(filename, lambda row_data: len(row_data) >= 3 and all([len(v) for v in row_data]))
        return ret

    def loadItemGroupTxt(id):
        '''文件内容：物品名称
        (1阶)起源玄兵
        (1阶)起源战甲
        (1阶)起源头盔
        '''
        id = str(id)
        if id in Data.itemgroups:
            filename = os.path.join(Data._dir_group_txt, f'{id}_{Data.itemgroups[id]}.txt')
            ret = readCSV(filename, lambda row_data: len(row_data) == 1 and int(Data.getItemId(row_data[0])) > 0)
            return [Data.getItemId(v[0]) for v in ret]
        else:
            return []

    @staticmethod
    def getItem(name):
        if name in Data._itemdef_r:
            return Data._itemdef_r[name]
        return 0

    @staticmethod
    def getItemGroup(name):
        if name in Data.itemgroups_r:
            return Data.itemgroups_r[name]
        return 0

    @staticmethod
    def applyMondropLine(ty, n, line):
        tmp = n.split(';')
        name = tmp[0]
        if ty == DropType.ITEM:
            line[COL_MONDROP_ITEM - 1] = Data.getItem(name)
        elif ty == DropType.ITEM_GROUP:
            line[COL_MONDROP_ITEM_GROUP - 1] = Data.getItemGroup(name)
        elif ty == DropType.VCOIN:
            line[COL_MONDROP_VCOIN - 1] = name
            line[COL_MONDROP_DESC - 1] = ty
        for v in tmp[1:]:
            # deal extended args
            v = v.strip()
            if v == '1' or v == 'bind':
                line[COL_MONDROP_BIND - 1] = 1
            else:
                m = re.match(PTN_COL_VALUE, v)
                if m:
                    k, v = m.groups()
                    line[int(k) - 1] = v

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
    文件名格式：<id>_<字符串名称>.txt
    '''
    if not os.path.exists(dir):
        os.makedirs(dir)
    ret = dict()
    for f in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, f)):
            continue
        m = re.match(PTN_TXT_FILES, f)
        if m:
            tmp = m.groups()
            ret[tmp[0]] = tmp[1]
    return ret


def checkTxtFiles(dir):
    '''检查文本配置文件格式'''
    raise NotImplementedError


def readCSV(filename, check_line=None):
    rows = list()
    with open(filename, encoding='gbk') as f:
        reader = csv.reader(f)
        for row in reader:
            if check_line and not check_line(row):
                raise Exception(f'readCSV({filename})[line:{len(rows)+1}] check line error.')
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
    startEdit(filecopy)

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
        recs = applyMondrop(dir, ids)

    if len(recs) > 0:
        # 需要编辑 dropplus
        ids = list(recs)
        applyDropplus(dir, ids)

    # 3. remove copy file
    if not os.path.samefile(filename, filecopy):
        os.remove(filecopy)


def applyMondrop(dir, ids):
    '''修改mondrop表，返回引用的物品组id'''
    filename = os.path.join(dir, FILE_MONDROP)
    ids.sort()

    mondrop = readCSV(filename)
    mondrop_head, mondrop_data = mondrop[:3], mondrop[3:]
    for id in ids:
        txt_data = Data.loadDropTxt(id)
        mergeMondrop(mondrop_data, id, txt_data)

    # 重新设置第一列索引
    groups = set()
    for i, v in enumerate(mondrop_data):
        v[0] = i + 1
        tmp = v[COL_MONDROP_ITEM_GROUP - 1]
        if tmp in Data.itemgroups:
            groups.add(tmp)

    with open(filename, encoding='gbk', mode='w') as f:
        writer = csv.writer(f, lineterminator='\n')
        [writer.writerow(line) for line in mondrop_head]
        [writer.writerow(line) for line in mondrop_data]

    return groups


def mergeLines(data, new_data, COL_ID):
    '''将<new_data>按照第<COL_ID>列排序更新并写入<data>'''
    if len(new_data) == 0:
        return
    id = new_data[0][COL_ID - 1]
    old = []
    idx = 0  # 新数据插入位置
    while (idx < len(data)):
        if data[idx][COL_ID - 1] == id:
            # 移除旧配置
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

    for i, v in enumerate(new_data):
        data.insert(idx + i, v)


def mergeMondrop(data, id, txt_data):
    '''将txt文件内数据合并到表格数据'''
    template = data[0]  # 第一行作为模板数据
    new_data = [genMondropLine(template, id, v) for v in txt_data]
    mergeLines(data, new_data, COL_MONDROP_ID)


def genMondropLine(template, id, txt_line):
    '''根据模板行，创建新行数据'''
    prop, ty, n = txt_line  # n=num|name
    prop = min(DROP_RATIO, int(eval(prop) * DROP_RATIO))
    # print(prop, ty, n)
    line = copy(template)
    line[COL_MONDROP_ITEM - 1] = 0
    line[COL_MONDROP_ITEM_GROUP - 1] = 0
    line[COL_MONDROP_PROP - 1] = 0
    line[COL_MONDROP_BIND - 1] = 0
    line[COL_MONDROP_VCOIN - 1] = 0
    line[COL_MONDROP_DESC - 1] = n
    ty = DropType(ty)
    Data.applyMondropLine(ty, n, line)
    line[COL_MONDROP_ID - 1] = id
    line[COL_MONDROP_PROP - 1] = str(prop)
    return line


def applyDropplus(dir, ids):
    '''修改dropplus表'''
    filename = os.path.join(dir, FILE_DROPPLUS)
    ids.sort()

    dropplus = readCSV(filename)
    dropplus_head, dropplus_data = dropplus[:3], dropplus[3:]
    for id in ids:
        txt_data = Data.loadItemGroupTxt(id)
        mergeDropplus(dropplus_data, id, txt_data)

    # 重新设置第一列索引
    for i, v in enumerate(dropplus_data):
        v[0] = i + 1

    with open(filename, encoding='gbk', mode='w') as f:
        writer = csv.writer(f, lineterminator='\n')
        [writer.writerow(line) for line in dropplus_head]
        [writer.writerow(line) for line in dropplus_data]


def mergeDropplus(data, id, txt_data):
    '''将txt文件内数据合并到表格数据'''
    template = data[0]

    def line(itemid):
        ret = copy(template)
        ret[COL_DROPPLUS_ID - 1] = id
        ret[COL_DROPPLUS_ITEM - 1] = itemid
        ret[COL_DROPPLUS_DESC - 1] = f'#{Data.getItemName(itemid)}'
        return ret

    new_data = [line(v) for v in txt_data]
    mergeLines(data, new_data, COL_DROPPLUS_ID)


def process(filename):
    root = os.path.dirname(filename)
    name = os.path.basename(filename)
    if not Data.check(root):
        print('不支持的文件路径')
        return
    if name != FILE_MONDEF:
        # 普通编辑功能
        os.startfile(filename)
        return

    editMondef(filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='怪物掉落配置工具')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--version', help='显示版本号', action='store_true')
    group.add_argument('-f', '--filename', help='csv文件路径', default='')
    parser.add_argument('-r', '--ratio', choices=[100, 10000, 1000000], type=int, default=10000, help='爆率比例')
    args = parser.parse_args()
    # print(args)
    if args.version:
        print(f'版本号: {VERSION}')
    else:
        DROP_RATIO = args.ratio
        try:
            process(args.filename)
        except Exception as e:
            print(traceback.format_exc())
            os.system('pause')
    sys.exit(0)
