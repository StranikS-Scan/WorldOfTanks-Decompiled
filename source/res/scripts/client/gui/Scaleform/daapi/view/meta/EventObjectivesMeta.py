# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventObjectivesMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventObjectivesMeta(BaseDAAPIComponent):

    def as_showS(self):
        return self.flashObject.as_show() if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None

    def as_setMainTextS(self, title, descr):
        return self.flashObject.as_setMainText(title, descr) if self._isDAAPIInited() else None

    def as_setTimeS(self, time):
        return self.flashObject.as_setTime(time) if self._isDAAPIInited() else None
