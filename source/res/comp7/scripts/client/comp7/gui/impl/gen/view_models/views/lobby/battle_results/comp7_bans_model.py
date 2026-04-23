# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/battle_results/comp7_bans_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class Comp7BansModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(Comp7BansModel, self).__init__(properties=properties, commands=commands)

    @property
    def bannedByAlliesVehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getBannedByAlliesVehicleType():
        return VehicleModel

    @property
    def bannedByEnemiesVehicle(self):
        return self._getViewModel(1)

    @staticmethod
    def getBannedByEnemiesVehicleType():
        return VehicleModel

    def getIsEnabled(self):
        return self._getBool(2)

    def setIsEnabled(self, value):
        self._setBool(2, value)

    def getIsAlliesRandomlySelected(self):
        return self._getBool(3)

    def setIsAlliesRandomlySelected(self, value):
        self._setBool(3, value)

    def getIsEnemyRandomlySelected(self):
        return self._getBool(4)

    def setIsEnemyRandomlySelected(self, value):
        self._setBool(4, value)

    def getAlliesVotes(self):
        return self._getNumber(5)

    def setAlliesVotes(self, value):
        self._setNumber(5, value)

    def getEnemyVotes(self):
        return self._getNumber(6)

    def setEnemyVotes(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(Comp7BansModel, self)._initialize()
        self._addViewModelProperty('bannedByAlliesVehicle', VehicleModel())
        self._addViewModelProperty('bannedByEnemiesVehicle', VehicleModel())
        self._addBoolProperty('isEnabled', True)
        self._addBoolProperty('isAlliesRandomlySelected', False)
        self._addBoolProperty('isEnemyRandomlySelected', False)
        self._addNumberProperty('alliesVotes', 0)
        self._addNumberProperty('enemyVotes', 0)
