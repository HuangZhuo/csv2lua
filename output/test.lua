--[[
	这个文件是由【csv2lua】工具导出，不要手动修改直接提交！

	id                  int                 序号
	name                string              名称
	use_money           int                 花费钱
	use_food            int                 花费实物
	is_init             bool                初始化
	defense             int[]               防御
--]]

return {
	[1] = {
		["id"] = 1,
		["name"] = "house",
		["use_money"] = 1000,
		["use_food"] = -123,
		["is_init"] = true,
		["defense"] = {100, 101},
	},
	[2] = {
		["id"] = 2,
		["name"] = "farm",
		["use_money"] = 100,
		["use_food"] = 234,
		["is_init"] = false,
		["defense"] = {200, 101, 102},
	},
}
