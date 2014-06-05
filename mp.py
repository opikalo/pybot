from multiprocessing import Process, Queue,Lock
import time

import matplotlib
matplotlib.use("qt4agg")

from matplotlib.pylab import subplots,close
from matplotlib import cm
from quick_grab import HarpoonLagoon

import pylab


def g(q, l):
    hl = HarpoonLagoon(q, l)
    hl.run()

def display(q, l):
    fig, ax = subplots(1,1)
    ax.set_aspect('equal')    
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 500)
    ax.hold(True)
    fig.canvas.draw()

    
    # cache the background
    background = fig.canvas.copy_from_bbox(ax.bbox)

    plt = ax.plot([0],[0],'o')[0]

    fig.show()

    while True:
        #l.acquire()
        x,y = q.get()
        #print "received", x,y
        #l.release()

        plt.set_data(x,y)

        if True:
            # restore background
            fig.canvas.restore_region(background)

            # redraw just the points
            ax.draw_artist(plt)

            # fill in the axes rectangle
            fig.canvas.blit(ax.bbox)

        else:
            fig.canvas.draw()

    close(fig)

if __name__ == '__main__':

    lock = Lock()
    coord_queue = Queue()
    p1 = Process(target=g, args=(coord_queue, lock))
    p2 = Process(target=display, args=(coord_queue, lock))
    p1.start()
    p2.start()

    p1.join()
    p2.join()
