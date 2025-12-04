# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/lootboxes_storage_view_statistic_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class LootboxesStorageViewStatisticModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(LootboxesStorageViewStatisticModel, self).__init__(properties=properties, commands=commands)

    def getLastReceivedVehicles(self):
        return self._getArray(0)

    def setLastReceivedVehicles(self, value):
        self._setArray(0, value)

    @staticmethod
    def getLastReceivedVehiclesType():
        return BonusModel

    def _initialize(self):
        super(LootboxesStorageViewStatisticModel, self)._initialize()
        self._addArrayProperty('lastReceivedVehicles', Array())
