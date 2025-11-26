# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/loadout_view_model.py
from frameworks.wulf import Array, ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_royale_equipment_model import BattleRoyaleEquipmentModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_royale_respawn_ability_model import BattleRoyaleRespawnAbilityModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_royale_shell_model import BattleRoyaleShellModel

class LoadoutViewModel(ViewModel):
    __slots__ = ('showUpgrades',)

    def __init__(self, properties=3, commands=1):
        super(LoadoutViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def respawnAbility(self):
        return self._getViewModel(0)

    @staticmethod
    def getRespawnAbilityType():
        return BattleRoyaleRespawnAbilityModel

    def getShells(self):
        return self._getArray(1)

    def setShells(self, value):
        self._setArray(1, value)

    @staticmethod
    def getShellsType():
        return BattleRoyaleShellModel

    def getEquipment(self):
        return self._getArray(2)

    def setEquipment(self, value):
        self._setArray(2, value)

    @staticmethod
    def getEquipmentType():
        return BattleRoyaleEquipmentModel

    def _initialize(self):
        super(LoadoutViewModel, self)._initialize()
        self._addViewModelProperty('respawnAbility', BattleRoyaleRespawnAbilityModel())
        self._addArrayProperty('shells', Array())
        self._addArrayProperty('equipment', Array())
        self.showUpgrades = self._addCommand('showUpgrades')
