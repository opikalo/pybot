import logging
from multiprocessing import Process, Queue, Lock
import sys
import time

from Queue import Empty

from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.util import sleep

from pubsub_boiler import init_pubsub

logger = logging.getLogger(__name__)


class Component(ApplicationSession):
   """
   An application component that publishes an event from the queue every second
   """

   queue = None

   @inlineCallbacks
   def onJoin(self, details):
       while True:
           try:
               data = self.queue.get_nowait()
               self.publish('com.myapp.topic1', data)
           except Empty:
               pass

           yield sleep(0.1)

   def onDisconnect(self):
       reactor.stop()


class Publisher:
    def __init__(self, queue, lock):
        self.reactor = init_pubsub(Component, queue)

    def run(self):
        ## now enter the Twisted reactor loop
        self.reactor.run()


def publisher_func(queue, lock):
    p = Publisher(queue, lock)
    p.run()
    

def generator_func(queue, lock):
    counter = 0 
    while True:
        data = [
            ['x', 'y1', 'y2' ],
            [ counter, counter, None],
            [ counter + 10, None, counter + 10]
            ]

        print "sending", data
        queue.put(data)
        counter += 1
        counter = counter % 500
        time.sleep(.1)

if __name__ == '__main__':

    queue = Queue()
    lock = Lock()
    publisher_proc = Process(target=publisher_func, args=(queue, lock))

    data_proc = Process(target=generator_func, args=(queue, lock))

    publisher_proc.start()
    data_proc.start()

    publisher_proc.join()
    data_proc.join()
