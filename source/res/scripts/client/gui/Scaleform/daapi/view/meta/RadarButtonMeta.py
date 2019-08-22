# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RadarButtonMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class RadarButtonMeta(BaseDAAPIComponent):

    def onClick(self):
        self._printOverrideError('onClick')

    def as_initS(self, keyCode, sfKeyCode, tag, iconPath, tooltipText, isReplay):
        return self.flashObject.as_init(keyCode, sfKeyCode, tag, iconPath, tooltipText, isReplay) if self._isDAAPIInited() else None

    def as_setCoolDownTimeS(self, duration, baseTime, startTime, animation):
        return self.flashObject.as_setCoolDownTime(duration, baseTime, startTime, animation) if self._isDAAPIInited() else None

    def as_updateEnableS(self, isEnabled):
        return self.flashObject.as_updateEnable(isEnabled) if self._isDAAPIInited() else None
