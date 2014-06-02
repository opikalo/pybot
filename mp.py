from multiprocessing import Process, Queue,Lock
import time

import matplotlib
matplotlib.use("qt4agg")


from matplotlib.pylab import subplots,close
from matplotlib import cm
import pylab


def g(q, l):
    for i in range(600):
        if not q.full():
            l.acquire()
            print "sending", i
            l.release()
            q.put([[i],[i]])

    time.sleep(10)

def display(q, l):
    fig, ax = subplots(1,1)
    ax.set_aspect('equal')
    
    ax.set_xlim(0,600)
    ax.set_ylim(0,500)
    ax.hold(True)
    fig.canvas.draw()

    # cache the background
    background = fig.canvas.copy_from_bbox(ax.bbox)
    
    plt = ax.plot([300],[250],'o')[0]
    fig.show()

    while True:
        if not q.empty():
            l.acquire()
            x,y = q.get()
            print "received", x,y
            l.release()

            plt.set_data(x,y)

            if True:
                # restore background
                fig.canvas.restore_region(background)

                # redraw just the points
                ax.draw_artist(plt)

                # fill in the axes rectangle
                fig.canvas.blit(ax.bbox)

                time.sleep(0.02)
            else:
                fig.canvas.draw()
                fig.show()
                    

        else:
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
