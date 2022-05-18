# 自定义表格转换需求

import csv
import os.path
import sys
from typing import OrderedDict

from csv2lua import ExportHelper


def map2npc(src_file) -> dict:
    '''
    功能：获取地图通过npc进入映射
    '''
    ret = {}
    with open(src_file, encoding='utf8') as f:
        reader = csv.reader(f)
        reader = filter(ExportHelper.isValidLine, reader)
        for row in reader:
            ret[row[0]] = row[1]
    return ret


def mongen(map2npc_file, src_file):
    '''
    功能：根据mongen表，反向索引怪物所在地图。-> mongen_tmp
    第1列是地图名，第4列是怪物id
    反向索引后，第一列是怪物id，第二列是怪物出现的地图名数组
    '''
    name, ext = os.path.splitext(src_file)
    dest_file = f'{name}_tmp{ext}'

    m2n = map2npc(map2npc_file)

    with open(src_file, encoding='gbk') as f:
        reader = csv.reader(f)
        reader = filter(ExportHelper.isValidLine, reader)
        tmpMap = OrderedDict()
        for row in reader:
            mapid, monid = row[0], row[3]
            if not monid in tmpMap:
                tmpMap[monid] = list()
            if not mapid in tmpMap[monid]:
                tmpMap[monid].append(mapid)
        tmp = []
        for _, v in enumerate(tmpMap):
            try:
                tmpNpc = [m2n[k] for k in tmpMap[v]]
                tmp.append([v, ';'.join(tmpMap[v]), ';'.join(tmpNpc)])
            except KeyError as e:
                tmp.append([v, 'MISSING', e.args[0]])
            except Exception as e:
                print(repr(e))
        with open(dest_file, mode='w') as f2:
            writer = csv.writer(f2, lineterminator='\n')
            writer.writerow(['#id', 'map', 'npc'])
            writer.writerows(tmp)
    return dest_file


def write_bosstrial(src_file, dest_file):
    '''
    功能：修改bosstraial.csv，把数据放到第4,5列
    '''
    tmp = {}
    with open(src_file, encoding='utf8') as f:
        reader = csv.reader(f)
        reader = filter(ExportHelper.isValidLine, reader)
        for row in reader:
            tmp[row[0]] = row

    buf = []
    missing = set()
    with open(dest_file, mode='r', encoding='gbk') as f2:
        buf = list(csv.reader(f2))
        # 提前检查表格是否可以正确修改输出
        for line in buf:
            if ExportHelper.isValidLine(line) and line[0] in tmp:
                map, npc = tmp[line[0]][1], tmp[line[0]][2]
                if map == 'MISSING':
                    missing.add(npc)
                    continue
                line[3], line[4] = map, npc
    if missing:
        print(f'需要补全地图配置：{str(missing)}')
        return False
    with open(dest_file, mode='w', encoding='gbk') as f2:
        writer = csv.writer(f2, lineterminator='\n')
        for line in buf:
            writer.writerow(line)
    return True


def main():
    if len(sys.argv) < 4:
        print('ERR args')
        return -1
    else:
        tmpfile = mongen(sys.argv[1], sys.argv[2])
        write_bosstrial(tmpfile, sys.argv[3])
        return 0


if __name__ == '__main__':
    main()
