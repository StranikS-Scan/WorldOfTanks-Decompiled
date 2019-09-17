# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FestivalRacePlayerHealthBarMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FestivalRacePlayerHealthBarMeta(BaseDAAPIComponent):

    def as_updateHealthS(self, healthStr, progress):
        return self.flashObject.as_updateHealth(healthStr, progress) if self._isDAAPIInited() else None
