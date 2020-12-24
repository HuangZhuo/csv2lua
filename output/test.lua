
--[[
	这个文件是由【csv2lua】工具导出，不要手动修改直接提交！

	id                  	序号                  	int                 
	name                	名称                  	string              
	use_money           	花费钱                 	int                 
	use_food            	花费实物                	int                 
	is_init             	初始化                 	bool                
	defense             	防御                  	int                 
--]]

return {
	[1] = {
		["id"] = 1,
		["name"] = "house",
		["use_money"] = 1000,
		["use_food"] = 123,
		["is_init"] = "TRUE",
		["defense"] = {100, 101},
	},
	[2] = {
		["id"] = 2,
		["name"] = "farm",
		["use_money"] = 100,
		["use_food"] = 234,
		["is_init"] = "FALSE",
		["defense"] = {200, 101, 102},
	},
}
