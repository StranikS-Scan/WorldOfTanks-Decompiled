# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WTReinforcementPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class WTReinforcementPanelMeta(BaseDAAPIComponent):

    def as_setPlayerLivesS(self, lives):
        return self.flashObject.as_setPlayerLives(lives) if self._isDAAPIInited() else None
