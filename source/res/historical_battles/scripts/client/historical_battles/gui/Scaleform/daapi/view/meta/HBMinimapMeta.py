# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/meta/HBMinimapMeta.py
from gui.Scaleform.daapi.view.meta.EpicMinimapMeta import EpicMinimapMeta

class HBMinimapMeta(EpicMinimapMeta):

    def as_setTabModeS(self, value):
        return self.flashObject.as_setTabMode(value) if self._isDAAPIInited() else None
