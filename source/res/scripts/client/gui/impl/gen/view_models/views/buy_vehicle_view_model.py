# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/buy_vehicle_view_model.py
import typing
from frameworks.wulf import Array
from frameworks.wulf.gui_constants import ResourceValue
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.buy_vehicle_view.equipment_block_model import EquipmentBlockModel
from gui.impl.gen.view_models.views.buy_vehicle_view.vehicle_congratulation_model import VehicleCongratulationModel

class BuyVehicleViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onBuyBtnClick', 'onShowInHangarClick', 'onCommanderLvlChange', 'onToggleRentAndTradeIn', 'onCheckboxWithoutCrewChanged')

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

    def getTankLvl(self):
        return self._getString(3)

    def setTankLvl(self, value):
        self._setString(3, value)

    def getTankName(self):
        return self._getString(4)

    def setTankName(self, value):
        self._setString(4, value)

    def getTankType(self):
        return self._getString(5)

    def setTankType(self, value):
        self._setString(5, value)

    def getIsWithoutCommander(self):
        return self._getBool(6)

    def setIsWithoutCommander(self, value):
        self._setBool(6, value)

    def getCountCrew(self):
        return self._getNumber(7)

    def setCountCrew(self, value):
        self._setNumber(7, value)

    def getVehicleNameTooltip(self):
        return self._getString(8)

    def setVehicleNameTooltip(self, value):
        self._setString(8, value)

    def getTankPrice(self):
        return self._getArray(9)

    def setTankPrice(self, value):
        self._setArray(9, value)

    def getCommanderLvlCards(self):
        return self._getArray(10)

    def setCommanderLvlCards(self, value):
        self._setArray(10, value)

    def getTradeOffVehicleIntCD(self):
        return self._getNumber(11)

    def setTradeOffVehicleIntCD(self, value):
        self._setNumber(11, value)

    def getBuyVehicleIntCD(self):
        return self._getNumber(12)

    def setBuyVehicleIntCD(self, value):
        self._setNumber(12, value)

    def getIsToggleBtnVisible(self):
        return self._getBool(13)

    def setIsToggleBtnVisible(self, value):
        self._setBool(13, value)

    def getIsElite(self):
        return self._getBool(14)

    def setIsElite(self, value):
        self._setBool(14, value)

    def getIsRentVisible(self):
        return self._getBool(15)

    def setIsRentVisible(self, value):
        self._setBool(15, value)

    def getWithoutCommanderAltText(self):
        return self._getResource(16)

    def setWithoutCommanderAltText(self, value):
        self._setResource(16, value)

    def getIsInBootcamp(self):
        return self._getBool(17)

    def setIsInBootcamp(self, value):
        self._setBool(17, value)

    def getPriceDescription(self):
        return self._getResource(18)

    def setPriceDescription(self, value):
        self._setResource(18, value)

    def getNoCrewCheckboxLabel(self):
        return self._getResource(19)

    def setNoCrewCheckboxLabel(self, value):
        self._setResource(19, value)

    def getIsMovingTextEnabled(self):
        return self._getBool(20)

    def setIsMovingTextEnabled(self, value):
        self._setBool(20, value)

    def getIsContentHidden(self):
        return self._getBool(21)

    def setIsContentHidden(self, value):
        self._setBool(21, value)

    def _initialize(self):
        self._addViewModelProperty('equipmentBlock', EquipmentBlockModel())
        self._addViewModelProperty('congratulationAnim', VehicleCongratulationModel())
        self._addStringProperty('nation', '')
        self._addStringProperty('tankLvl', '')
        self._addStringProperty('tankName', '')
        self._addStringProperty('tankType', '')
        self._addBoolProperty('isWithoutCommander', False)
        self._addNumberProperty('countCrew', 0)
        self._addStringProperty('vehicleNameTooltip', '')
        self._addArrayProperty('tankPrice', Array())
        self._addArrayProperty('commanderLvlCards', Array())
        self._addNumberProperty('tradeOffVehicleIntCD', -1)
        self._addNumberProperty('buyVehicleIntCD', 0)
        self._addBoolProperty('isToggleBtnVisible', False)
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isRentVisible', False)
        self._addResourceProperty('withoutCommanderAltText', ResourceValue.DEFAULT)
        self._addBoolProperty('isInBootcamp', False)
        self._addResourceProperty('priceDescription', ResourceValue.DEFAULT)
        self._addResourceProperty('noCrewCheckboxLabel', ResourceValue.DEFAULT)
        self._addBoolProperty('isMovingTextEnabled', False)
        self._addBoolProperty('isContentHidden', False)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onBuyBtnClick = self._addCommand('onBuyBtnClick')
        self.onShowInHangarClick = self._addCommand('onShowInHangarClick')
        self.onCommanderLvlChange = self._addCommand('onCommanderLvlChange')
        self.onToggleRentAndTradeIn = self._addCommand('onToggleRentAndTradeIn')
        self.onCheckboxWithoutCrewChanged = self._addCommand('onCheckboxWithoutCrewChanged')
