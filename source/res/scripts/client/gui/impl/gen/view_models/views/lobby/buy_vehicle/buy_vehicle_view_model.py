# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/buy_vehicle/buy_vehicle_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.buy_vehicle.buy_vehicle_congratulation_model import BuyVehicleCongratulationModel
from gui.impl.gen.view_models.views.lobby.buy_vehicle.buy_vehicle_content_view_model import BuyVehicleContentViewModel

class BuyVehicleViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onBuyBtnClick', 'onInHangarClick', 'onBackClick')

    def __init__(self, properties=6, commands=4):
        super(BuyVehicleViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def equipmentBlock(self):
        return self._getViewModel(0)

    @property
    def congratulationAnim(self):
        return self._getViewModel(1)

    def getNation(self):
        return self._getString(2)

    def setNation(self, value):
        self._setString(2, value)

    def getIsContentHidden(self):
        return self._getBool(3)

    def setIsContentHidden(self, value):
        self._setBool(3, value)

    def getBgSource(self):
        return self._getResource(4)

    def setBgSource(self, value):
        self._setResource(4, value)

    def getVehicleImage(self):
        return self._getResource(5)

    def setVehicleImage(self, value):
        self._setResource(5, value)

    def _initialize(self):
        super(BuyVehicleViewModel, self)._initialize()
        self._addViewModelProperty('equipmentBlock', BuyVehicleContentViewModel())
        self._addViewModelProperty('congratulationAnim', BuyVehicleCongratulationModel())
        self._addStringProperty('nation', '')
        self._addBoolProperty('isContentHidden', False)
        self._addResourceProperty('bgSource', R.invalid())
        self._addResourceProperty('vehicleImage', R.invalid())
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onBuyBtnClick = self._addCommand('onBuyBtnClick')
        self.onInHangarClick = self._addCommand('onInHangarClick')
        self.onBackClick = self._addCommand('onBackClick')
