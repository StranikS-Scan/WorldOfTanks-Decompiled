# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FragPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FragPanelMeta(BaseDAAPIComponent):

    def as_setLeftFieldS(self, info):
        return self.flashObject.as_setLeftField(info) if self._isDAAPIInited() else None

    def as_setRightFieldS(self, info):
        return self.flashObject.as_setRightField(info) if self._isDAAPIInited() else None
