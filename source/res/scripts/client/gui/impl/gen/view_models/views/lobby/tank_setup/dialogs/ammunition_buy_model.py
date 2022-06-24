# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/dialogs/ammunition_buy_model.py
from gui.impl.gen.view_models.views.lobby.common.dialog_with_exchange import DialogWithExchange
from gui.impl.gen.view_models.views.lobby.tank_setup.common.deal_panel_model import DealPanelModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.main_content.ammunition_buy_content import AmmunitionBuyContent

class AmmunitionBuyModel(DialogWithExchange):
    __slots__ = ()

    def __init__(self, properties=20, commands=3):
        super(AmmunitionBuyModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainContent(self):
        return self._getViewModel(15)

    @staticmethod
    def getMainContentType():
        return AmmunitionBuyContent

    @property
    def dealPanel(self):
        return self._getViewModel(16)

    @staticmethod
    def getDealPanelType():
        return DealPanelModel

    def getWithRollback(self):
        return self._getBool(17)

    def setWithRollback(self, value):
        self._setBool(17, value)

    def getVehicleType(self):
        return self._getString(18)

    def setVehicleType(self, value):
        self._setString(18, value)

    def getApplyForAllVehiclesByType(self):
        return self._getBool(19)

    def setApplyForAllVehiclesByType(self, value):
        self._setBool(19, value)

    def _initialize(self):
        super(AmmunitionBuyModel, self)._initialize()
        self._addViewModelProperty('mainContent', AmmunitionBuyContent())
        self._addViewModelProperty('dealPanel', DealPanelModel())
        self._addBoolProperty('withRollback', False)
        self._addStringProperty('vehicleType', '')
        self._addBoolProperty('applyForAllVehiclesByType', False)
