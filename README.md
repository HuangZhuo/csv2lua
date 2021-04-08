# csv2lua
定制化csv->lua导出工具

## 功能

1. 支持配置文件
2. 支持跳过空行，忽略'#'开头的行
3. 支持单元格内由';'分隔创建数组

## 配置说明

配置文件：`config.json`
```
{
    "csvDir": "表格所在目录",
    "outputDir": "导出到目录（不存在会被创建）",
    "encoding": "csv文件编码",
    "descLine": "注释所在行",
    "keyLine": "key所在行",
    "typeLine": "类型所在行",
    "dataLine": "数据起始行",
    "needConvert": [
        {
            "name": "表格文件名"
        }
    ]
}
```

## 导出为exe
> pyinstaller -F .\csv2lua.py

## 测试
```
>python3 csv2lua.py
Start....
./csv\test.csv
Finished!
```
test.csv -> test.lua

## todo
