import ImageGrab
import logging
import os
import time

import timeit

import numpy
import cv, cv2
import win32api,win32con


import time
import matplotlib
matplotlib.use("qt4agg")

from matplotlib.pylab import subplots,close
from matplotlib import cm
import pylab

class Error(Exception):
    pass

class NoGameScreenFound(Error):
    pass

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def find_best_image(img_rgb, template):
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    w, h = template.shape[::-1]
    
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    return (max_loc[0], max_loc[1], max_loc[0] + w, max_loc[1] + h)

def find_images(img_rgb, template, threshold = 0.8):
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = numpy.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        yield (pt[0], pt[1], pt[0] + w, pt[1] + h)
        #cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

    #cv2.imwrite('res.png', img_rgb)

def screen_stream(box):
    pil_image = ImageGrab.grab(box).convert('RGB')
    cv_im = numpy.array(pil_image) 
    cv_im = cv_im[:, :, ::-1].copy() 

    return cv_im


def screen_grab(template, save=False, save_name=''):
    #box = (157,346,796,825)
    #im = ImageGrab.grab(box)

    pil_image = ImageGrab.grab().convert('RGB')
    cv_im = numpy.array(pil_image) 

    cv_im = cv_im[:, :, ::-1].copy() 

    box = find_best_image(cv_im, template)

    if save:
        top_left = (box[0], box[1])
        bottom_right = (box[2], box[3])
    
        cv2.rectangle(cv_im, top_left, bottom_right, 255, 2)

        cv2.imwrite(save_name, cv_im)

    return box



class HarpoonLagoon(object):
    def __init__(self):
        #determine initial dimension of the game
        start_template = cv2.imread('game_snapshot.png', 0)
        self.box = screen_grab(start_template)
        logger.info("found bounding box %s", self.box)

        self.x_pad = self.box[0]
        self.y_pad = self.box[1]

        self.t1 = cv2.imread('large_tuna.png', 0)
        self.t2 = numpy.fliplr(self.t1)
        
        self.p1 = cv2.imread('large_pleco.png', 0)
        self.p2 = numpy.fliplr(self.p1)

        self.display_setup()

        self.start_fishing()

    def display_setup(self):
        self.fig, self.ax = subplots(1,1)
        self.ax.set_aspect('equal')

        self.ax.set_xlim(0,600)
        self.ax.set_ylim(0,500)
        self.ax.hold(True)
        self.fig.canvas.draw()


        # cache the background
        self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)

        self.plt = self.ax.plot([300],[250],'o')[0]

        pylab.ion()

    def show_pos(self,x,y):
        self.plt.set_data(x,y)

        # restore background
        self.fig.canvas.restore_region(self.background)

        # redraw just the points
        self.ax.draw_artist(self.plt)

        # fill in the axes rectangle
        self.fig.canvas.blit(self.ax.bbox)

        pylab.show()
        time.sleep(1)

    def start_fishing(self):
        self.mouse_pos(300, 333)
        self.left_click()

    def find_large_tuna(self):
        pos_x = []
        pos_y = []
        for t in [self.t1,]: # self.p1
            for tuna in find_images(self.snapshot, t, 0.6):
                pos_x.append(tuna[0])
                pos_y.append(tuna[1])
                #self.mouse_pos(tuna[0], tuna[1])

                # if tuna[0] < 300:
                #     logger.debug("fire, fish at %s", tuna[0])
                
                #     self.fire()

        # for t in [self.t2, self.p2]:
        #     for tuna in find_images(self.snapshot, t, 0.6):
        #         pos_x.append(tuna[0])
        #         pos_y.append(tuna[1])

        #         #self.mouse_pos(tuna[0], tuna[1])

        #         if tuna[0] > 250:
        #             logger.debug("fire, fish at %s", tuna[0])

        #             self.fire()

        self.show_pos(pos_x, pos_y)
            
    def run(self):
        while True:
            start_time = timeit.default_timer()
            self.snapshot = screen_stream(self.box)
            self.find_large_tuna()
            
            #self.fire()
            elapsed = timeit.default_timer() - start_time
            time.sleep(1)
            print elapsed
            
            
    def left_click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
        time.sleep(.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

    def fire(self):
        win32api.keybd_event(win32con.VK_SPACE, 0, 
                             0, 0)
        time.sleep(.1)
        win32api.keybd_event(win32con.VK_SPACE, 0,
                             win32con.KEYEVENTF_KEYUP ,0)

    def mouse_pos(self, x, y):
        win32api.SetCursorPos((self.x_pad + x, self.y_pad + y))
     
    def get_cords(self):
        x, y = win32api.GetCursorPos()
        x = x - self.x_pad
        y = y - self.y_pad
        print x, y
                          
def main():
    hl = HarpoonLagoon()

    hl.run()
    #while True:
    #    hl.get_cords()
 
if __name__ == '__main__':
    main()
