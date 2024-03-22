# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/tooltips/tab_tooltip_view_model.py
from frameworks.wulf import ViewModel

class TabTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(TabTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getTabId(self):
        return self._getString(0)

    def setTabId(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(TabTooltipViewModel, self)._initialize()
        self._addStringProperty('tabId', '')
