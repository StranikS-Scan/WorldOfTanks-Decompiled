# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/roster_view/roster_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.carousel_view_model import CarouselViewModel
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_supply_view_model import RosterSupplyViewModel
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_vehicle_specs_view_model import RosterVehicleSpecsViewModel
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_vehicle_view_model import RosterVehicleViewModel

class GameMode(Enum):
    ONEXONE = '1x1'
    ONEXSEVEN = '1x7'


class RosterViewModel(ViewModel):
    __slots__ = ('onAcceptClicked', 'onCancelClicked', 'onClose', 'onItemClicked', 'onFilterTextChanged', 'onFilterClearClicked', 'onClearVehicleSlotClicked', 'onClearSupplySlotClicked', 'onClosingAnimationEnded', 'onMannerClicked')

    def __init__(self, properties=9, commands=10):
        super(RosterViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def carousel(self):
        return self._getViewModel(0)

    @property
    def vehicleSpecs(self):
        return self._getViewModel(1)

    def getVehicles(self):
        return self._getArray(2)

    def setVehicles(self, value):
        self._setArray(2, value)

    def getSupplies(self):
        return self._getArray(3)

    def setSupplies(self, value):
        self._setArray(3, value)

    def getSlotVehicleClasses(self):
        return self._getArray(4)

    def setSlotVehicleClasses(self, value):
        self._setArray(4, value)

    def getHasConfigurationChanged(self):
        return self._getBool(5)

    def setHasConfigurationChanged(self, value):
        self._setBool(5, value)

    def getTotalItems(self):
        return self._getNumber(6)

    def setTotalItems(self, value):
        self._setNumber(6, value)

    def getGameMode(self):
        return GameMode(self._getString(7))

    def setGameMode(self, value):
        self._setString(7, value.value)

    def getIsClosing(self):
        return self._getBool(8)

    def setIsClosing(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(RosterViewModel, self)._initialize()
        self._addViewModelProperty('carousel', CarouselViewModel())
        self._addViewModelProperty('vehicleSpecs', RosterVehicleSpecsViewModel())
        self._addArrayProperty('vehicles', Array())
        self._addArrayProperty('supplies', Array())
        self._addArrayProperty('slotVehicleClasses', Array())
        self._addBoolProperty('hasConfigurationChanged', False)
        self._addNumberProperty('totalItems', 0)
        self._addStringProperty('gameMode')
        self._addBoolProperty('isClosing', False)
        self.onAcceptClicked = self._addCommand('onAcceptClicked')
        self.onCancelClicked = self._addCommand('onCancelClicked')
        self.onClose = self._addCommand('onClose')
        self.onItemClicked = self._addCommand('onItemClicked')
        self.onFilterTextChanged = self._addCommand('onFilterTextChanged')
        self.onFilterClearClicked = self._addCommand('onFilterClearClicked')
        self.onClearVehicleSlotClicked = self._addCommand('onClearVehicleSlotClicked')
        self.onClearSupplySlotClicked = self._addCommand('onClearSupplySlotClicked')
        self.onClosingAnimationEnded = self._addCommand('onClosingAnimationEnded')
        self.onMannerClicked = self._addCommand('onMannerClicked')
