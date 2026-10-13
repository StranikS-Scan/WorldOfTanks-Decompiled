# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/PortalMine.py
from BasicMine import BasicMine

class PortalMine(BasicMine):

    def onLeaveWorld(self):
        if self.gameObject is not None:
            self.gameObject.detonate()
        super(PortalMine, self).onLeaveWorld()
        return
