"""
This function is mainly implemented to generate the mask from MaskRCNN.
In order to use it properly, you need to set up your MaskRCNN folder in the Model directory which
is the same with this file. Furthermore, you need to properly set up your weights correctly on MODEL_PATH

"""
import os
import sys
import random
import math
import numpy as np
import cv2
import tensorflow as tf
FILE_ABSDIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR=FILE_ABSDIR+"/"+"MaskRCNN"
# Root directory of the project
print("Directory of MaskRCNN is: ",ROOT_DIR)
 
# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn.config import Config
from mrcnn import utils
import mrcnn.model as modellib
 
# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
print(MODEL_DIR)
# Local path to trained weights file
MODEL_PATH = os.path.join(MODEL_DIR ,"shapes20191113T1842/mask_rcnn_shapes_0030.h5")

# Directory of images to run detection on
IMAGE_DIR = os.path.join(ROOT_DIR, "images")
 
class ShapesConfig(Config):
    """Configuration for training on the toy shapes dataset.
    Derives from the base Config class and overrides values specific
    to the toy shapes dataset.
    """
    # Give the configuration a recognizable name
    NAME = "shapes"
 
    # Train on 1 GPU and 8 images per GPU. We can put multiple images on each
    # GPU because the images are small. Batch size is 8 (GPUs * images/GPU).
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
 
    # Number of classes (including background)
    NUM_CLASSES = 1 + 5  # background + 3 shapes
 
    # Use small images for faster training. Set the limits of the small side
    # the large side, and that determines the image shape.
    IMAGE_MIN_DIM = 480
    IMAGE_MAX_DIM = 640
 
    # Use smaller anchors because our image and objects are small
    RPN_ANCHOR_SCALES = (8 * 6, 16 * 6, 32 * 6, 64 * 6, 128 * 6)  # anchor side in pixels
 
    # Reduce training ROIs per image because the images are small and have
    # few objects. Aim to allow ROI sampling to pick 33% positive ROIs.
    TRAIN_ROIS_PER_IMAGE =50
 
    # Use a small epoch since the data is simple
    STEPS_PER_EPOCH = 100
 
    # use small validation steps since the epoch is small
    VALIDATION_STEPS = 50
 
#import train_tongue
#class InferenceConfig(coco.CocoConfig):
class InferenceConfig(ShapesConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1



class MaskGenerator:
    config=InferenceConfig()

    def __init__(self,class_names):
        self.class_names=class_names
        print("Create MaskRCNN detector!!!")
    def load_model(self):
        config=tf.ConfigProto()
        config.gpu_options.allow_growth=True
        # config.gpu_options.per_process_gpu_memory_fraction=0.9
        tf.keras.backend.set_session(tf.Session(config=config))
        self.graph=tf.get_default_graph()
        with self.graph.as_default():
            # Create model object in inference mode.
            self.model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=self.config)

            # Load weights trained on MS-COCO
            self.model.load_weights(MODEL_PATH, by_name=True)
    def generateMask(self,label,image):

        with self.graph.as_default():
            print("graph is: ",self.graph)
            results=self.model.detect([image], verbose=1)
            r = results[0]
            target_index=self.class_names.index(label)
            # can find the instance
            if(target_index in r['class_ids']):
                idx=list(r['class_ids']).index(target_index)
                return   r['masks'][:,:,idx].astype(int)
            # if not
            else:
                return None


if __name__=="__main__":
    target_label='cup'
    # COCO Class names
    # Index of the class in the list is its ID. For example, to get ID of
    # the teddy bear class, use: class_names.index('teddy bear')
    class_names = ['BG', 'apple','banana','box','cup','tape']
    mask_generator=MaskGenerator(class_names)
    mask_generator.load_model()
    # load image from images directory
    # image = skimage.io.imread(IMAGE_DIR+"/color1.png")
    image= cv2.imread(IMAGE_DIR+"/color4.png")

    # # Run detection
    # results = mask_generator.model.detect([image], verbose=1)
    mask=mask_generator.generateMask(target_label,image)
    # # Visualize results

    # r = results[0]
    # print(r['class_ids'])
    # print(r['masks'].shape)
    # mask=r['masks'][:,:,0].astype(int)
    mask_binary=np.where(mask==1,255,0)
    cv2.imwrite("mask.png",mask_binary)
    # visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'],
                                # class_names, r['scores'])