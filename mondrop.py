#!/usr/bin/env python3
# encoding:UTF-8
'''
    2022-03-04
    处理怪物掉落
'''
import sys
import os
import csv
import re

from idsub import getCopyFileName
from idsub import loadItemdef

VERSION = '0.0.1'

DIR_TXT = 'mondrop'  # 文本配置文件路径
FILE_MONDEF = 'mondef.csv'
FILE_MONDROP = 'mondrop.csv'
FILE_DROPPLUS = 'dropplus.csv'
COL_MONDEF_DROP = 33  # mondef drop 配置列
PTN_TXT_FILES = r'([\u4e00-\u9fa5]+)_([1-9]\d+).txt'
PTN_TXT_CELL = r'([\u4e00-\u9fa5]+);?'


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
    pass


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
    dir_txt = os.path.join(dir, DIR_TXT)
    drops, _ = loadDropsAndItems(dir_txt)

    # 1. 生成临时文件用于编辑
    lines = readCSV(filename)
    filecopy = getCopyFileName(filename)
    with open(filecopy, encoding='gbk', mode='w') as f:
        writer = csv.writer(f, lineterminator='\n')
        for line in lines:
            line[COL_MONDEF_DROP - 1] = subCellEx(line[COL_MONDEF_DROP - 1], drops)
            writer.writerow(line)
    os.system(f'start /wait {filecopy}')

    # 2. 保存临时文件，生成需要修改的掉落id集合
    drops, _ = loadDropsAndItems(dir_txt)
    drops_r = {v: k for k, v in drops.items()}
    lines = readCSV(filecopy)
    recs = set()
    with open(filename, encoding='gbk', mode='w') as f:
        writer = csv.writer(f, lineterminator='\n')
        for line in lines:
            tmp = subCellEx(line[COL_MONDEF_DROP - 1], drops_r, recs)
            # todo: 检查单元格格式

            line[COL_MONDEF_DROP - 1] = tmp
            writer.writerow(line)

    if len(recs) > 0:
        # 需要编辑 mondrop
        ids = [drops_r[v] for v in recs]
        applyMondrop(dir_txt, ids, drops)

    # 3. remove copy file
    if not os.path.samefile(filename, filecopy):
        os.remove(filecopy)


def applyMondrop(dir_txt, ids, drops):
    ids.sort()

    print(ids)


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
