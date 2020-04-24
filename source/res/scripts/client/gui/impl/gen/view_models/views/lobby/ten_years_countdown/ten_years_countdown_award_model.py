# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ten_years_countdown/ten_years_countdown_award_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class TenYearsCountdownAwardModel(ViewModel):
    __slots__ = ('onActionBtnClick', 'onDestroyEvent')

    def __init__(self, properties=4, commands=2):
        super(TenYearsCountdownAwardModel, self).__init__(properties=properties, commands=commands)

    def getAwardType(self):
        return self._getString(0)

    def setAwardType(self, value):
        self._setString(0, value)

    def getStartClose(self):
        return self._getBool(1)

    def setStartClose(self, value):
        self._setBool(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    def getTitle(self):
        return self._getResource(3)

    def setTitle(self, value):
        self._setResource(3, value)

    def _initialize(self):
        super(TenYearsCountdownAwardModel, self)._initialize()
        self._addStringProperty('awardType', '')
        self._addBoolProperty('startClose', False)
        self._addArrayProperty('rewards', Array())
        self._addResourceProperty('title', R.invalid())
        self.onActionBtnClick = self._addCommand('onActionBtnClick')
        self.onDestroyEvent = self._addCommand('onDestroyEvent')
