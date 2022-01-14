# csv2lua
定制化csv->lua导出工具

## 功能

1. 支持配置文件
2. 支持跳过空行，忽略`#`开头的行
3. 支持单元格内由`;`分隔创建数组

## 使用

```shell
csv2lua.py <csvfilename>...
```
### 注意事项
- `csvfilename`为相对`csvDir`下的文件名
- 可以传入多个文件名利用多线程批量完成转换

## 配置说明

配置文件：`config.json`
```json
{
    "csvDir": "表格所在目录",
    "outputDir": "导出到目录（不存在会被创建）",
    "encoding": "csv文件编码",
    "descLine": "注释所在行",
    "keyLine": "key所在行",
    "typeLine": "类型所在行",
    "dataLine": "数据起始行",
    "luaHeader": "导出lua文件的头部注释说明"
}
```

### 注意事项
- `encoding`配置最好使用`utf8`或者`gbk`（不要使用`gb2312`）

## 导出为exe
> pyinstaller -F .\csv2lua.py

## 测试
> python csv2lua.py test.csv

## todo
- [ ] 更加完善的命令行支持
- [ ] 支持出错后终止选项