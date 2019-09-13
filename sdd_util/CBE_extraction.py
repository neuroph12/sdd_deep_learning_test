import os
import sys
import pyodbc
import glob
import re
import logging
import datetime 
from time import sleep
from collections import namedtuple
from printProgressBar import printProgressBar
from sdd_image_resize import image_crop


def dict_conversion(func):
    def wrapper(*args,**kwargs):
        o_row,sw = func(*args,**kwargs)
        if sw:
            c_row = dict(o_row)
            print('rows : type[list] -> type{dict}')
            return c_row
        else:
            return o_row
    return wrapper

class odbc_connect:
    """
    SDD CBE To connect to MDB and extract data.
    When calling a class, it takes the mdb path as a parameter.
    Method : header_extraction,odbc,close
    """
    def __init__(self,mdb):
        conn_str = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'r'DBQ=%s;'%(mdb))
        self.cnxn = pyodbc.connect(conn_str)
        self.cursor = self.cnxn.cursor()

    def header_extraction(self,query):
        """
        Extract the header from the query statement using regular expressions.
        """
        header_re = re.findall('.+(?=FROM)',query)
        return re.sub('[|[|]|]|SELECT','',*header_re).strip().replace(',',' ')
        
    @dict_conversion 
    def odbc(self,query=None,sw=None,name=None): #archive.mdb
        """
        arguments:
            quray(str) :Query statements you want to extract from ODBC
              sw(bool) :Change extract data type list-> dict (Limited to class number and name extraction)
        """
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        rows = []
        header = self.header_extraction(query)
        row_nt = namedtuple(name,header)
        while row:
            rows.append(row_nt(*row))
            row = self.cursor.fetchone()
        return rows,sw
    
    def close(self):
        """
          cursor close
        """
        self.cursor.close()
        self.cnxn.close()
		
		
		

class defect_image_load:
    """
    Generate sdd image format from sdd db.

    arguments
    select_class_no : class number in list form.  ex)[0,1,100,229] ,'all' Extract all class numbers
    name_class : Takes a class name consisting of dict as an argument.
    """
    def __init__(self,name_class):
        self.select_class_no = 'all'   #[0,1,100,229]
        self.image_root = '/archive/images'
        self.sdd_name = 'sdd_name'
        self.extension = 'tif'
        if self.select_class_no == 'all':
            self.s_class=list(name_class.keys())
        else:
            self.s_class=self.select_class_no

    def image_path(self,defects=None):
        """
        Create an image path and image format.
         arguments
        defects : sdd Receives defect information as an argument.
        """
        if defects:
            Class = defects.Class
            coilid = str(defects.CoilId).zfill(8)
            camno = str(defects.CameraNo).zfill(2)
            defectno = str(defects.DefectNo).zfill(4)
            defectid = defects.DefectId
            image_file = self.sdd_name+'_'+coilid+'_'+camno+'_'+'srcimg'+'_'+defectno+'.'+self.extension
            image_files = os.path.join(self.image_root,coilid,camno,image_file)
            if os.path.isfile(image_files):
                return Class,coilid,camno,defectno,defectid,image_files      
            
def defect_name_normalization(d_class_name):
    """
    Defect class name normalized to remove special characters, spaces.
    """
    d_name = re.sub('[-=+,#/\?:^$.@*\"¡Ø~&%¤ý!¡»\\¡®|\(\)\[\]\<\>`\'¡¦¡·]','_',d_class_name).replace(' ','_')
    d_image_file_name = d_name+'_'+str(no)+'.jpg'
    return d_name,d_image_file_name     

def log_Settings(file):
    return logging.basicConfig(filename=file,level=logging.DEBUG)


if __name__=="__main__":
    
    mdb_root = '/archive/archive.mdb'    
    log_root = '/sdd_log/cbe_extraction.log '
    query1 ="""SELECT [ClassId],[Name] FROM [defectclasses] WHERE Status= 'U'""" # Defect Number Defect Name Extraction
    query2 ="""SELECT [CoilId],[Class],[CameraNo],[DefectNo],[DefectId] FROM [defects] WHERE [Class] in(%s)""" # Extraction of defect information
    query3 ="""SELECT [RoiX0],[RoiX1],[RoiY0],[RoiY1] FROM [defects] WHERE [CoilId]=%s AND [DefectId]=%s""" #ROI extraction
    
    log_Settings(log_root) #log setup

    
    db = odbc_connect(mdb_root) #ODBC 
    logging.info('{} mdb connection.'.format(db))
    class_name = db.odbc(query1,sw=True,name='class_name')#class dict 
    logging.info('{} mdb Defect name extraction complete.'.format(class_name))
    sdd_image_path = defect_image_load(class_name) #defect image path
    logging.info('{} defect image path.'.format(sdd_image_path))
    sdd_defects = db.odbc(query2%(','.join(map(str,sdd_image_path.s_class))) ,sw=False,name='defects') #Defect information 
    logging.info('Extraction of sdd defect information')
    sdd_image_crop = image_crop() #Crop
    l = len(sdd_defects)
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    start_time = datetime.datetime.now()    
    for no,sdd_defect in  enumerate(sdd_defects):
        Class,coilid,camno,defectno,defectid,image_files = sdd_image_path.image_path(defects=sdd_defect)
        logging.info('{} Data Processing.'.format(image_files))
        sdd_roi = db.odbc(query3%(coilid,defectid) ,sw=False,name='ROI') #ROI information odbc connection extraction
        logging.info('{} ROI extraction.'.format(sdd_roi))
        resize_image_name,resize_image_file_name = defect_name_normalization(class_name[Class]) #Db defect name normalization
        sdd_image_crop.get_resize(image_files,*sdd_roi,resize_image_name,resize_image_file_name)#crop image save
        logging.info('{} Resize image.'.format(resize_image_file_name))
        sleep(0.1)
        printProgressBar(no+1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    print(datetime.datetime.now()-start_time)		
    db.close()
