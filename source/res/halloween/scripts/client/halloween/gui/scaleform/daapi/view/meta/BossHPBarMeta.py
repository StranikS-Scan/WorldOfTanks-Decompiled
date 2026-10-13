# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/meta/BossHPBarMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BossHPBarMeta(BaseDAAPIComponent):

    def as_setVisibleS(self, value):
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None

    def as_setLockedS(self, value):
        return self.flashObject.as_setLocked(value) if self._isDAAPIInited() else None

    def as_setMaxLivesS(self, value, difficulty, info):
        return self.flashObject.as_setMaxLives(value, difficulty, info) if self._isDAAPIInited() else None

    def as_setLivesS(self, value):
        return self.flashObject.as_setLives(value) if self._isDAAPIInited() else None

    def as_setBossHPS(self, label, progress):
        return self.flashObject.as_setBossHP(label, progress) if self._isDAAPIInited() else None

    def as_setShieldsS(self, value):
        return self.flashObject.as_setShields(value) if self._isDAAPIInited() else None
