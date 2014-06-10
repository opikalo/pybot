import sys

from twisted.python import log
from twisted.internet.endpoints import clientFromString
from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.choosereactor import install_reactor
from autobahn.twisted import wamp, websocket
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.wamp import ApplicationSessionFactory
from autobahn.wamp import types
from autobahn.twisted.websocket import WampWebSocketClientFactory

class Component(ApplicationSession):
   """
   An application component that publishes an event every second.
   """

   @inlineCallbacks
   def onJoin(self, details):
      counter = 0
      while True:
         self.publish('com.myapp.topic1', counter)
         counter += 1
         yield sleep(1)


   def onDisconnect(self):
       reactor.stop()


if __name__ == '__main__':

    end_point = "tcp:127.0.0.1:8080"

    debug = False

    if debug:
        log.startLogging(sys.stdout)


    ## we use an Autobahn utility to import the "best" available Twisted reactor
    ##

    reactor = install_reactor()
    print("Running on reactor {}".format(reactor))


    ## create a WAMP application session factory
    ##
    session_factory = ApplicationSessionFactory(types.ComponentConfig(realm = "realm1"))


    ## .. and set the session class on the factory
    ##
    session_factory.session = Component


    ## create a WAMP-over-WebSocket transport client factory
    ##

    transport_factory = WampWebSocketClientFactory(session_factory, 
                                                   debug_wamp = debug)
    transport_factory.setProtocolOptions(failByDrop = False)

    ## start the client from an endpoint
    ##
    client = clientFromString(reactor, end_point)
    client.connect(transport_factory)

    ## now enter the Twisted reactor loop
    ##
    reactor.run()
