# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PvEWinLosePanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PvEWinLosePanelMeta(BaseDAAPIComponent):

    def as_setCombatEndStateS(self, data):
        """
        :param data: Represented by PvEWinLoseVO (AS)
        """
        return self.flashObject.as_setCombatEndState(data) if self._isDAAPIInited() else None
