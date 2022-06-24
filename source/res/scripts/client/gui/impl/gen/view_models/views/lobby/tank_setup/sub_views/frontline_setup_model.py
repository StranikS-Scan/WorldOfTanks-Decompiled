# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/frontline_setup_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_ability_slot_model import BattleAbilitySlotModel

class FrontlineSetupModel(BaseSetupModel):
    __slots__ = ('showBattleAbilitiesSetup', 'onChangeApplyAbilitiesToTypeSettings')

    def __init__(self, properties=10, commands=9):
        super(FrontlineSetupModel, self).__init__(properties=properties, commands=commands)

    def getIsLocked(self):
        return self._getBool(5)

    def setIsLocked(self, value):
        self._setBool(5, value)

    def getIsTypeSelected(self):
        return self._getBool(6)

    def setIsTypeSelected(self, value):
        self._setBool(6, value)

    def getVehicleType(self):
        return self._getString(7)

    def setVehicleType(self, value):
        self._setString(7, value)

    def getSelectedCategory(self):
        return self._getString(8)

    def setSelectedCategory(self, value):
        self._setString(8, value)

    def getSlots(self):
        return self._getArray(9)

    def setSlots(self, value):
        self._setArray(9, value)

    @staticmethod
    def getSlotsType():
        return BattleAbilitySlotModel

    def _initialize(self):
        super(FrontlineSetupModel, self)._initialize()
        self._addBoolProperty('isLocked', True)
        self._addBoolProperty('isTypeSelected', False)
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('selectedCategory', '')
        self._addArrayProperty('slots', Array())
        self.showBattleAbilitiesSetup = self._addCommand('showBattleAbilitiesSetup')
        self.onChangeApplyAbilitiesToTypeSettings = self._addCommand('onChangeApplyAbilitiesToTypeSettings')
