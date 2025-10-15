# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/meta/PortalPostmortemPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PortalPostmortemPanelMeta(BaseDAAPIComponent):

    def as_setTimerS(self, time):
        return self.flashObject.as_setTimer(time) if self._isDAAPIInited() else None
