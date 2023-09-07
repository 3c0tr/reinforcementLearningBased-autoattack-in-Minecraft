import argparse
from sys import platform
import pygetwindow as gw

from models import *  # set ONNX_EXPORT in models.py
from utils.datasets import *
from utils.utils import *
import numpy as np
import cv2
from PIL import ImageGrab
import time
from PIL import Image

class mygame:
    def __init__(self):
        super().__init__()
        parser = argparse.ArgumentParser()
        parser.add_argument('--cfg', type=str, default='cfg/yolov3-tiny-3cls.cfg', help='*.cfg path')
        parser.add_argument('--names', type=str, default='data/classes.names', help='*.names path')
        parser.add_argument('--weights', type=str, default='weights/best.pt', help='weights path')
        parser.add_argument('--source', type=str, default='data/co', help='source')  # input file/folder, 0 for webcam
        parser.add_argument('--output', type=str, default='output', help='output folder')  # output folder
        parser.add_argument('--img-size', type=int, default=208, help='inference size (pixels)')
        parser.add_argument('--conf-thres', type=float, default=0.3, help='object confidence threshold')
        parser.add_argument('--iou-thres', type=float, default=0.6, help='IOU threshold for NMS')
        parser.add_argument('--fourcc', type=str, default='mp4v', help='output video codec (verify ffmpeg support)')
        parser.add_argument('--half', action='store_true', help='half precision FP16 inference')
        parser.add_argument('--device', default='', help='device id (i.e. 0 or 0,1) or cpu')
        parser.add_argument('--view-img', action='store_true', help='display results')
        parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
        parser.add_argument('--classes', nargs='+', type=int, help='filter by class')
        parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
        self.opt = parser.parse_args()
        img_size = (320, 192) if ONNX_EXPORT else self.opt.img_size
        weights = self.opt.weights
        view_img = self.opt.view_img
        # Initialize
        self.device = torch_utils.select_device(device='cpu' if ONNX_EXPORT else self.opt.device)
        model0 = Darknet(self.opt.cfg, img_size)
        self.model=model0
        attempt_download(weights)
        if weights.endswith('.pt'):  # pytorch format
            self.model.load_state_dict(torch.load(weights, map_location=self.device)['model'])
            self.model.to(self.device).eval()
        else:  # darknet format
            load_darknet_weights(self.model, weights)


    def pred(self,myimg):

        half = self.opt.half
        half = half and self.device.type != 'cpu'

        # Get names and colors
        names = load_classes(self.opt.names)
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]

        # Eval mode
        # Half precision
        if half:
            self.model.half()

        # Get names and colors
        names = load_classes(self.opt.names)
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]

        # Run inference
        t0 = time.time()

        img_size = 416
        img0 = myimg
        # Padded resize
        img = letterbox(img0, new_shape=img_size)[0]

        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)

        img = torch.from_numpy(img).to(self.device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = torch_utils.time_synchronized()
        pred = self.model(img)[0].float() if half else self.model(img)[0]
        t2 = torch_utils.time_synchronized()

        # Apply NMS
        pred = non_max_suppression(pred, self.opt.conf_thres, self.opt.iou_thres, classes=self.opt.classes, agnostic=self.opt.agnostic_nms)

        return pred


#with torch.no_grad():
    # path ='./data/co/1668948627620.jpg'

#   myimg = cv2.imread('C:/Users/17617/Desktop/jvav/MC_data/1668948627620.jpg')
#    game=mygame()
#    cnt = 0
#    while True:
#        if gw.getActiveWindowTitle().find("Minecraft") != -1:
#            minecraft = gw.getActiveWindow()
#           print(minecraft.box)
#            #pred = game.pred(myimg)
#            #print(pred)
