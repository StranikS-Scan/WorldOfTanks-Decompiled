# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/listener.py
from gui.prb_control import prbDispatcherProperty, prbEntityProperty

class IPrbListener(object):
    """
    Base prebattle listener class.
    """

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @prbEntityProperty
    def prbEntity(self):
        return None

    def startPrbListening(self):
        """
        Start prebattle events listening.
        """
        self.prbEntity.addListener(self)

    def stopPrbListening(self):
        """
        Stop prebattle events listening.
        """
        if self.prbEntity is not None:
            self.prbEntity.removeListener(self)
        return
