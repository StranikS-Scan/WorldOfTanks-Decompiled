# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/meta/ExampleHangarWidgetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ExampleHangarWidgetMeta(BaseDAAPIComponent):

    def as_showSomeDataS(self, message, iconSource):
        return self.flashObject.as_showSomeData(message, iconSource) if self._isDAAPIInited() else None

    def as_setVisibilityS(self, isVisible):
        return self.flashObject.as_setVisibility(isVisible) if self._isDAAPIInited() else None
