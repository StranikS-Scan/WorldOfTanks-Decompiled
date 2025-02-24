# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RocketAcceleratorIndicatorMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class RocketAcceleratorIndicatorMeta(BaseDAAPIComponent):

    def as_setStateS(self, state):
        return self.flashObject.as_setState(state) if self._isDAAPIInited() else None

    def as_setVisibleS(self, visible):
        return self.flashObject.as_setVisible(visible) if self._isDAAPIInited() else None

    def as_setCountS(self, count):
        return self.flashObject.as_setCount(count) if self._isDAAPIInited() else None

    def as_setProgressS(self, progress):
        return self.flashObject.as_setProgress(progress) if self._isDAAPIInited() else None

    def as_setActiveTimeS(self, time):
        return self.flashObject.as_setActiveTime(time) if self._isDAAPIInited() else None

    def as_updateLayoutS(self, x, y):
        return self.flashObject.as_updateLayout(x, y) if self._isDAAPIInited() else None
