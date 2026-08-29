# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/meta/WTMissileWidgetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class WTMissileWidgetMeta(BaseDAAPIComponent):

    def as_setRangeS(self, value):
        return self.flashObject.as_setRange(value) if self._isDAAPIInited() else None

    def as_setAltitudeS(self, value):
        return self.flashObject.as_setAltitude(value) if self._isDAAPIInited() else None

    def as_setMaxAltitudeS(self, value):
        return self.flashObject.as_setMaxAltitude(value) if self._isDAAPIInited() else None

    def as_showS(self, useAnim=False):
        return self.flashObject.as_show(useAnim) if self._isDAAPIInited() else None

    def as_hideS(self, useAnim=False):
        return self.flashObject.as_hide(useAnim) if self._isDAAPIInited() else None
