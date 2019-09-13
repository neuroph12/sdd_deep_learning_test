import os
import sys
import pyodbc
import glob
import re
import logging
import datetime 
import sys
sys.path.append('\\'.join(os.getcwd().split('\\')[0:-1]))
import config 
from collections import namedtuple
import multiprocessing
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
        #header = self.header_extraction(query)
        #row_nt = namedtuple(name,header)
        while row:
            #rows.append(row_nt(*row))
            rows.append(list(row))
            row = self.cursor.fetchone()
        return rows,sw
    
    def close(self):
        """
          cursor close
        """
        self.cursor.close()
        self.cnxn.close()

def defect_name_normalization(d_class_name,*args):
    """
    Defect class name normalized to remove special characters, spaces.
    """
    factory = config.factory
    d_name = re.sub('[-=+,#/\?:^$.@*\"¡Ø~&%¤ý!¡»\\¡®|\(\)\[\]\<\>`\'¡¦¡·]','_',d_class_name).replace(' ','_')
    coilid,camno,defectid = args
    d_image_file_name = d_name+'_'+factory+'_'+coilid+'_'+camno+'_'+str(defectid)+'.jpg'
    return d_name,d_image_file_name     

def class_no(class_name,select_class_no='all'):
    """
    Select the defect number to extract.
     arguments
    name_class : Takes a class name consisting of dict as an argument.
    """
    if select_class_no == 'all':
        s_class=list(class_name.keys())
    else:
        s_class=select_class_no
    return s_class

def image_path(defects=None):
    """
    Create an image path and image format.
     arguments
    defects : sdd Receives defect information as an argument.
    """
    image_root = config.image_root
    sdd_name = config.sdd_name
    extension = 'tif'
    if defects:
        Class = defects[1]
        coilid = str(defects[0]).zfill(8)
        camno = str(defects[2]).zfill(2)
        defectno = str(defects[3]).zfill(4)
        defectid = defects[4]
        sdd_roi = defects[5:]
        image_file = sdd_name+'_'+coilid+'_'+camno+'_'+'srcimg'+'_'+defectno+'.'+extension
        image_files = os.path.join(image_root,coilid,camno,image_file)
        if os.path.isfile(image_files):
            return Class,coilid,camno,defectno,defectid,sdd_roi,image_files      


mdb_root = config.mdb_root
query1 ="""SELECT [ClassId],[Name] FROM [defectclasses] WHERE Status= 'U'""" # Defect Number Defect Name Extraction
query2 ="""SELECT [CoilId],[Class],[CameraNo],[DefectNo],[DefectId],[RoiX0],[RoiX1],[RoiY0],[RoiY1] FROM [defects] WHERE [Class] in(%s)""" # Extraction of defect information
query3 ="""SELECT [RoiX0],[RoiX1],[RoiY0],[RoiY1] FROM [defects] WHERE [CoilId]=%s AND [DefectId]=%s""" #ROI extraction
db = odbc_connect(mdb_root) #ODBC 
class_name = db.odbc(query1,sw=True,name='class_name')#class dict 
sdd_defects = db.odbc(query2%(','.join(map(str,class_no(class_name)))) ,sw=False,name='defects') #Defect information 
sdd_image_crop = image_crop() #Crop

def thread_play(sdd):
     Class,coilid,camno,defectno,defectid,sdd_roi,image_files = image_path(sdd)
     resize_image_name,resize_image_file_name = defect_name_normalization(class_name[Class],coilid,camno,defectid)
     #sdd_image_crop.get_resize(image_files,sdd_roi,resize_image_name,resize_image_file_name)#crop image save   
     sdd_image_crop.center_of_resize(image_files,sdd_roi,resize_image_name,resize_image_file_name)#center crop image save   	 
     print('Image Crop ->',resize_image_file_name)


if __name__=="__main__":
    start_time = datetime.datetime.now()
    pool = multiprocessing.Pool(processes=4)
    pool.map(thread_play,sdd_defects,4)
    #pool.close()
    #pool.join()
    print(datetime.datetime.now() - start_time)
    db.close()
