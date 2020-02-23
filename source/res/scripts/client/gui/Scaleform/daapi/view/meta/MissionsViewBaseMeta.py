# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MissionsViewBaseMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MissionsViewBaseMeta(BaseDAAPIComponent):

    def dummyClicked(self, clickType):
        self._printOverrideError('dummyClicked')

    def as_showDummyS(self, data):
        return self.flashObject.as_showDummy(data) if self._isDAAPIInited() else None

    def as_hideDummyS(self):
        return self.flashObject.as_hideDummy() if self._isDAAPIInited() else None

    def as_setWaitingVisibleS(self, visible):
        return self.flashObject.as_setWaitingVisible(visible) if self._isDAAPIInited() else None

    def as_setBackgroundS(self, source):
        return self.flashObject.as_setBackground(source) if self._isDAAPIInited() else None
