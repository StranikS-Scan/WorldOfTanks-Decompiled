# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/seniority_awards_multi_open_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel

class SeniorityAwardsMultiOpenViewModel(ViewModel):
    __slots__ = ('onOpenBox', 'onCloseBtnClick', 'onOpenBoxBtnClick', 'onReadyToRestart', 'onSkipAnimation')
    WINDOW_MAX_BOX_COUNT = 5

    def __init__(self, properties=10, commands=5):
        super(SeniorityAwardsMultiOpenViewModel, self).__init__(properties=properties, commands=commands)

    def getBoxesCounter(self):
        return self._getNumber(0)

    def setBoxesCounter(self, value):
        self._setNumber(0, value)

    def getLimitToOpen(self):
        return self._getNumber(1)

    def setLimitToOpen(self, value):
        self._setNumber(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    def getRewardSize(self):
        return self._getString(3)

    def setRewardSize(self, value):
        self._setString(3, value)

    def getLootboxIcon(self):
        return self._getResource(4)

    def setLootboxIcon(self, value):
        self._setResource(4, value)

    def getRestart(self):
        return self._getBool(5)

    def setRestart(self, value):
        self._setBool(5, value)

    def getIsOpenBoxBtnEnabled(self):
        return self._getBool(6)

    def setIsOpenBoxBtnEnabled(self, value):
        self._setBool(6, value)

    def getHardReset(self):
        return self._getBool(7)

    def setHardReset(self, value):
        self._setBool(7, value)

    def getStartShowIndex(self):
        return self._getNumber(8)

    def setStartShowIndex(self, value):
        self._setNumber(8, value)

    def getIsServerError(self):
        return self._getBool(9)

    def setIsServerError(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(SeniorityAwardsMultiOpenViewModel, self)._initialize()
        self._addNumberProperty('boxesCounter', 0)
        self._addNumberProperty('limitToOpen', 0)
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('rewardSize', '')
        self._addResourceProperty('lootboxIcon', R.invalid())
        self._addBoolProperty('restart', False)
        self._addBoolProperty('isOpenBoxBtnEnabled', True)
        self._addBoolProperty('hardReset', False)
        self._addNumberProperty('startShowIndex', 0)
        self._addBoolProperty('isServerError', False)
        self.onOpenBox = self._addCommand('onOpenBox')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onOpenBoxBtnClick = self._addCommand('onOpenBoxBtnClick')
        self.onReadyToRestart = self._addCommand('onReadyToRestart')
        self.onSkipAnimation = self._addCommand('onSkipAnimation')
