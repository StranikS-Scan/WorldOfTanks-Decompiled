# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HalloweenPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HalloweenPanelMeta(BaseDAAPIComponent):

    def as_updateLeviathanProgressS(self, progress):
        return self.flashObject.as_updateLeviathanProgress(progress) if self._isDAAPIInited() else None

    def as_setObjectiveMsgS(self, msg):
        return self.flashObject.as_setObjectiveMsg(msg) if self._isDAAPIInited() else None
