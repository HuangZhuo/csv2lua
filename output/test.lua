
--[[
	����ļ����ɡ�csv2lua�����ߵ�������Ҫ�ֶ��޸�ֱ���ύ��

	id                  	���                  	int                 
	name                	����                  	string              
	use_money           	����Ǯ                 	int                 
	use_food            	����ʵ��                	int                 
	is_init             	��ʼ��                 	bool                
	defense             	����                  	int                 
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
