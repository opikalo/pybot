import Queue
import threading

import numpy as np
import time

from matplotlib import cm, use
use("qt4agg")

from matplotlib.pylab import subplots,close
import matplotlib.pyplot as pp



def randomwalk(dims=(256,256),n=20,sigma=5,alpha=0.95,seed=1):
    """ A simple random walk with memory """

    r,c = dims
    gen = np.random.RandomState(seed)
    pos = gen.rand(2,n)*((r,),(c,))
    old_delta = gen.randn(2,n)*sigma

    while 1:

        delta = (1.-alpha)*gen.randn(2,n)*sigma + alpha*old_delta
        pos += delta
        for ii in xrange(n):
            if not (0. <= pos[0,ii] < r) : pos[0,ii] = abs(pos[0,ii] % r)
            if not (0. <= pos[1,ii] < c) : pos[1,ii] = abs(pos[1,ii] % c)
        old_delta = delta
        yield pos

def make_data(q):
    rw = randomwalk()
    while True:
        x,y = rw.next()

        q.put([x,y])


def run(q, niter=1000,doblit=True):
    """
    Visualise the simulation using matplotlib, using blit for 
    improved speed
    """

    fig,ax = subplots(1,1)
    ax.set_aspect('equal')
    ax.set_xlim(0,255)
    ax.set_ylim(0,255)
    ax.hold(True)

    x,y = q.get()
    fig.canvas.draw()

    fig.show()

    mngr = pp.get_current_fig_manager()

    mngr.window.setGeometry(10,10,640, 545)

    if doblit:

        # cache the background
        background = fig.canvas.copy_from_bbox(ax.bbox)

    plt = ax.plot(x,y,'o')[0]
    tic = time.time()

    for ii in xrange(niter):

        # update the xy data
        x,y = q.get()
        plt.set_data(x,y)

        if doblit:

            # restore background
            fig.canvas.restore_region(background)

            # redraw just the points
            ax.draw_artist(plt)

            # fill in the axes rectangle
            fig.canvas.blit(ax.bbox)

        else:

            # redraw everything
            fig.canvas.draw()

    close(fig)
    print "Blit = %s, average FPS: %.2f" %(
           str(doblit),niter/(time.time()-tic))


if __name__ == '__main__':

    q = Queue.Queue(maxsize=1)
    t = threading.Thread(target=make_data, args = (q,))
    t.daemon = True
    t.start()
    run(q)
