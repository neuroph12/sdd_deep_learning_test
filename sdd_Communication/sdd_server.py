import socket
from threading import Thread
import numpy as np
import os
import io
import traceback
from PIL import Image
import time
from keras_applications.imagenet_utils import preprocess_input
import tensorflow as tf
import tensorflow.contrib.tensorrt as trt 
from tensorflow.python.platform import gfile
from matplotlib import pyplot as plt
import base64
import traceback
import sys
sys.path.append('/'.join(os.getcwd().split('/')[0:-1]))
import config 

def read_pb_graph(model):
    with gfile.FastGFile(model,'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
    return graph_def



TENSORRT_MODEL_PATH = config.frozen_name 
trt_graph = read_pb_graph(TENSORRT_MODEL_PATH)
tf_config = tf.ConfigProto()
tf_config.gpu_options.allow_growth = True
tf_sess = tf.Session(config=tf_config)
tf.import_graph_def(trt_graph, name='')
tf_input = tf_sess.graph.get_tensor_by_name(config.tf_input+':0')
tf_output = tf_sess.graph.get_tensor_by_name(config.output_input+':0')


def input_size(im_input=None,in_shape=1):
    input_shape = im_input.get_shape()[1:].as_list()
    input_shape.insert(0,in_shape)
    return input_shape

def run(output,pre_img):
    return tf_sess.run(output, feed_dict={tf_input: pre_img})

print('Model loaded')
starttime = time.time()
input_im_size = input_size(tf_input)
print('input image_size',input_im_size)
dummmy_img = np.ones(input_im_size)
run(tf_output,dummmy_img)
now = time.time()-starttime
print('Ready to load model',now)



def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def handle(ClientSocekt):
    while 1:
        length = recvall(ClientSocekt,16) 
        print('length',length)
        if length is None:
            return 
        else:       
            stringData = recvall(ClientSocekt, int(length))
            data = np.fromstring(stringData, dtype='uint8')
            name = ClientSocekt.recv(65535)
            print('Image name :',name.decode())
            f = io.BytesIO(base64.b64decode(data))
            try:
                pilimage = Image.open(f).convert('L')
                img1 = pilimage.resize(input_im_size[1:3])
                img1 = np.asarray(img1)
                input_img = img1.reshape(input_im_size)
                input_img = input_img / 255.0
                predict = run(tf_output,input_img)
                print(predict)
                label_argmax = np.argmax(predict)
                accuracy = round(predict[0][label_argmax] * 100,1)
                label = str(label_argmax)+':'+str(accuracy)
                print(label)
    
            except Exception as e:
                print('Error',e)
                traceback.print_stack()
                label = 'None'


            ClientSocekt.sendall(label.encode())  

TCP_IP = ''
TCP_PORT = config.tcp_port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind((TCP_IP, TCP_PORT))
s.listen(True)
print('Waiting to receive')
while 1:
    ClientSocekt,addr_info = s.accept()
    ct = Thread(target=handle, args=(ClientSocekt,))
    ct.run()
#ClientSocekt.close()
#pilimage.save('./%s'%(name.decode()+'.jpg'))
#print('Image save complete')

