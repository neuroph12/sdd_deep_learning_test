import socket
import numpy
import os
import base64
import sys
sys.path.append('/'.join(os.getcwd().split('/')[0:-1]))
import config 

class client:
    def __init__(self):
        self.TCP_IP = config.tcp_ip
        self.TCP_PORT = config.tcp_port
        self.sock = socket.socket()
        try:
            self.sock.connect((self.TCP_IP, self.TCP_PORT))
            print('Connected: {}:{}'.format(self.TCP_IP, self.TCP_PORT))  
        except Exception as e:
            print('Connection failed: {}:{}'.format(self.TCP_IP, self.TCP_PORT))  
        
    def image_format(self,images):
        with open(images,'rb')as image: 
            b64string = base64.b64encode(image.read()).decode() 
            data = numpy.array(b64string) 
            i_stringData = data.tostring()  
            
            return i_stringData
        
    def get_predict(self,images):

        stringData = self.image_format(images)
        try:
            self.sock.send(str(len(stringData)).ljust(16).encode()) 
            self.sock.send(stringData)      
            self.sock.send(str(images).encode())  
        except  SocketError as e:
            if e.errno != errno.ECONNRESET:#Not error we are looking for
                raise
            pass # Handle error here.
        
        print('%s Transfer completed' %(os.path.basename(images)) )
        
        while 1:
            data = self.sock.recv(65535)
            if data:
                #print(data)
                return data 
        #self.sock.close()
        


