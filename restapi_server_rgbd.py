from flask import Flask, jsonify
from flask import make_response
from flask import request
from flask import abort
import pyrealsense2 as rs
import numpy as np
import sys
import os
import cv2
import time
import json
import tensorflow as tf
import importlib
import json
from Models.maskrcnn_mask_generator import MaskGenerator
from multiprocessing import Process,Pool
from ra605.arm_kinematic import *
from Config.realsense_config import RGBDCamera,HAND_EYE_TFMATRIX
from Utils.point_cloud_tool import *
# ignore warning
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# ===============================================================
# Multithread function for detecting mask from MaskRCNN
# How to use?
"""
Send in data as this format:
For instance:
data={
    'target_label':"apple",
    'image',[[]]
}
"""
def detect_mask_function(data):
    tf.reset_default_graph()
    MASK_GENERATOR=MaskGenerator(CLASS_NAME)
    MASK_GENERATOR.load_model()
    mask=MASK_GENERATOR.generateMask(data['target_label'],data['image'])
    mask_binary=np.where(mask==1,255,0)
    cv2.imwrite(data['target_label']+".png",mask_binary)
    # partial point cloud 太少的話 就回傳none
    print("mask的點數為： %d" %(len(np.where(mask==1)[0]),))
    if(len(np.where(mask==1)[0])<2500):
        mask=None
    # realse data from gpu
    print(mask)
    tf.keras.backend.clear_session()
    del MASK_GENERATOR
    return mask

# ===============================================================
# load pointnet
pn_graph=tf.Graph()
with pn_graph.as_default():
    c=tf.constant(5.0)
    assert c.graph is pn_graph

# ================================================================
# load MaskRCNN Model
# HERE NEED TO SET UP ALL PARAMETER BY YOURSELF. SOMETHING YOU WANT TO GRASP
CLASS_NAME = ['BG', 'apple','banana','box','cup','tape']

MASK_GENERATOR=None
# ----------------------------------------------------------------
# Global variable
POINT_CLOUD_PATH_FILE="pc_file_train01.json"
REALSENSE_CAMERA=RGBDCamera()
CURRENT_POSTION=None
pose_list=[]
color_list=[]
depth_list=[]
mask_list=[]
detect_count=0
SAVE_DIRECTORY="pointnet_data_v3"
app = Flask(__name__)
# =================================================================
# Parameters
# Configure depth and color streams for realsense d435
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
align_to = rs.stream.color
align = rs.align(align_to)
# ==================================================================

# testing data
tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]
# 這邊是註冊方法 假如要trigger任何action的話 也可以藉由get
# =====================================================================
# get all tasks
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_all_task():
    return jsonify({'task': tasks})
# ======================================================================
# 獲得特定的task
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    print(task)
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})
# ===============================================================================
# post 方法實作 負責接收PXI的資料
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201
# ===============================================================================
# post Get 6dof的資料
# 收取任何從PXI的資料
# Data receiver 這邊主要都是用
"""
這個route主要負責的是接收從PXI端來的資料
可以用request的json屬性去讀取裡面的資料
"""
@app.route('/todo/api/v1.0/data/send6dof', methods=['POST'])
def create_6dof():
    global CURRENT_POSTION
    print(request.json)
    if not request.json or not '6dof' in request.json:
        abort(400)
    six_degreeOfFreedom=request.json['6dof']
    # 要處理json格式 要先將json string轉成 json
    # 這樣就可以轉成dict
    six_degreeOfFreedom=json.loads(six_degreeOfFreedom)
    print(six_degreeOfFreedom)
    CURRENT_POSTION=forward_kinematic(six_degreeOfFreedom)

    CURRENT_POSTION[0:3,3]=CURRENT_POSTION[0:3,3]/1000
    # T0_6*HAND_EYE_MATRIX
    CURRENT_POSTION=CURRENT_POSTION.dot(HAND_EYE_TFMATRIX)
    print(CURRENT_POSTION)
    # print("J1: ",six_degreeOfFreedom['J1'])
    # print("J2: ",six_degreeOfFreedom['J2'])
    # print("J3: ",six_degreeOfFreedom['J3'])
    # print("J4: ",six_degreeOfFreedom['J4'])
    # print("J5: ",six_degreeOfFreedom['J5'])
    # print("J6: ",six_degreeOfFreedom['J6'])
    # time.sleep(5)
    return jsonify({'msg': "Success"}), 201
# ==============================================================================
# Put Delete 方法實作 這邊可用可不用
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})
# ============================================================================
# 控制器希望PC這邊做甚麼事情
# Action controller
# 純粹希望pc端坐事情的 可以使用action name傳遞 注意後面的/不能夠省略
@app.route('/todo/api/v1.0/actions/<string:action_name>/', methods=['GET'])
def take_action(action_name):
    global pipeline,config,MASK_GENERATOR,REALSENSE_CAMERA,POINT_CLOUD_PATH_FILE,detect_count,SAVE_DIRECTORY
    print("url: '/todo/api/v1.0/actions/<string:action_name>'")
    if action_name==None:
        abort(404)
    # 新增action name即可
    # In order to turn on the stream in the code you need to let labview to control it through URL
    # finishing stream can use the same way to complete it.
    elif action_name=="start_stream":
        pipeline.start(config)
        return jsonify({'msg': "start stream"})
    elif action_name=="finish_stream":
        if(len(color_list)!=0):
            pose_list.clear()
            color_list.clear()
            depth_list.clear()
            mask_list.clear()        
        pipeline.stop()
        return jsonify({'msg': "finish stream"})
# ==========================================================================
    # Code with bugs, not recommend to use it
    # start an detector object
    elif action_name=="start_detector":

        tf.reset_default_graph()
        MASK_GENERATOR=MaskGenerator(CLASS_NAME)
        MASK_GENERATOR.load_model()

        return jsonify({'msg': "start mask detector"})
    # finish an detector object
    elif action_name=="finish_detector":
        print("Clear all session in the end!!!")
        # sess=tf.keras.backend.get_session()
        tf.reset_default_graph()
        tf.keras.backend.clear_session()
        del MASK_GENERATOR
        return jsonify({'msg': "finish mask detector"})
    elif action_name=="test_detector":
        # bgr type
        print(tf.keras.backend.get_session())
        image=cv2.imread('./color4.png')
        print(image.shape)
        # rgb == skimage
        image=image[:,:,::-1]
        target_label="tape"
        mask=MASK_GENERATOR.generateMask(target_label,image)
        mask_binary=np.where(mask==1,255,0)
        cv2.imwrite("mask.png",mask_binary)
        return jsonify({'msg': "Sucessfully detect mask from model1"})
# ==========================================================================
    # testing multithread with MaskRCNN model
    elif action_name=="multithread":
        data={}

        image=cv2.imread('./frame-09-10-2019-11-40-23.png')
        print(image.shape)
        # rgb == skimage
        image=image[:,:,::-1]
        data['image']=image
        data['target_label']="banana"
        pool=Pool(1)
        mask_list.append(pool.apply(detect_mask_function,(data,)))
        pool.close()
        pool.join()
        del pool
        return jsonify({'msg': "multithread test!!!"})
    # ===============================================================================
    # 這個action主要用來處理儲存的問題
    elif action_name=="check_image_number":
        """
        Because I want to do 3d-reconstruction, I need to check the length of image
        should be at least two.
        """
        print("現在的照片有： %s 張" % str(len(color_list)))
        print("現在的次數有： %s 次" % str(detect_count))
        if(len(color_list)==1):
            # 這邊要儲存partial point cloud file 還有其路徑
            folder_name=SAVE_DIRECTORY
            if os.path.isdir(folder_name):
                print("The point cloud is saving in: /",folder_name)
            else:
                os.makedirs(folder_name)
            ply_points,xyz_points=join_map_with_mask(pose_list,color_list,depth_list,mask_list,REALSENSE_CAMERA)
            if(xyz_points.shape[0]>=4000):
                file_name=time.strftime("%d-%m-%Y-%H-%M-%S")
                full_json_path='./'+folder_name+'/'+POINT_CLOUD_PATH_FILE
                pc_json_file=open(full_json_path,'r')
                path_list=json.load(pc_json_file)
                full_path_name=folder_name+"/"+file_name+".ply"
                print(full_path_name)
                print(type(path_list))
                path_list.append(full_path_name)
                pc_json_file.close()
                pc_json_file=open(full_json_path,'w')
                json.dump(path_list,pc_json_file)
                pc_json_file.close()
                savePoints_to_ply(folder_name,file_name+".ply",ply_points)
                pose_list.clear()
                color_list.clear()
                depth_list.clear()
                mask_list.clear()
                if(detect_count==5):
                    detect_count=0
                    return jsonify({'msg': "Yes"})
                return jsonify({'msg': "No"})
            else:
                pose_list.clear()
                color_list.clear()
                depth_list.clear()
                mask_list.clear()
                return jsonify({'msg': "No"})                
        else:
            return jsonify({'msg': "No"})
    # ==========================================================================
    elif action_name=="sayhi":
        # 每次讀入的session都不一樣位址
        print(len(mask_list))
        print(mask_list[0].shape)
        # with tf.Session(graph=pn_graph) as sess:
        #     print(sess)
        #     print("graph name is: ",pn_graph)
        #     print(sess.run(c))
        return jsonify({'msg': "Hello"})
    else:
        abort(404)
    # ==========================================================================

"""
這裡面的寫法必須注意的事情有：
1.要進來這個route就是必須傳遞parameter，否則會走上面那個路徑
labview端就不需要傳參數給action parameter
2.新增方法的話只要新增elif的條件判斷即可，action parameter就是對應的參數
"""
@app.route('/todo/api/v1.0/actions/<string:action_name>/<string:action_parameter>', methods=['GET'])
def take_action_with_parameter(action_name,action_parameter):
    global pipeline,config,CURRENT_POSTION,detect_count
    # 基本上 裡面可以用來處理任何邏輯運算 以及需要執行甚麼動作
    print(action_name,action_parameter)
    # pipeline.start(config)
    time.sleep(1)
    if action_name==None:
        abort(404)
    # 假如有其他action需要parameter 則加入其他elif條件即可
    elif(action_name=='takepic'):
        # 這邊的action parameter就是folder name
        folder_name=action_parameter
        if os.path.isdir(folder_name):
            print("The photo is saving in: /",folder_name)
        else:
            os.makedirs(folder_name)
        # Take picture setting up
        # ====================================
        # replace by rgbd setting up
        # while True:
        #     ret, frame = cap.read()
        #     if ret==True:
        #         cv2.imwrite(folder_name+"/"+"frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".png",frame)
        #         break

        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if color_frame:
                color_image = np.asanyarray(color_frame.get_data())
                cv2.imwrite(folder_name+"/"+"frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".png",color_image)
                # pipeline.stop()
                break
                
        return jsonify({'msg': "Success"})
    # ---------------------------------------------------------------------
    # 寫exploration algorithm的方法:
    # photo including color and depth map
    elif(action_name=="get_photo_and_mask"):
        if(action_parameter not in CLASS_NAME):
            return jsonify({'msg': "Failed WITH WRONG Parameter!"})
        color_image=None
        while True:
            # Get frameset of color and depth
            frames = pipeline.wait_for_frames()
            # frames.get_depth_frame() is a 640x360 depth image
            
            # Align the depth frame to color frame
            aligned_frames = align.process(frames)
            
            # Get aligned frames
            aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
            color_frame = aligned_frames.get_color_frame()
            
            # Validate that both frames are valid
            if not aligned_depth_frame or not color_frame:
                continue
            
            if color_frame:
                depth_image = np.asanyarray(aligned_depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())
                cv2.imwrite(SAVE_DIRECTORY+"/"+"frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".png",color_image)
                cv2.imwrite("_color2.png",color_image)
                cv2.imwrite("_dep2.png",depth_image)
                break
        target_label=str(action_parameter)
        data={}
        # bgr to rgb for detection
        image=color_image[:,:,::-1]
        data['image']=image
        data['target_label']=target_label
        pool=Pool(1)
        mask=pool.apply(detect_mask_function,(data,))
        pool.close()
        pool.join()
        del pool
        if(mask is not None):
            # 換成用image套件讀入
            # color要傳入 rgb的img
            color_img = Image.fromarray(image.astype('uint8'), 'RGB')
            depth_img = Image.fromarray(depth_image)
            mask_img = Image.fromarray(np.uint8(mask))
            # 儲存起來所有資訊
            mask_list.append(mask_img)
            color_list.append(color_img)
            depth_list.append(depth_img)
            pose_list.append(CURRENT_POSTION)
            detect_count+=1
            return jsonify({'msg': "Successfully detect mask"})
        else:
            detect_count+=1
            return jsonify({'msg': "Failed"})
    elif(action_name=="others"):
        return jsonify({'msg': action_name+action_parameter})
    else:
        abort(404)

# ==============================================================================
# router 最後都希望可以放入 errorhandler處理404的狀況
@app.errorhandler(404)
def error_handler(error):
    return make_response(jsonify({'msg': 'Failed'}), 404)

if __name__ == '__main__':

    DEBUG_MODE=True
    app.run(host='0.0.0.0',port=12345,debug = DEBUG_MODE)














    # ===================================================================
    # # Code with bugs, not recommend to use it
    # # start an detector object
    # elif action_name=="start_detector":

    #     tf.reset_default_graph()
    #     MASK_GENERATOR=MaskGenerator(CLASS_NAME)
    #     MASK_GENERATOR.load_model()

    #     return jsonify({'msg': "start mask detector"})
    # # finish an detector object
    # elif action_name=="finish_detector":
    #     print("Clear all session in the end!!!")
    #     # sess=tf.keras.backend.get_session()
    #     tf.reset_default_graph()
    #     tf.keras.backend.clear_session()
    #     del MASK_GENERATOR
    #     return jsonify({'msg': "finish mask detector"})
    # elif action_name=="test_detector":
    #     # bgr type
    #     print(tf.keras.backend.get_session())
    #     image=cv2.imread('./color4.png')
    #     print(image.shape)
    #     # rgb == skimage
    #     image=image[:,:,::-1]
    #     target_label="tape"
    #     mask=MASK_GENERATOR.generateMask(target_label,image)
    #     mask_binary=np.where(mask==1,255,0)
    #     cv2.imwrite("mask.png",mask_binary)
    #     return jsonify({'msg': "Sucessfully detect mask from model1"})