# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/subscriptions.py
from gui.clans.interfaces import IClanListener
from gui.shared.utils.listeners_collection import ListenersCollection

class WebListeners(ListenersCollection):

    def __init__(self):
        super(WebListeners, self).__init__()
        self._setListenerClass(IClanListener)

    def notify(self, eventType, *args):
        self._invokeListeners(eventType, *args)

    def addListener(self, listener):
        if not self.hasListener(listener):
            super(WebListeners, self).addListener(listener)

    def getListenersIterator(self):
        return list(super(WebListeners, self).getListenersIterator())
