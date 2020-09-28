# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WTEventCarouselWidgetMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class WTEventCarouselWidgetMeta(InjectComponentAdaptor):

    def updateWidgetLayout(self, value):
        self._printOverrideError('updateWidgetLayout')

    def as_showWidgetS(self):
        return self.flashObject.as_showWidget() if self._isDAAPIInited() else None

    def as_hideWidgetS(self):
        return self.flashObject.as_hideWidget() if self._isDAAPIInited() else None
