# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/battle_boosters_setup_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_booster_slot_model import BattleBoosterSlotModel

class InstructionType(Enum):
    ECONOMIC = 'economic'
    CREW = 'crew'
    OPTDEVICE = 'optDevice'


class BattleBoostersSetupModel(BaseSetupModel):
    __slots__ = ('showInfoPage', 'onIntroPassed')

    def __init__(self, properties=9, commands=9):
        super(BattleBoostersSetupModel, self).__init__(properties=properties, commands=commands)

    def getSlots(self):
        return self._getArray(5)

    def setSlots(self, value):
        self._setArray(5, value)

    @staticmethod
    def getSlotsType():
        return BattleBoosterSlotModel

    def getWithIntroduction(self):
        return self._getBool(6)

    def setWithIntroduction(self, value):
        self._setBool(6, value)

    def getIntroductionType(self):
        return self._getString(7)

    def setIntroductionType(self, value):
        self._setString(7, value)

    def getInstructionType(self):
        return InstructionType(self._getString(8))

    def setInstructionType(self, value):
        self._setString(8, value.value)

    def _initialize(self):
        super(BattleBoostersSetupModel, self)._initialize()
        self._addArrayProperty('slots', Array())
        self._addBoolProperty('withIntroduction', False)
        self._addStringProperty('introductionType', '')
        self._addStringProperty('instructionType')
        self.showInfoPage = self._addCommand('showInfoPage')
        self.onIntroPassed = self._addCommand('onIntroPassed')
