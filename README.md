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
* 需要做一個3d reconstuction 的演算法 結合maskrcnn
* Utils裡面還需要補上json_to_dataset檔案、以及 取出mask的png檔案存到cv2_mask folder裡面
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
