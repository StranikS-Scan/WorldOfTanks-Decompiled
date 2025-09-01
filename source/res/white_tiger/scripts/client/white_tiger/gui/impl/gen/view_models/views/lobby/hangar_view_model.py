# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/hangar_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel

class WhiteTigerVehicles(Enum):
    NONE = 'none'
    BT110 = 'BT110'
    BT220 = 'BT220'
    RESISTOR = 'RESISTOR'
    THUNDERBOLT = 'THUNDERBOLT'
    FOUDRE = 'FOUDRE'
    POJISTKA = 'POJISTKA'


class HangarViewModel(ViewModel):
    __slots__ = ('onEscPressed', 'onInfoClicked', 'onViewLoaded')

    def __init__(self, properties=2, commands=3):
        super(HangarViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def router(self):
        return self._getViewModel(0)

    @staticmethod
    def getRouterType():
        return RouterModel

    def getSelectedVehicle(self):
        return WhiteTigerVehicles(self._getString(1))

    def setSelectedVehicle(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(HangarViewModel, self)._initialize()
        self._addViewModelProperty('router', RouterModel())
        self._addStringProperty('selectedVehicle')
        self.onEscPressed = self._addCommand('onEscPressed')
        self.onInfoClicked = self._addCommand('onInfoClicked')
        self.onViewLoaded = self._addCommand('onViewLoaded')
