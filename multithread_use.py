# import multiprocessing


# def func(msg):
#     return multiprocessing.current_process().name + '-' + msg+"fuck"

# if __name__ == "__main__":
#     pool = multiprocessing.Pool(processes=3) # 创建4个进程
#     results = []
#     for i in range(10):
#         msg = "hello %d" %(i)
#         results.append(pool.apply_async(func, (msg, )))
#     pool.close() # 关闭进程池，表示不能再往进程池中添加进程，需要在join之前调用
#     pool.join() # 等待进程池中的所有进程执行完毕
#     print ("Sub-process(es) done.")

#     for res in results:
#         print (res.get())


import time
from multiprocessing import Process,Pool
from flask import Flask

app = Flask(__name__)
list_test=[]

def testFun():
    list_test.append("fuck")
    print('Starting')
    time.sleep(3)
    print('3 Seconds Later')
def _process(msg):
    return msg
@app.route('/')
def root():
    msg="fuck"
    with Pool(1) as p:
        list_test.append(p.apply(_process,(msg,)))
    print(list_test)
    # backProc = Process(target=testFun, args=())
    # backProc.start()
    return 'Started a background process with PID '

if __name__ == '__main__':
    
    app.run(debug=True)