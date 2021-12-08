# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_style_reward_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class NewYearStyleRewardViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=3, commands=1):
        super(NewYearStyleRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    def getStyleStr(self):
        return self._getString(1)

    def setStyleStr(self, value):
        self._setString(1, value)

    def getIsMega(self):
        return self._getBool(2)

    def setIsMega(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(NewYearStyleRewardViewModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('styleStr', '')
        self._addBoolProperty('isMega', False)
        self.onClose = self._addCommand('onClose')
