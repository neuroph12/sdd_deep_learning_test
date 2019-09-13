from __future__ import print_function
import tensorflow.keras
import os
import sys
import json
import matplotlib.pyplot as plt 
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras import layers,Input,models
from tensorflow.keras import optimizers
from tensorflow.keras import losses
from tensorflow.keras.utils import multi_gpu_model
sys.path.append('/'.join(os.getcwd().split('/')[0:-1]))
import config 

class Base_init(object):
    def __init__(self,class_weight=None,batch_size = 32):
        self.model = None
        self.batch_size = batch_size
        self.num_classes = config.num_classes
        self.img_size = config.image_size
   
    def call(self):
        raise NotImplementedError('subclasses must override _create()')

class image_generator(Base_init):
    
    def __init__(self):
        super(image_generator, self).__init__()
        self.dataset_dir = config.dataset_dir
       
    def __call__(self,dataset_name):
        image_dir = os.path.join(self.dataset_dir,dataset_name)
        
        if dataset_name is not 'test':
            datagen = ImageDataGenerator(rescale=1./255,
                                      #width_shift_range=0.2,   #no sdd image
                                      #height_shift_range=0.2,  #no sdd image
                                      shear_range=0.2,
                                      #zoom_range=0.2,          #no sdd image
                                      vertical_flip=True,
                                      horizontal_flip=True,
                                      fill_mode='nearest')
        else:
            datagen = ImageDataGenerator(rescale=1./255)
        return datagen.flow_from_directory(image_dir,target_size=(self.img_size[0],self.img_size[0]),
                                           batch_size=self.batch_size,color_mode='grayscale',class_mode='categorical')

class c_InceptionV3(Base_init):

    def __init__(self,use_bn=False, use_dp=False):
        super(c_InceptionV3, self).__init__()
        self.use_bn = use_bn
        self.use_dp = use_dp
        self.inputs = layers.Input(shape=self.img_size)
        if self.use_dp:
            self.dp = layers.Dropout(0.5)
        if self.use_bn:
            self.bn = layers.BatchNormalization(axis=-1)
        
    def __call__ (self):
        base_model = InceptionV3(input_tensor=self.inputs,include_top=False,weights=None,pooling=None)
        x = base_model.output
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(1024, activation='relu', name='fc1')(x)
        if self.use_dp:
            x = self.dp(x)
        if self.use_bn:
            x = self.bn(x)
        predictions = layers.Dense(self.num_classes, activation='softmax')(x)
        return models.Model(base_model.input,predictions)


def config_write(file,search,layer_name):
    t_no = 0
    with open(file,'r+b') as f:
        for line in f.readlines():
            line_no = len(line)
            t_no += line_no
            line_list = line.split()
            if line_list:
                if line_list[0] == search.encode('utf-8'):
                    print('found an %s'%(search))
                    position=t_no-line_no
                    f.seek(position)
                    new_line =(search+" = '"+layer_name+"'")
                    new_line =(new_line+'#'*int(line_no-len(new_line)-1)+'\n').encode('utf-8')
                    print('Change content \n %s \n -> %s \n' %(b''.join(line_list),new_line))
                    f.write(new_line)
                    break

def class_json(train,validation,test,jfile,make=True):
    if train.class_indices == validation.class_indices==test.class_indices:
        classes= {v:k for k,v in train.class_indices.items()}
        with open(jfile,'w',encoding='utf-8') as f:
             json.dump(classes,f,ensure_ascii=False,indent='\t')
        print('Save class name as json')
    else:
        print('The class does not match. Check it out.')  

def smooth_curve(points,factor=0.8):
    smoothed_points =[]
    for point in points:
        if smoothed_points:
            previous = smoothed_points[-1]
            smoothed_points.append(previous*factor+point*(1-factor))
        else:
            smoothed_points.append(point)
    return smoothed_points

def plt_graph(x,y1,y2,label_name1,label_name2,title_name,save_name):
    plt.plot(x,smooth_curve(y1),'bo',label=label_name1)
    plt.plot(x,smooth_curve(y2),'b',label=label_name2)
    plt.title(title_name)
    plt.legend()
    fig = plt.gcf()
    fig.savefig('./'+save_name)
    plt.figure()
    print('graph save')

def main():
    save_dir = os.path.join(os.getcwd(), 'saved_models')
    model_name = 'keras_sdd_trained_inceptionv3_2hap_07.h5'

    train_gen= image_generator()('train')
    validation_gen= image_generator()('validation')
    test_gen = image_generator()('test')
    class_json(train_gen,validation_gen,test_gen,config.class_json,make=True)
    model = c_InceptionV3(use_dp=True)()
    model.summary()
    model = multi_gpu_model(model,gpus=2)
    model.compile(optimizer=optimizers.Adam(lr=1e-4),loss='categorical_crossentropy',metrics=['acc'])
    history_tl = model.fit_generator(train_gen,steps_per_epoch=50,epochs=500,verbose=2,validation_data=validation_gen,validation_steps=50)
    model.evaluate_generator(test_gen)
    model.save(os.path.join(save_dir,model_name)) 
    acc = history_tl.history['acc']
    val_acc = history_tl.history['val_acc']
    loss = history_tl.history['loss']
    val_loss = history_tl.history['val_loss']
    epochs = range(1,len(acc)+1)
    plt_graph(epochs,acc,val_acc,'Smoothed training acc','Smoothed validation acc','Training and validation accuracy','accuracy.jpg')
    plt_graph(epochs,loss,val_loss,'Smoothed training loss','Smoothed validation loss','Training and validation loss','loss.jpg')
    input_names = model.input.op.name #model_name
    output_names = model.output.op.name
    config_write(config.config_root,'tf_input',input_names)  #config writer
    config_write(config.config_root,'output_input',output_names)      

if __name__ =='__main__':
    main()

