# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_vehicles_view_model.py
from frameworks.wulf import Array
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_bonus_info_model import NyBonusInfoModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_vehicle_slot_view_model import NyVehicleSlotViewModel

class NyVehiclesViewModel(NyWithRomanNumbersModel):
    __slots__ = ('onCloseBtnClick', 'onClearBtnClick', 'onSwitchSlotBonus', 'onGoToChallengeQuests', 'onOpenIntro', 'onIntroClose')

    def __init__(self, properties=8, commands=6):
        super(NyVehiclesViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonuses(self):
        return self._getViewModel(1)

    def getIsPostEvent(self):
        return self._getBool(2)

    def setIsPostEvent(self, value):
        self._setBool(2, value)

    def getLevelStr(self):
        return self._getString(3)

    def setLevelStr(self, value):
        self._setString(3, value)

    def getIsIntroOpened(self):
        return self._getBool(4)

    def setIsIntroOpened(self, value):
        self._setBool(4, value)

    def getCurrentAtmosphereLvl(self):
        return self._getNumber(5)

    def setCurrentAtmosphereLvl(self, value):
        self._setNumber(5, value)

    def getVehicleSlots(self):
        return self._getArray(6)

    def setVehicleSlots(self, value):
        self._setArray(6, value)

    def getExtraSlots(self):
        return self._getArray(7)

    def setExtraSlots(self, value):
        self._setArray(7, value)

    def _initialize(self):
        super(NyVehiclesViewModel, self)._initialize()
        self._addViewModelProperty('bonuses', UserListModel())
        self._addBoolProperty('isPostEvent', False)
        self._addStringProperty('levelStr', '')
        self._addBoolProperty('isIntroOpened', False)
        self._addNumberProperty('currentAtmosphereLvl', 0)
        self._addArrayProperty('vehicleSlots', Array())
        self._addArrayProperty('extraSlots', Array())
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onClearBtnClick = self._addCommand('onClearBtnClick')
        self.onSwitchSlotBonus = self._addCommand('onSwitchSlotBonus')
        self.onGoToChallengeQuests = self._addCommand('onGoToChallengeQuests')
        self.onOpenIntro = self._addCommand('onOpenIntro')
        self.onIntroClose = self._addCommand('onIntroClose')
