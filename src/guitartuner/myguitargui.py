from tkinter import *
import sys, os
import numpy as np
from tkinter import *
from pdb import set_trace as tr
import time
import random
from queue import Queue, Empty
from threading import Thread
import pathlib

if sys.platform == 'linux':
    from guitartuner._guitartuner import measureFrequency
else:
    from guitartuner._guitartuner_windows import measureFrequency

def startTuner():

    width = 300
    height = width//2
    margin = 5
    centerx, centery = width//2, height - 2 * margin
    r = width - margin
    r = 100
    thetas = 0; thetae = 180 # start, stop
    N = 23 # 1 + 10 + 1 + 10 + 1
    thetapieces = np.linspace(thetas, thetae, N) * np.pi / 180 # in radians
    # 10 divisions on each side 
    # including 3 big ones - 10 + 10 + 3
    x = r * np.cos(thetapieces)
    y = r * np.sin(thetapieces)
    # correcting with center co-ordinates
    x = centerx + x
    y = centery - y
    root = Tk()
    root.title('Guitar Tuner')
    #iconpath = os.path.abspath('iconguitar.png')
    curdir = pathlib.Path(__file__).parent.resolve()
    iconpath = os.path.join(curdir, 'iconguitar.png')
    icon = PhotoImage(file=iconpath)
    root.iconphoto(False, icon)
    root.geometry(str(width+50)+'x'+str(height+50))
    can = Canvas(root, width=width, height=height)
    can.pack(side=TOP)
    Button(root, text='Quit', command=sys.exit).pack(side=TOP)
    thetamains = np.array([0, 90, 180]) * np.pi/180
    # 0, 90 , 180 @ 0, 1, 2
    X = r * np.cos(thetamains)
    Y = r * np.sin(thetamains)
    X = centerx + X; Y = centery - Y
    que = Queue()
    def producer():
        #while True:
        #    time.sleep(1)
        #    que.put(random.choice(range(len(x))))
        measureFrequency(que)
    Thread(target=producer, daemon=True).start()
    # last data initialization
    prevdata = [(1, '-'), (2, '-'), (4, '-'), (4, 2)]
    def drawtuner(endx, endy):
        nonlocal prevdata
        can.delete('all')
        for i, j in zip(x, y):
            can.create_oval(i, j, i+2, j +2)
        # three notes - thetas 0, 90, 180
        for i, j in zip(X, Y):
            can.create_oval(i-4, j-4, i+5, j +5)
        # center circle
        can.create_oval(centerx-1, centery-1, centerx+1, centery+1)
        # needle
        can.create_line(centerx, centery, endx, endy, arrow=LAST)
        try:
            data = que.get(block=False)
            prevdata = data
            #print('data: -->', data)
        except Empty:
            #data = [(1, '-'), (2, '-'), (4, '-'), (4, 2)]
            data = prevdata
        # data extraction
        lf, lnote = data[0][0], data[0][1]
        mf, mnote = data[1][0], data[1][1]
        hf, hnote = data[2][0], data[2][1]
        avfreq, drange = data[3][0], data[3][1]
        # data conversion - to canvas - logic
        if data[3][1] == 1: # avfreq in 180-90
            thetaf = 180 + ((90 - 180)/(mf - lf)) * (avfreq - lf)
            thetaf *= np.pi/180  # in radians
        else: 
            thetaf = 90 + ((0 - 90)/(hf - mf)) * (avfreq - mf)
            thetaf *= np.pi/180 # in radians
        # for out of range values
        #if thetaf > np.pi/2: thetaf = 0
        # need head for avfreq
        xf = r * np.cos(thetaf)
        yf = r * np.sin(thetaf)
        # correcting for center
        xf = centerx + xf
        yf = centery - yf
        # note labels in reverse order
        can.create_text(X[0] + 25, Y[0], text=data[2][1])
        can.create_text(X[1], Y[1]-25, text=data[1][1])
        can.create_text(X[2] - 25, Y[2], text=data[0][1])
        choice = 0
        #print(data)
        can.after(10, lambda : drawtuner(xf, yf))
    drawtuner(X[0], Y[0])
    mainloop()

if __name__ == '__main__':
    startTuner()
