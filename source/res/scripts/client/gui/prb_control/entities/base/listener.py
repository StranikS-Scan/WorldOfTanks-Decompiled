# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/listener.py
from gui.prb_control import prbDispatcherProperty, prbEntityProperty

class IPrbListener(object):

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @prbEntityProperty
    def prbEntity(self):
        return None

    def startPrbListening(self):
        if self.prbEntity is not None and hasattr(self.prbEntity, 'addListener'):
            self.prbEntity.addListener(self)
        return

    def stopPrbListening(self):
        if self.prbEntity is not None:
            self.prbEntity.removeListener(self)
        return
