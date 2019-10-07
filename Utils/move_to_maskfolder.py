"""
這個檔案主要用來處理將labelme_json裡面的每個json folder 取出裡面的label.png
並且將名稱改成對應的folder名稱且複製到cv2_mask的folder裡面
"""


import shutil
import os
base_dir='../Models/MaskRCNN/samples/mydataset/graspingitem'
src_dir = base_dir+'/labelme_json'
dest_dir = base_dir+'/cv2_mask'

for child_dir in os.listdir(src_dir):
    new_name = child_dir.split('_')[0] + '.png'
    old_mask = os.path.join(os.path.join(src_dir, child_dir), 'label.png')
    new_mask = os.path.join(dest_dir, new_name)
    shutil.copyfile(old_mask,new_mask)