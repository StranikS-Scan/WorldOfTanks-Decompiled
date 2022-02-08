# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_buy_confirm_any_number_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class BattlePassBuyConfirmAnyNumberViewModel(ViewModel):
    __slots__ = ('onCloseClick', 'onBuyClick', 'onShowRewardsClick', 'onChangeSelectedLevels')

    def __init__(self, properties=8, commands=4):
        super(BattlePassBuyConfirmAnyNumberViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    def getPrice(self):
        return self._getNumber(1)

    def setPrice(self, value):
        self._setNumber(1, value)

    def getLevelsStart(self):
        return self._getNumber(2)

    def setLevelsStart(self, value):
        self._setNumber(2, value)

    def getLevelsPassed(self):
        return self._getNumber(3)

    def setLevelsPassed(self, value):
        self._setNumber(3, value)

    def getLevelsTotal(self):
        return self._getNumber(4)

    def setLevelsTotal(self, value):
        self._setNumber(4, value)

    def getLevelsSelected(self):
        return self._getNumber(5)

    def setLevelsSelected(self, value):
        self._setNumber(5, value)

    def getChapterID(self):
        return self._getNumber(6)

    def setChapterID(self, value):
        self._setNumber(6, value)

    def getBackBtnText(self):
        return self._getString(7)

    def setBackBtnText(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(BattlePassBuyConfirmAnyNumberViewModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addNumberProperty('price', 0)
        self._addNumberProperty('levelsStart', 0)
        self._addNumberProperty('levelsPassed', 0)
        self._addNumberProperty('levelsTotal', 0)
        self._addNumberProperty('levelsSelected', 0)
        self._addNumberProperty('chapterID', 0)
        self._addStringProperty('backBtnText', '')
        self.onCloseClick = self._addCommand('onCloseClick')
        self.onBuyClick = self._addCommand('onBuyClick')
        self.onShowRewardsClick = self._addCommand('onShowRewardsClick')
        self.onChangeSelectedLevels = self._addCommand('onChangeSelectedLevels')
