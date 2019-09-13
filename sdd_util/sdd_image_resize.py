from PIL import Image
import os
import config

class image_crop:
    """
    sdd Crop the image in batches.
     arguments
    x_fixed_area : Default area to crop the image
    y_fixed_area :             ''
      image_size : CNN image size
    resize_image_folder :Path to save image
    """
    def __init__(self):
        self.x_fixed_area ,self.y_fixed_area = 200,200
        self.image_size = config.image_size[0]
        self.resize_image_folder =config.resize_image_folder
        
    def resize_path(self,defect_name):
        """
        Create folder with fault name
        """
        r_path = os.path.join(self.resize_image_folder,defect_name)
        if os.path.isdir(r_path):
            return r_path
        else:
            os.mkdir(r_path)
            return r_path   

    def Image_area(self,x0,x1,y0,y1):
        """
        Set coordinates for cropping an image
        """
        #x-axis compensation 
        box_x = int((self.x_fixed_area-(x1-x0))/2)
        #y-axis compensation
        box_y = int((self.y_fixed_area-(y1-y0))/2)
        x0=(x0 - box_x)
        x1=(x1 + box_x)
        y0=(y0 - box_y)
        y1=(y1 + box_y)  
        return x0,x1,y0,y1   
    
    def get_resize(self,image_file,roi,defect_name,resize_name):
        """
        Cut and save the image with the set image coordinates.
         arguments
        image_file  : Image file path
               roi  : Defect area
        defect_name : Fully qualified fault name
        resize_name : Cropped Image File Name
        """
        
        image = Image.open(image_file)
        resize_root = self.resize_path(defect_name)
        resize_image_name = os.path.join(resize_root,resize_name)
        x_size ,y_size = image.size
        if self.y_fixed_area > y_size:
            self.y_fixed_area = y_size
        d_x0,d_x1,d_y0,d_y1 = 0,x_size,0,y_size
        o_x0,o_x1,o_y0,o_y1 = roi
        x0,x1,y0,y1 = self.Image_area(o_x0,o_x1,o_y0,o_y1)
        if x0 < d_x0:
            x0 = d_x0
            x1=abs(x0)+x1
        if x1 > d_x1:
            x1 = x_size 
            x0 = x0-(x1-x_size)
        if y0 < d_y0:
            y0 = d_y0
            y1= abs(y0)+y1
        if y1 > d_y1:
            y1 = y_size
            y0= y0-(y1-y_size)
        area=[x0,y0,x1,y1]
        c_image = image.crop(area)
        c_re_image = c_image.resize((self.image_size,self.image_size))
        c_re_image.save(resize_image_name)

    def center_of_resize(self,image_file,roi,defect_name,resize_name):
        """
        Crop the defect ROI area and resize it to center the background image.
         arguments
        image_file  : Image file path
               roi  : Defect area
        defect_name : Fully qualified fault name
        resize_name : Cropped Image File Name
        """
        image = Image.open(image_file)
        x0,x1,y0,y1 = roi
        cropped_img = image.crop((x0,y0,x1,y1))
        resize_root = self.resize_path(defect_name)
        resize_image_name = os.path.join(resize_root,resize_name)
        c_x,c_y =cropped_img.size

        if c_x > self.image_size:
            cropped_img=cropped_img.resize((self.image_size,c_y))
        if c_y > self.image_size:
            cropped_img=cropped_img.resize((c_x,self.image_size))
        c_x,c_y =cropped_img.size
        c_x = int(round(c_x/2,0))
        c_y = int(round(c_y/2,0))
        b_im = Image.new("L",(self.image_size,self.image_size))
        b_size = int(round(self.image_size/2,0))
        b_im.paste(im=cropped_img, box=(b_size-c_x, b_size-c_y))
        b_im.save(resize_image_name,quality=100)
