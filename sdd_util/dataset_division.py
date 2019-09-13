
import os
import shutil
from itertools import groupby
import glob
sys.path.append('\\'.join(os.getcwd().split('\\')[0:-1]))
import config 


class dataset_division:
    """
      Crop CBE Msos -> Learning Data Partitioning
    """
    
    def __init__(self):
        self.image_root = config.image_root
        self.dataset_root = config.dataset_root
        self.train_root = os.path.join(self.dataset_root,'train')
        self.validation_root =  os.path.join(self.dataset_root,'validation')
        self.test_root =  os.path.join(self.dataset_root,'test')
        
    def re_file_no(self):
        """
        Recreate the file name number
        """
        file_names = os.listdir(self.image_root)
        for name in file_names:
            path1 = os.path.join(self.image_root,name)
            for no,path2 in enumerate(os.listdir(path1)):
                images = os.path.join(path1,path2)
                re_image_name =name+'_'+str(no).zfill(5)+'.jpg'
                print(images,'->',re_image_name)
                os.rename(images,os.path.join(path1,re_image_name))
    
    def division(self):
        """
        Learning Data Partitioning
        """
        if not os.path.isdir(self.dataset_root):
            os.mkdir(self.dataset_root)
        if not os.path.isdir(self.train_root):
            os.mkdir(self.train_root)
        if not os.path.isdir(self.validation_root):
            os.mkdir(self.validation_root)
        if not os.path.isdir(self.test_root):
            os.mkdir(self.test_root)
            
        images_file_dir = glob.glob(self.image_root+'\\'+'*\\*.jpg')
        image_file_breed = map(lambda file: (file.split('\\')[7],file),images_file_dir)
        for image_name , image_folders in groupby(image_file_breed,lambda x: x[0]):
            for i,image_folder in enumerate(image_folders):
                if i % 5 == 0: #test
                    test_defect = os.path.join(self.test_root,image_name)
                    if not os.path.isdir(test_defect):
                        os.mkdir(test_defect)
                    print('image move',test_defect)
                    shutil.move(image_folder[1],test_defect)
                    
                elif i % 5 == 1: #validation
                    validation_defect = os.path.join(self.validation_root,image_name)
                    if not os.path.isdir(validation_defect):
                        os.mkdir(validation_defect)
                    print('image move',validation_defect)
                    shutil.move(image_folder[1],validation_defect)
                else:#train
                    train_defect = os.path.join(self.train_root,image_name)
                    if not os.path.isdir(train_defect):
                        os.mkdir(train_defect)
                    print('image move',train_defect)
                    shutil.move(image_folder[1],train_defect)
                    
if __name__=='__main__':
    start = dataset_division()
    start.re_file_no()
    start.division()
