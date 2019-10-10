"""
這個工具主要是用來處理restful api 儲存的照片數據
收到資訊後 先對照片做排序及檢查順序
要訓練的資料目前會存在Maskrcnn/samples/mydataset/graspingitem/pic裡面
"""
import os
import glob
"""
"""
def change_file_name(path):
    # root path
    root_path = os.path.abspath(os.path.dirname(os.getcwd()))
    print("Root path is "+root_path)
    path=root_path+"/"+path
    print(path)
    if os.path.isdir(path):
        count=1
        # get root work path
        current_working_path=os.getcwd()
        print("Current path:"+os.getcwd())
        # change current work path
        os.chdir(path)
        print("Current path:"+os.getcwd())
        # 假如已經有file name是數字，找最大數字
        file_list=glob.glob(r'[0-9]*.png')
        get_number_list=[int(file_name.split('.')[0].strip()) for file_name in file_list]
        # 處理新進來的圖片
        if(file_list):
            max_index=max(get_number_list)
            count=max_index+1
            file_list2=glob.glob(r'*.png')
            other_file_list2=[file_name for file_name in file_list2 if file_name not in file_list]
            for name in other_file_list2:
                os.rename(name,str(count)+'.png')
                count+=1
        # 假如都沒有數字的圖片
        else:
            count=1
            for name in glob.iglob('./*'):
                os.rename(name,str(count)+'.png')
                count+=1
        os.chdir(current_working_path)
    else:
        raise NameError('Check your path!!')

if __name__=='__main__':

    ModelPath='Models/MaskRCNN/samples/mydataset/graspingitem/pic'
    change_file_name(ModelPath)