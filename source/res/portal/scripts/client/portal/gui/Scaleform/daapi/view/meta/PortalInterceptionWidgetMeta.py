# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/meta/PortalInterceptionWidgetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PortalInterceptionWidgetMeta(BaseDAAPIComponent):

    def as_updateTimeS(self, seconds):
        return self.flashObject.as_updateTime(seconds) if self._isDAAPIInited() else None
