import logging
from multiprocessing import Process, Queue, Lock
import sys
import time

from Queue import Empty

from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.util import sleep

from pubsub_boiler import init_pubsub

from quick_grab import HarpoonLagoon

logger = logging.getLogger(__name__)


class Component(ApplicationSession):
   """
   An application component that publishes an event from the queue every second
   """

   queue = None

   @inlineCallbacks
   def onJoin(self, details):
       if not self.factory._myAppSession:
           self.factory._myAppSession = self

       while True:
           try:
               data = self.queue.get_nowait()
               print "published", data
               self.publish('com.myapp.topic1', data)
           except Empty:
               pass

           yield sleep(1)

   def onLeave(self, details):
       if self.factory._myAppSession == self:
           self.factory._myAppSession = None


   def onDisconnect(self):
       reactor.stop()


class Publisher:
    def __init__(self, queue, lock):
        self.reactor, self.session_factory = init_pubsub(Component, queue)
        #print "publisher session_factory", self.session_factory

    def run(self):
        ## now enter the Twisted reactor loop
        self.reactor.run()


def publisher_func(queue, lock):
    p = Publisher(queue, lock)
    p.run()
    

def generator_func(queue, lock):

    hl = HarpoonLagoon(queue, lock)
    hl.run()


    counter = 0 
    while True:
        data = [
            ['x', 'y1', 'y2' ],
            [ counter, counter, None],
            [ counter + 10, None, counter + 10]
            ]

        queue.put(data)

        #print "session_factory", session_factory
        # if session_factory:
        #     if session_factory._myAppSession:
        #         print "published", data

        #         session_factory._myAppSession.publish('com.myapp.topic1', data)
        #     else:
        #         print("no session")


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
