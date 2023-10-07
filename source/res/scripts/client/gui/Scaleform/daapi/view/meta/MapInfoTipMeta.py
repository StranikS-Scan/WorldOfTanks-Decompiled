# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MapInfoTipMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MapInfoTipMeta(BaseDAAPIComponent):

    def as_setEnabledS(self, enabled):
        return self.flashObject.as_setEnabled(enabled) if self._isDAAPIInited() else None
