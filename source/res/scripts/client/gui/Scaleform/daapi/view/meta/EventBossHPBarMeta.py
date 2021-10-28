# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBossHPBarMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventBossHPBarMeta(BaseDAAPIComponent):

    def as_setPhaseS(self, value):
        return self.flashObject.as_setPhase(value) if self._isDAAPIInited() else None

    def as_setBossHPS(self, label, progress):
        return self.flashObject.as_setBossHP(label, progress) if self._isDAAPIInited() else None

    def as_setVisibleS(self, vis):
        return self.flashObject.as_setVisible(vis) if self._isDAAPIInited() else None
