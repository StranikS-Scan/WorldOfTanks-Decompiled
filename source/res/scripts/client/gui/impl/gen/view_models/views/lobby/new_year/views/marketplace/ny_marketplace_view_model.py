# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/marketplace/ny_marketplace_view_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.new_year.views.base.ny_scene_rotatable_view import NySceneRotatableView
from gui.impl.gen.view_models.views.lobby.new_year.views.marketplace.card_model import CardModel
from gui.impl.gen.view_models.views.lobby.new_year.views.marketplace.ny_marketplace_kit_model import NyMarketplaceKitModel

class KitState(Enum):
    RECEIVED = 'received'
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'


class VehicleState(Enum):
    DEFAULT = 'default'
    NOT_IN_INVENTORY = 'notInInventory'
    BROKEN = 'broken'
    IN_BATTLE = 'inBattle'
    IN_UNIT = 'inUnit'
    CUSTOMIZATION_UNAVAILABLE = 'customizationUnavailable'


class NyMarketplaceViewModel(NySceneRotatableView):
    __slots__ = ('onSwitchKit',)

    def __init__(self, properties=9, commands=3):
        super(NyMarketplaceViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def kit(self):
        return self._getViewModel(1)

    @staticmethod
    def getKitType():
        return NyMarketplaceKitModel

    def getCurrentTabName(self):
        return self._getString(2)

    def setCurrentTabName(self, value):
        self._setString(2, value)

    def getKitState(self):
        return KitState(self._getString(3))

    def setKitState(self, value):
        self._setString(3, value.value)

    def getCurrentKitName(self):
        return self._getString(4)

    def setCurrentKitName(self, value):
        self._setString(4, value)

    def getIsInteractive(self):
        return self._getBool(5)

    def setIsInteractive(self, value):
        self._setBool(5, value)

    def getIsVehicleCustomizationEnabled(self):
        return self._getBool(6)

    def setIsVehicleCustomizationEnabled(self, value):
        self._setBool(6, value)

    def getVehicleState(self):
        return VehicleState(self._getString(7))

    def setVehicleState(self, value):
        self._setString(7, value.value)

    def getCards(self):
        return self._getArray(8)

    def setCards(self, value):
        self._setArray(8, value)

    @staticmethod
    def getCardsType():
        return CardModel

    def _initialize(self):
        super(NyMarketplaceViewModel, self)._initialize()
        self._addViewModelProperty('kit', NyMarketplaceKitModel())
        self._addStringProperty('currentTabName', 'ny22')
        self._addStringProperty('kitState')
        self._addStringProperty('currentKitName', '')
        self._addBoolProperty('isInteractive', True)
        self._addBoolProperty('isVehicleCustomizationEnabled', True)
        self._addStringProperty('vehicleState')
        self._addArrayProperty('cards', Array())
        self.onSwitchKit = self._addCommand('onSwitchKit')
