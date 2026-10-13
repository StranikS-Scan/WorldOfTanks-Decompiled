# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/meta/ExampleBattleWidgetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ExampleBattleWidgetMeta(BaseDAAPIComponent):

    def as_showSomeDataS(self, data):
        return self.flashObject.as_showSomeData(data) if self._isDAAPIInited() else None
