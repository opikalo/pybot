import logging
from multiprocessing import Process, Queue, Lock
import sys
import time

from Queue import Empty

from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.util import sleep

import matplotlib
from matplotlib.pylab import subplots,close
from matplotlib import cm
import numpy as np
import matplotlib.pyplot as plt


import pylab

from pubsub_boiler import init_pubsub

logger = logging.getLogger(__name__)


class Component(ApplicationSession):
   """
   An application component that subscribes and receives events,
   and stop after having received 5 events.
   """
   queue = None

   @inlineCallbacks
   def onJoin(self, details):

      def on_event(i):
         #print("Got event: {}".format(i))
         self.queue.put(i)

      yield self.subscribe(on_event, 'com.myapp.topic1')


   def onDisconnect(self):
      reactor.stop()

class Subscriber(object):
    def __init__(self, queue, lock):
        self.reactor = init_pubsub(Component, queue)

    def run(self):
        self.reactor.run()


def subscriber_func(queue, lock):
    s = Subscriber(queue, lock)
    s.run()
    

if __name__ == '__main__':

    queue = Queue()
    lock = Lock()
    subscriber_proc = Process(target=subscriber_func, args=(queue, lock))

    subscriber_proc.start()

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
        x,y = queue.get()
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


        time.sleep(.1)


    #subscriber_proc.join()
