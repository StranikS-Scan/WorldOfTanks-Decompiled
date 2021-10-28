# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBanInfoMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventBanInfoMeta(BaseDAAPIComponent):

    def as_setEventBanInfoS(self, data):
        return self.flashObject.as_setEventBanInfo(data) if self._isDAAPIInited() else None

    def as_setVisibleS(self, value):
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None
