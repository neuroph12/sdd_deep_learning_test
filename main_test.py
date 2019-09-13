
#test sdd deep learning

from sdd_Communication import  sdd_client
#from sdd_Communication.sdd_download_images import get_defect_image
from sdd_util.sdd_database import db_extraction
from config import class_json
import glob
import json 
import os
import config 




#print(class_json)
#####################################################################
test_image_root = '/sdd_images/crop_image/89005/*.jpg'
test_image = glob.glob(test_image_root)
#print(test_image)
print('test')
#####################################################################

#while 1:
#    coil_id = get_defect_image(crop=True)

get_data_query = """SELECT TOP 1000 [no]
      ,[defect_no]
      ,[sdd_class]
      ,[deep_class]
      ,[deep_class_name]
      ,[deep_accuracy]
  FROM [2HAP_Deep_Test].[dbo].[prediction]"""

insert_query ="""insert into [2HAP_Deep_Test].[dbo].[prediction] 
 values('{0}','{1}','{2}','{3}','{4}','{5}','{6}')"""
                  
sdd_deep_test_db = db_extraction(config.server_name,config.database_name) #database

with open(class_json)as json_file: #label name json  load
    json_data=json.load(json_file)
#print(json_data)
scc  = sdd_client.client()  #crop image client 
for i,im in enumerate(test_image): 
    coil_id,defect_no,no = os.path.basename(os.path.splitext(im)[0]).split('_')
    print('no: %s,coil_id: %s,defect_no: %s' %(no,coil_id,defect_no))
    predict = scc.get_predict(im).decode('utf-8') 
    key_no = predict.split(':')[0] #dict keys
    print(json_data[key_no],predict)
    #database insert
    sdd_deep_test_db.insert_data(insert_query.format(no,coil_id,defect_no,0,0,json_data[key_no],predict.split(':')[1]).replace("\n","")) #database insert
sdd_deep_test_db.close() #database close