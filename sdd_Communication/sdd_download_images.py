# coding: utf-8

import zeep
import urllib.request
import re
import time
import pathlib
import os
import requests
import base64
import numpy as np
import io
from datetime import datetime

#client.wsdl.dump()
#gatactivecoils=(client.service.GetActiveCoils(False))

#'http://localhost_name:51000/InspectionDataInterface/1.0/?wsdl'
#Enter your computer name
def start_get_coils(client = zeep.Client(wsdl='http://localhost_name:51000/InspectionDataInterface/1.0/?wsdl')):
    '''Please check the current coil status.
   Call GetActiveCoils to send the previously completed coil and the current working coil.
   We need to get the current coil status: I. '''
    coils = client.service.GetActiveCoils(False)
    for i in range(len(coils.Coil)):
        #print(coils.Coil[i].Status)
        status = str(coils.Coil[i].Status)
        if status in['I']:
            #print(coils.Coil[i])
            CoilKey = coils.Coil[i].CoilKey
            CoilName = coils.Coil[i].CoilName
            ParamSetName = coils.Coil[i].ParamSetName   
    return CoilKey,CoilName,ParamSetName


def Check_coil_status():
    '''You must constantly check the status of the coil in operation.
   If the coil in operation is A, check the current state of the coil (A) at intervals of 60 seconds.
   If the coil state is F, pass CoilKey, ColiName, and ParamSetName to the next get_defect_image function.''' 
    CoilKey,CoilName,ParamSetName = start_get_coils()
    while CoilKey:
        status_coil = client.service.GetActiveCoils(False)
        for i in range(len(status_coil.Coil)):
            now = datetime.now()
            nowdate = now.strftime('%Y-%m-%d %H:%M:%S')
            if CoilKey in [status_coil.Coil[i].CoilKey]:
                status = str(status_coil.Coil[i].Status)
                print('Time:{0}, Get active Coil:{1},Statis:{2}'.format(nowdate,CoilName,status))
                if status in['F']:
                    print(status_coil.Coil[i])
                    status_coil_CoilKey = status_coil.Coil[i].CoilKey
                    status_coil_CoilName = status_coil.Coil[i].CoilName
                    status_coil_ParamSetName = status_coil.Coil[i].ParamSetName
                    return status_coil_CoilKey,status_coil_CoilName,status_coil_ParamSetName
                time.sleep(60)
                break
                

def downlode_images():#Do not use now.
    '''If the download folder does not exist, create it.
      Path output if folder exists.''' 
    mother_folder = '/Downlode'
    downlode_image = os.path.join(mother_folder,'images')
    if os.path.isdir(downlode_image) is False:
        pathlib.Path(downlode_image).mkdir(parents=False, exist_ok=True)
        print('There is no download folder, so create it.' '%s : Download images by this path'%(downlode_image))
    else:
        print('%s : Download images by this path'%(downlode_image))
    return downlode_image
        

def get_defect_image(down=False,crop=True):
    '''If you request GetCoilData using CoilKey among the completed coil information 
   and request the selected defect of DefectClassKeys, the image will be downloaded. '''
    status_coil_CoilKey,status_coil_CoilName,status_coil_ParamSetName = Check_coil_status()
    get_defects = client.service.GetCoilData(CoilKey=status_coil_CoilKey,DefectClassKeys='{DCK0,0}')#{DCK0,class_no}
    
    if get_defects['Defects'] is None:
        print('Defects None')
        #sys.exit()
    elif status_coil_ParamSetName in['SDD Material name']:#Enter the material name to make it work
        image_counting = 0
        
        for i,defects in enumerate(get_defects.Defects.Defect):
            get_coilld = defects.CoilId
            get_defectclass =defects.DefectClass
            get_defectId = defects.DefectId
            get_defectimageURL = str(defects.DefectImageURL)
            get_roi = (defects.RoiX0,defects.RoiX1,defects.RoiY0,defects.RoiY1)
            if get_defectimageURL !='None':
                if down:
                    downlode = downlode_images()
                    urllib.request.urlretrieve(get_defectimageURL,downlode+'\\%s_%s_%s.jpg' %(get_coilld,get_defectId,i))
                if crop:
                    r = requests.get(get_defectimageURL, allow_redirects=True)
                    b64string = base64.b64encode(r.content)
                    data = np.array(b64string)
                    i_stringData = data.tostring()
                    image_counting +=1
                    image = np.fromstring(i_stringData,dtype='uint8')
                    f = io.BytesIO(base64.b64decode(image))
                    print(f,get_roi,str(get_coilld),'%s_%s_%s.jpg' %(get_coilld,get_defectId,i))
                    image_crop().get_resize(f,get_roi,str(get_coilld),'%s_%s_%s.jpg' %(get_coilld,get_defectId,i))
        print("You've downloaded %s images."%(image_counting))
    else:
        print('This is not a coil%s.'%{status_coil_ParamSetName})
    return get_coilld