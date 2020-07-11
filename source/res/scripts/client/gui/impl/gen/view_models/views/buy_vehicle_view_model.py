# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/buy_vehicle_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from gui.impl.gen.view_models.views.buy_vehicle_view.equipment_block_model import EquipmentBlockModel
from gui.impl.gen.view_models.views.buy_vehicle_view.vehicle_congratulation_model import VehicleCongratulationModel

class BuyVehicleViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onBuyBtnClick', 'onInHangarClick', 'onBackClick', 'onCommanderLvlChange', 'onCheckboxWithoutCrewChanged')

    def __init__(self, properties=21, commands=6):
        super(BuyVehicleViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def commanderLvlCards(self):
        return self._getViewModel(0)

    @property
    def equipmentBlock(self):
        return self._getViewModel(1)

    @property
    def congratulationAnim(self):
        return self._getViewModel(2)

    def getNation(self):
        return self._getString(3)

    def setNation(self, value):
        self._setString(3, value)

    def getTankLvl(self):
        return self._getString(4)

    def setTankLvl(self, value):
        self._setString(4, value)

    def getTankName(self):
        return self._getString(5)

    def setTankName(self, value):
        self._setString(5, value)

    def getTankType(self):
        return self._getString(6)

    def setTankType(self, value):
        self._setString(6, value)

    def getIsWithoutCommander(self):
        return self._getBool(7)

    def setIsWithoutCommander(self, value):
        self._setBool(7, value)

    def getCountCrew(self):
        return self._getNumber(8)

    def setCountCrew(self, value):
        self._setNumber(8, value)

    def getVehicleNameTooltip(self):
        return self._getString(9)

    def setVehicleNameTooltip(self, value):
        self._setString(9, value)

    def getTradeOffVehicleIntCD(self):
        return self._getNumber(10)

    def setTradeOffVehicleIntCD(self, value):
        self._setNumber(10, value)

    def getBuyVehicleIntCD(self):
        return self._getNumber(11)

    def setBuyVehicleIntCD(self, value):
        self._setNumber(11, value)

    def getIsToggleBtnVisible(self):
        return self._getBool(12)

    def setIsToggleBtnVisible(self, value):
        self._setBool(12, value)

    def getIsElite(self):
        return self._getBool(13)

    def setIsElite(self, value):
        self._setBool(13, value)

    def getIsRentSelected(self):
        return self._getBool(14)

    def setIsRentSelected(self, value):
        self._setBool(14, value)

    def getIsRestore(self):
        return self._getBool(15)

    def setIsRestore(self, value):
        self._setBool(15, value)

    def getWithoutCommanderAltText(self):
        return self._getResource(16)

    def setWithoutCommanderAltText(self, value):
        self._setResource(16, value)

    def getPriceDescription(self):
        return self._getResource(17)

    def setPriceDescription(self, value):
        self._setResource(17, value)

    def getNoCrewCheckboxLabel(self):
        return self._getResource(18)

    def setNoCrewCheckboxLabel(self, value):
        self._setResource(18, value)

    def getIsContentHidden(self):
        return self._getBool(19)

    def setIsContentHidden(self, value):
        self._setBool(19, value)

    def getBgSource(self):
        return self._getResource(20)

    def setBgSource(self, value):
        self._setResource(20, value)

    def _initialize(self):
        super(BuyVehicleViewModel, self)._initialize()
        self._addViewModelProperty('commanderLvlCards', ListModel())
        self._addViewModelProperty('equipmentBlock', EquipmentBlockModel())
        self._addViewModelProperty('congratulationAnim', VehicleCongratulationModel())
        self._addStringProperty('nation', '')
        self._addStringProperty('tankLvl', '')
        self._addStringProperty('tankName', '')
        self._addStringProperty('tankType', '')
        self._addBoolProperty('isWithoutCommander', False)
        self._addNumberProperty('countCrew', 0)
        self._addStringProperty('vehicleNameTooltip', '')
        self._addNumberProperty('tradeOffVehicleIntCD', -1)
        self._addNumberProperty('buyVehicleIntCD', 0)
        self._addBoolProperty('isToggleBtnVisible', False)
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isRentSelected', False)
        self._addBoolProperty('isRestore', False)
        self._addResourceProperty('withoutCommanderAltText', R.invalid())
        self._addResourceProperty('priceDescription', R.invalid())
        self._addResourceProperty('noCrewCheckboxLabel', R.invalid())
        self._addBoolProperty('isContentHidden', False)
        self._addResourceProperty('bgSource', R.invalid())
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onBuyBtnClick = self._addCommand('onBuyBtnClick')
        self.onInHangarClick = self._addCommand('onInHangarClick')
        self.onBackClick = self._addCommand('onBackClick')
        self.onCommanderLvlChange = self._addCommand('onCommanderLvlChange')
        self.onCheckboxWithoutCrewChanged = self._addCommand('onCheckboxWithoutCrewChanged')
