# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/buy_vehicle_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from gui.impl.gen.view_models.views.buy_vehicle_view.equipment_block_model import EquipmentBlockModel
from gui.impl.gen.view_models.views.buy_vehicle_view.toggle_trade_in_btn_model import ToggleTradeInBtnModel
from gui.impl.gen.view_models.views.buy_vehicle_view.vehicle_congratulation_model import VehicleCongratulationModel

class BuyVehicleViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onBuyBtnClick', 'onInHangarClick', 'onBackClick', 'onCommanderLvlChange', 'onCheckboxWithoutCrewChanged')

    @property
    def tankPrice(self):
        return self._getViewModel(0)

    @property
    def commanderLvlCards(self):
        return self._getViewModel(1)

    @property
    def equipmentBlock(self):
        return self._getViewModel(2)

    @property
    def congratulationAnim(self):
        return self._getViewModel(3)

    @property
    def toggleTradeInBtn(self):
        return self._getViewModel(4)

    def getNation(self):
        return self._getString(5)

    def setNation(self, value):
        self._setString(5, value)

    def getTankLvl(self):
        return self._getString(6)

    def setTankLvl(self, value):
        self._setString(6, value)

    def getTankName(self):
        return self._getString(7)

    def setTankName(self, value):
        self._setString(7, value)

    def getTankType(self):
        return self._getString(8)

    def setTankType(self, value):
        self._setString(8, value)

    def getIsWithoutCommander(self):
        return self._getBool(9)

    def setIsWithoutCommander(self, value):
        self._setBool(9, value)

    def getCountCrew(self):
        return self._getNumber(10)

    def setCountCrew(self, value):
        self._setNumber(10, value)

    def getVehicleNameTooltip(self):
        return self._getString(11)

    def setVehicleNameTooltip(self, value):
        self._setString(11, value)

    def getTradeOffVehicleIntCD(self):
        return self._getNumber(12)

    def setTradeOffVehicleIntCD(self, value):
        self._setNumber(12, value)

    def getBuyVehicleIntCD(self):
        return self._getNumber(13)

    def setBuyVehicleIntCD(self, value):
        self._setNumber(13, value)

    def getIsToggleBtnVisible(self):
        return self._getBool(14)

    def setIsToggleBtnVisible(self, value):
        self._setBool(14, value)

    def getIsElite(self):
        return self._getBool(15)

    def setIsElite(self, value):
        self._setBool(15, value)

    def getIsRentSelected(self):
        return self._getBool(16)

    def setIsRentSelected(self, value):
        self._setBool(16, value)

    def getIsRestore(self):
        return self._getBool(17)

    def setIsRestore(self, value):
        self._setBool(17, value)

    def getWithoutCommanderAltText(self):
        return self._getResource(18)

    def setWithoutCommanderAltText(self, value):
        self._setResource(18, value)

    def getPriceDescription(self):
        return self._getResource(19)

    def setPriceDescription(self, value):
        self._setResource(19, value)

    def getNoCrewCheckboxLabel(self):
        return self._getResource(20)

    def setNoCrewCheckboxLabel(self, value):
        self._setResource(20, value)

    def getIsMovingTextEnabled(self):
        return self._getBool(21)

    def setIsMovingTextEnabled(self, value):
        self._setBool(21, value)

    def getIsContentHidden(self):
        return self._getBool(22)

    def setIsContentHidden(self, value):
        self._setBool(22, value)

    def getBgSource(self):
        return self._getResource(23)

    def setBgSource(self, value):
        self._setResource(23, value)

    def _initialize(self):
        super(BuyVehicleViewModel, self)._initialize()
        self._addViewModelProperty('tankPrice', ListModel())
        self._addViewModelProperty('commanderLvlCards', ListModel())
        self._addViewModelProperty('equipmentBlock', EquipmentBlockModel())
        self._addViewModelProperty('congratulationAnim', VehicleCongratulationModel())
        self._addViewModelProperty('toggleTradeInBtn', ToggleTradeInBtnModel())
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
        self._addBoolProperty('isMovingTextEnabled', False)
        self._addBoolProperty('isContentHidden', False)
        self._addResourceProperty('bgSource', R.invalid())
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onBuyBtnClick = self._addCommand('onBuyBtnClick')
        self.onInHangarClick = self._addCommand('onInHangarClick')
        self.onBackClick = self._addCommand('onBackClick')
        self.onCommanderLvlChange = self._addCommand('onCommanderLvlChange')
        self.onCheckboxWithoutCrewChanged = self._addCommand('onCheckboxWithoutCrewChanged')
