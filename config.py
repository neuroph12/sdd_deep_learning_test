
import os 

####################################
#CBE_extraction(multiprocessing).py#
####################################

#defect_name_normalization
factory = 'factory'
#image_path
parent_root = 'parent_root'
image_root = os.path.join(parent_root,'archive/images')
sdd_name = 'sdd_name'
mdb_root = os.path.join(parent_root,'archive/archive.mdb')

####################################
#               CNN                #
####################################

image_size = (299,299,1)
num_classes = 9

####################################
# sdd_keras_inception_v3_train.py  #
####################################
dataset_dir = os.path.join(parent_root,'sdd_images/sdd_dataset')
config_root = os.path.join(parent_root,'config.py')
class_json = os.path.join(parent_root,'classes.json')
tf_input = 'input_1'#############################################################
output_input = 'dense_1/concat'################################################

####################################
#       tensorrt_model.py          #
#         sdd_server.py            #
####################################
keras_model = os.path.join(parent_root,'saved_models/keras_sdd_trained_inceptionv3_2hap_03.h5')
frozen_name = os.path.join(parent_root,'saved_models/keras_sdd_trained_inceptionv3_2hap_03.uff')


####################################
#          sdd_client.py           #
####################################
tcp_ip = 'tcp_ip'
tcp_port = 5001



####################################
#      sdd_image_resize.py         #
####################################

resize_image_folder = os.path.join(parent_root,'sdd_images/CBE_Msos_Crop_images')

####################################
#      dataset_division.py         #
####################################

image_root = os.path.join(parent_root,'sdd_images/archive_crop')
dataset_root = os.path.join(parent_root,'sdd_images/sdd_dataset')

####################################
#         sdd_database.py          #
####################################

server_name = 'server_name'
database_name = 'database_name'
