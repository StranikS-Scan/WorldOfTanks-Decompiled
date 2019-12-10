# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class NewYearRewardsViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onSwitchContent')

    def __init__(self, properties=3, commands=2):
        super(NewYearRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getItemsTabBar(self):
        return self._getArray(0)

    def setItemsTabBar(self, value):
        self._setArray(0, value)

    def getStartIndex(self):
        return self._getNumber(1)

    def setStartIndex(self, value):
        self._setNumber(1, value)

    def getBgChangeViewName(self):
        return self._getString(2)

    def setBgChangeViewName(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(NewYearRewardsViewModel, self)._initialize()
        self._addArrayProperty('itemsTabBar', Array())
        self._addNumberProperty('startIndex', 0)
        self._addStringProperty('bgChangeViewName', '')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onSwitchContent = self._addCommand('onSwitchContent')
