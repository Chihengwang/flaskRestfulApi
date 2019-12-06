"""
In this file, you can set up the config of your own camera!
From my application, I use realsense d435 as my camera so I can easliy
find out the parameters from the SDK.
"""

cx = 316.001
cy = 244.572
fx = 616.391
fy = 616.819
scalingfactor = 0.0010000000474974513
"""
After Hand eye calibration, you can find out the hand-eye transformation matrix.
Please include this file into your restapi_server_rgbd.py so that you can use this matrix
to transform your points into base frame.
"""
# Unit: Meter
import numpy as np
HAND_EYE_TFMATRIX=np.array([
    [0,-1,0,0.11865],
    [1,0,0,-0.035 ],
    [0,0,1,0.018],
    [0,0,0,1]
])
class RGBDCamera():
    def __init__(self, centerx=cx,centery=cy,focalx=fx,focaly=fy,scalingfactor=scalingfactor):
        self.cx =centerx
        self.cy=centery
        self.fx=focalx
        self.fy=focaly
        self.scalingfactor=scalingfactor

