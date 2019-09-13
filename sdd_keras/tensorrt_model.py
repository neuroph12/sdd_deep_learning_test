from tensorflow.keras.models import load_model
import tensorflow as tf
import tensorflow.contrib.tensorrt as trt
from tensorflow.python.platform import gfile
from tensorflow.python.framework import graph_io
from tensorflow.python.tools import freeze_graph
from tensorflow.core.protobuf import saver_pb2
from tensorflow.python.training import saver as saver_lib
import tensorflow.keras.backend as k 
sys.path.append('/'.join(os.getcwd().split('/')[0:-1]))
import config 



class frozengraph:
    def __init__(self,model):
        self.output_names = model.output.op.name
        self.input_names = model.input.op.name
        sess = tf.keras.backend.get_session()
        frozen_graph = tf.graph_util.convert_variables_to_constants(sess, sess.graph.as_graph_def(), [self.output_names])
        self.frozen_graph = tf.graph_util.remove_training_nodes(frozen_graph)


    def TfEngine(self,frozen_name):

        tft_graph_def = trt.create_inference_graph(self.frozen_graph,
                                                   [self.output_names],max_batch_size=1,
                                                   max_workspace_size_bytes=1<<25,
                                                   precision_mode='FP16',
                                                   minimum_segment_size=50)  
        with gfile.FastGFile(frozen_name,'wb')as f:
            f.write(tft_graph_def.SerializeToString())


        print('convert %s complete'%(frozen_name))
        # check how many ops of the original frozen model
        all_nodes = len([1 for n in self.frozen_graph.node])
        print("numb. of all_nodes in frozen graph:", all_nodes)

        # check how many ops that is converted to TensorRT engine
        trt_engine_nodes = len([1 for n in tft_graph_def.node if str(n.op) == 'TRTEngineOp'])
        print("numb. of trt_engine_nodes in TensorRT graph:", trt_engine_nodes)
        all_nodes = len([1 for n in tft_graph_def.node])
        print("numb. of all_nodes in TensorRT graph:", all_nodes)


def main():
    keras_model = config.keras_model 
    frozen_name = config.frozen_name
    model = load_model(keras_model)
    model.save_weights('weights.h5') #ValueError: Tensor name 'batch_normalization..' 
    k.clear_session()
    k.set_learning_phase(0)
    model = load_model(keras_model)
    model.load_weights('weights.h5') 
    frozengraph(model).TfEngine(frozen_name)

if __name__ =='__main__':
   main()

  

  


