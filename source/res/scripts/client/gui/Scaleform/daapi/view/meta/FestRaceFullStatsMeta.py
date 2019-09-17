# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FestRaceFullStatsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FestRaceFullStatsMeta(BaseDAAPIComponent):

    def as_setArenaHeaderInfoS(self, info):
        return self.flashObject.as_setArenaHeaderInfo(info) if self._isDAAPIInited() else None
