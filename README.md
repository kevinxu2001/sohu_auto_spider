1. Setup the main json file:
	Download the model json data from auto.sohu.com url: http://db.auto.sohu.com/api/inc/brand/all_models.inc, and put into directory ${ROOT_PATH}/data/1.0/source/
	
2. Get model list json file:
	Run cmd 'pyton sina_auto_spider.py model'.
	Script will claw the data based on main_json_data, and write the data into file in the dir  ${ROOT_PATH}/data/1.0/sink/trims_dict
	
3. Get trim list json file:
	run cmd 'pyton sina_auto_spider.py trim', be sure step 2 has been executed completly.
	Script will claw the trim data based on model_list_json_file, and write the data into the dir ${ROOT_PATH}/data/1.0/sink/trims_profile/${SUB_DIR}
	