# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_rewards_view_model.py
from frameworks.wulf import ViewModel

class NewYearRewardsViewModel(ViewModel):
    __slots__ = ('onSwitchContent',)

    def __init__(self, properties=2, commands=1):
        super(NewYearRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getBgChangeViewName(self):
        return self._getString(0)

    def setBgChangeViewName(self, value):
        self._setString(0, value)

    def getNextViewName(self):
        return self._getString(1)

    def setNextViewName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(NewYearRewardsViewModel, self)._initialize()
        self._addStringProperty('bgChangeViewName', '')
        self._addStringProperty('nextViewName', '')
        self.onSwitchContent = self._addCommand('onSwitchContent')
