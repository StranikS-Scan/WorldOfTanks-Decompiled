# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/battle/ban_view_model.py
from frameworks.wulf import Array, ViewModel
from comp7.gui.impl.gen.view_models.views.battle.ban_progression_model import BanProgressionModel
from comp7.gui.impl.gen.view_models.views.battle.comp7_vehicle_model import Comp7VehicleModel
from comp7.gui.impl.gen.view_models.views.battle.player_model import PlayerModel

class BanViewModel(ViewModel):
    __slots__ = ('onClose', 'onConfirm', 'onSelect')

    def __init__(self, properties=7, commands=3):
        super(BanViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def banProgression(self):
        return self._getViewModel(0)

    @staticmethod
    def getBanProgressionType():
        return BanProgressionModel

    def getOwnId(self):
        return self._getNumber(1)

    def setOwnId(self, value):
        self._setNumber(1, value)

    def getPlayers(self):
        return self._getArray(2)

    def setPlayers(self, value):
        self._setArray(2, value)

    @staticmethod
    def getPlayersType():
        return PlayerModel

    def getVehicles(self):
        return self._getArray(3)

    def setVehicles(self, value):
        self._setArray(3, value)

    @staticmethod
    def getVehiclesType():
        return Comp7VehicleModel

    def getNationsOrder(self):
        return self._getArray(4)

    def setNationsOrder(self, value):
        self._setArray(4, value)

    @staticmethod
    def getNationsOrderType():
        return unicode

    def getIsSelectionAvailable(self):
        return self._getBool(5)

    def setIsSelectionAvailable(self, value):
        self._setBool(5, value)

    def getSelectedVehicleCD(self):
        return self._getNumber(6)

    def setSelectedVehicleCD(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(BanViewModel, self)._initialize()
        self._addViewModelProperty('banProgression', BanProgressionModel())
        self._addNumberProperty('ownId', 0)
        self._addArrayProperty('players', Array())
        self._addArrayProperty('vehicles', Array())
        self._addArrayProperty('nationsOrder', Array())
        self._addBoolProperty('isSelectionAvailable', True)
        self._addNumberProperty('selectedVehicleCD', -1)
        self.onClose = self._addCommand('onClose')
        self.onConfirm = self._addCommand('onConfirm')
        self.onSelect = self._addCommand('onSelect')
