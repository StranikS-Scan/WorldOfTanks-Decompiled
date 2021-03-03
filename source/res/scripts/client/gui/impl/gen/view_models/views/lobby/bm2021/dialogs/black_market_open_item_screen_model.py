# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bm2021/dialogs/black_market_open_item_screen_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.stats_model import StatsModel
from gui.impl.gen.view_models.common.vehicle_model import VehicleModel

class BlackMarketOpenItemScreenModel(ViewModel):
    __slots__ = ('onOpenHangar', 'onOpenVehicleList', 'onClose', 'onOpenPreview', 'onPickVehicle', 'onChooseVehicle', 'onNextOpenVehicle', 'onOpenExchange')

    def __init__(self, properties=8, commands=8):
        super(BlackMarketOpenItemScreenModel, self).__init__(properties=properties, commands=commands)

    @property
    def stats(self):
        return self._getViewModel(0)

    def getIsHangarOpened(self):
        return self._getBool(1)

    def setIsHangarOpened(self, value):
        self._setBool(1, value)

    def getEndDate(self):
        return self._getNumber(2)

    def setEndDate(self, value):
        self._setNumber(2, value)

    def getNextOpenPrice(self):
        return self._getNumber(3)

    def setNextOpenPrice(self, value):
        self._setNumber(3, value)

    def getSlotsNumber(self):
        return self._getNumber(4)

    def setSlotsNumber(self, value):
        self._setNumber(4, value)

    def getChosenVehicleId(self):
        return self._getNumber(5)

    def setChosenVehicleId(self, value):
        self._setNumber(5, value)

    def getIsOperationSuccessfull(self):
        return self._getBool(6)

    def setIsOperationSuccessfull(self, value):
        self._setBool(6, value)

    def getVehicleList(self):
        return self._getArray(7)

    def setVehicleList(self, value):
        self._setArray(7, value)

    def _initialize(self):
        super(BlackMarketOpenItemScreenModel, self)._initialize()
        self._addViewModelProperty('stats', StatsModel())
        self._addBoolProperty('isHangarOpened', False)
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('nextOpenPrice', 0)
        self._addNumberProperty('slotsNumber', 0)
        self._addNumberProperty('chosenVehicleId', 0)
        self._addBoolProperty('isOperationSuccessfull', False)
        self._addArrayProperty('vehicleList', Array())
        self.onOpenHangar = self._addCommand('onOpenHangar')
        self.onOpenVehicleList = self._addCommand('onOpenVehicleList')
        self.onClose = self._addCommand('onClose')
        self.onOpenPreview = self._addCommand('onOpenPreview')
        self.onPickVehicle = self._addCommand('onPickVehicle')
        self.onChooseVehicle = self._addCommand('onChooseVehicle')
        self.onNextOpenVehicle = self._addCommand('onNextOpenVehicle')
        self.onOpenExchange = self._addCommand('onOpenExchange')
