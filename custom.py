# 自定义表格转换需求

import csv
import os.path
import sys
from typing import OrderedDict

from csv2lua import ExportHelper, error


def mongen(src_file, dest_file=None):
    '''
    根据mongen表，反向索引怪物所在地图
    第1列是地图名，第4列是怪物id
    反向索引后，第一列是怪物id，第二列是怪物出现的地图名数组
    '''
    if not dest_file:
        name, ext = os.path.splitext(src_file)
        dest_file = f'{name}_tmp{ext}'
    with open(src_file, encoding='gbk') as f:
        reader = csv.reader(f)
        tmp = OrderedDict()
        for row in reader:
            if ExportHelper.isValidLine(row):
                mapid, monid = row[0], row[3]
                if not monid in tmp:
                    tmp[monid] = list()
                if not mapid in tmp[monid]:
                    tmp[monid].append(mapid)
        # todo: use map func
        for k in tmp.keys():
            tmp[k] = ';'.join(tmp[k])
        with open(dest_file, mode='w') as f2:
            writer = csv.writer(f2, lineterminator='\n')
            writer.writerows(tmp.items())
    return 0


def main():
    if len(sys.argv) < 2:
        error('ERR args')
        return -1
    else:
        return mongen(sys.argv[1])


if __name__ == '__main__':
    main()
