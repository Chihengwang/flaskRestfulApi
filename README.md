# flaskRestfulApi
Flask restful api

### 需要的套件有

* python-opencv
* flask


### 主要實現的功能:

> api v1.0 實現的功能：
>>* 從不同裝置藉由POST傳送資料給api server
>>* 藉由遠端的控制進行拍照的功能



-------------------------

### TODOLIST:

* 實測軌跡規劃以及POST的功能(V)
* 開始訓練資料(V)
* Utils裡面還需要補上json_to_dataset檔案、以及 取出mask的png檔案存到cv2_mask folder裡面(V)
* 完成IK FK function 並且測試(V)
* 需要做一個3d reconstuction 的演算法 結合maskrcnn,將model.detect的部份融入partial point cloud detect algorithm
--------------------------
### Updated logs

>2019/9/19
>>* 完成軌跡規劃測試且拍照的功能
>>* 新增兩條route 用來開啟/關閉RGBD的相機，以避免shutdown的問題
>>
>2019/10/6
>>* 新增一個照片排序的py檔案(Utils/maskrcnn_dataset_dealer.py)
>>主要可以將照片排序到1...n 有新增的照片也會直接以最大的數字進行排序
>>先cd 進去utils目錄下，執行 python maskrcnn_dataset_dealer.py將可以進行排序
>>* 測試了global variable是否能夠被action 影響。結論是可以的!!!
>>
>2019/10/7
>>* 更改了ubuntu裡面labelme json_to_dataset的檔案，並且測試了批量轉檔
>>  使用方法就是在 env 的cmd cd到json的當前目錄 輸入 `labelme_json_to_dataset ./` 即可看到結果
>>* 新增了move_to_maskfolder.py檔案 主要將每個json裡面的label.png移動到cv2_mask的資料夾裡面
>>* 準備資料的流程：
>>  1. 收資料
>>  2. 用 maskrcnn_dataset_dealer.py 排序資料
>>  3. 用labelme 一張張標註並且產生json file存入 dataset/json folder 裡面
>>  4. 在cmd裡面 cd到dataset/json 並且輸入`labelme_json_to_dataset ./`
>>  5. 將批量的json folder 存到 labelme_json的folder裡面 並在cd utils 執行 `python move_to_maskfolder.py`
>>
>2019/10/10
>>* successfully test train.py and fortest.py on MaskRCNN, which is cloned from [MaskRCNN](https://github.com/matterport/Mask_RCNN) 
>> As I mentioned above, we can use the python scripts above to make your own dataset.
>>* `tensorboard -logdir=logs/path_to_newest_weights` can take a look at your result from training data including validation
>> dataset.
>>* In Models/MaskRCNN/samples/mydataset/graspingitem folder, I provide the labeled data including original picture, json file
>> (from Labelme software), json folder(from labelme_json_to_dataset script), mask folder(from move_to_maskfolder.py script)
>>
>2019/10/24
>>* complete forword kinematic and inverse kinematic function of the RA605 and provide testing data below.
>> You can verify the validation of the t0_6 and t0_6_ik. If true, then our result is correct.
>>* integrate the arm_kinematic file into restapi_server file and successfully examine the correction of the process.
>>
>2019/12/01
>>* 完成multithread的測試(成功),放棄start detector的寫法(因為有GPU RAM 無法釋放的問題)
>>* 完成get_photo_and_mask的route用來處理拍照並偵測mask 假如沒有return None 且不會append進去list
>>* 新增check image number用來停止labview端的動作
>>* [x] 仍須要完成ply檔案的儲存
>>* [x] 完善收取6DOF的資料