# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_decorations_popover_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class NewYearDecorationsPopoverModel(ViewModel):
    __slots__ = ('onBreakBtnClick', 'onSlotStatusIsNewChanged', 'onSlotSelectedForBreak', 'onBreakAnimationComplete')
    EMPTY_STATE = 0
    INFO_BREAK_STATE = 1
    INFO_GET_STATE = 2
    BREAK_STATE = 3

    def __init__(self, properties=10, commands=4):
        super(NewYearDecorationsPopoverModel, self).__init__(properties=properties, commands=commands)

    @property
    def slotsList(self):
        return self._getViewModel(0)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def getSetting(self):
        return self._getResource(2)

    def setSetting(self, value):
        self._setResource(2, value)

    def getDecorationTypeIcon(self):
        return self._getResource(3)

    def setDecorationTypeIcon(self, value):
        self._setResource(3, value)

    def getRank(self):
        return self._getString(4)

    def setRank(self, value):
        self._setString(4, value)

    def getExpectedShardsCount(self):
        return self._getNumber(5)

    def setExpectedShardsCount(self, value):
        self._setNumber(5, value)

    def getEnabledBreakBtn(self):
        return self._getBool(6)

    def setEnabledBreakBtn(self, value):
        self._setBool(6, value)

    def getTotalRegisterDecorations(self):
        return self._getNumber(7)

    def setTotalRegisterDecorations(self, value):
        self._setNumber(7, value)

    def getCurrentBreakDecorations(self):
        return self._getNumber(8)

    def setCurrentBreakDecorations(self, value):
        self._setNumber(8, value)

    def getState(self):
        return self._getNumber(9)

    def setState(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(NewYearDecorationsPopoverModel, self)._initialize()
        self._addViewModelProperty('slotsList', UserListModel())
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('setting', R.invalid())
        self._addResourceProperty('decorationTypeIcon', R.invalid())
        self._addStringProperty('rank', '')
        self._addNumberProperty('expectedShardsCount', 0)
        self._addBoolProperty('enabledBreakBtn', False)
        self._addNumberProperty('totalRegisterDecorations', 0)
        self._addNumberProperty('currentBreakDecorations', 0)
        self._addNumberProperty('state', -1)
        self.onBreakBtnClick = self._addCommand('onBreakBtnClick')
        self.onSlotStatusIsNewChanged = self._addCommand('onSlotStatusIsNewChanged')
        self.onSlotSelectedForBreak = self._addCommand('onSlotSelectedForBreak')
        self.onBreakAnimationComplete = self._addCommand('onBreakAnimationComplete')
