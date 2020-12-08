# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_vehicles_view_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel

class NewYearVehiclesViewModel(NyWithRomanNumbersModel):
    __slots__ = ('onCloseBtnClick', 'onClearBtnClick', 'onSwitchExtraSlotBonus', 'onGoToChallengeQuests', 'onSetIntroInProgress', 'onReadyToShow')

    def __init__(self, properties=9, commands=6):
        super(NewYearVehiclesViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleSlots(self):
        return self._getViewModel(1)

    @property
    def extraSlots(self):
        return self._getViewModel(2)

    @property
    def bonuses(self):
        return self._getViewModel(3)

    def getIsInProgressIntro(self):
        return self._getBool(4)

    def setIsInProgressIntro(self, value):
        self._setBool(4, value)

    def getIsPostEventIntro(self):
        return self._getBool(5)

    def setIsPostEventIntro(self, value):
        self._setBool(5, value)

    def getIsExtraSlotBonusHint(self):
        return self._getBool(6)

    def setIsExtraSlotBonusHint(self, value):
        self._setBool(6, value)

    def getIntroRegularCooldown(self):
        return self._getNumber(7)

    def setIntroRegularCooldown(self, value):
        self._setNumber(7, value)

    def getIntroExtraCooldown(self):
        return self._getNumber(8)

    def setIntroExtraCooldown(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(NewYearVehiclesViewModel, self)._initialize()
        self._addViewModelProperty('vehicleSlots', ListModel())
        self._addViewModelProperty('extraSlots', ListModel())
        self._addViewModelProperty('bonuses', UserListModel())
        self._addBoolProperty('isInProgressIntro', False)
        self._addBoolProperty('isPostEventIntro', False)
        self._addBoolProperty('isExtraSlotBonusHint', False)
        self._addNumberProperty('introRegularCooldown', 0)
        self._addNumberProperty('introExtraCooldown', 0)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onClearBtnClick = self._addCommand('onClearBtnClick')
        self.onSwitchExtraSlotBonus = self._addCommand('onSwitchExtraSlotBonus')
        self.onGoToChallengeQuests = self._addCommand('onGoToChallengeQuests')
        self.onSetIntroInProgress = self._addCommand('onSetIntroInProgress')
        self.onReadyToShow = self._addCommand('onReadyToShow')
