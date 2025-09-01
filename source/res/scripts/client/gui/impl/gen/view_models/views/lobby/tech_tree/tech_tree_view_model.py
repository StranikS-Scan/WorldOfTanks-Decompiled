# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tech_tree/tech_tree_view_model.py
from enum import Enum
from frameworks.wulf import Array, Map, ViewModel
from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel

class NationEnum(Enum):
    CHINA = 'china'
    CZECHOSLOVAKIA = 'czech'
    FRANCE = 'france'
    GERMANY = 'germany'
    ITALY = 'italy'
    JAPAN = 'japan'
    POLAND = 'poland'
    SWEDEN = 'sweden'
    UK = 'uk'
    USA = 'usa'
    USSR = 'ussr'


class TechTreeViewModel(ViewModel):
    __slots__ = ('onOpenAboutVehicle', 'onAddToCompare', 'onOpenCollectableVehicles', 'onOpenPremiumShop')

    def __init__(self, properties=8, commands=4):
        super(TechTreeViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def router(self):
        return self._getViewModel(0)

    @staticmethod
    def getRouterType():
        return RouterModel

    def getFirstHighlightedLevel(self):
        return self._getNumber(1)

    def setFirstHighlightedLevel(self, value):
        self._setNumber(1, value)

    def getShowWelcomeAnimation(self):
        return self._getBool(2)

    def setShowWelcomeAnimation(self, value):
        self._setBool(2, value)

    def getCollectableVehiclesAvailable(self):
        return self._getBool(3)

    def setCollectableVehiclesAvailable(self, value):
        self._setBool(3, value)

    def getSelectedNation(self):
        return NationEnum(self._getString(4))

    def setSelectedNation(self, value):
        self._setString(4, value.value)

    def getAvailableNations(self):
        return self._getArray(5)

    def setAvailableNations(self, value):
        self._setArray(5, value)

    @staticmethod
    def getAvailableNationsType():
        return NationEnum

    def getTechTreeNodes(self):
        return self._getMap(6)

    def setTechTreeNodes(self, value):
        self._setMap(6, value)

    @staticmethod
    def getTechTreeNodesType():
        return (int, unicode)

    def getNodeOverrides(self):
        return self._getMap(7)

    def setNodeOverrides(self, value):
        self._setMap(7, value)

    @staticmethod
    def getNodeOverridesType():
        return (int, unicode)

    def _initialize(self):
        super(TechTreeViewModel, self)._initialize()
        self._addViewModelProperty('router', RouterModel())
        self._addNumberProperty('firstHighlightedLevel', 10)
        self._addBoolProperty('showWelcomeAnimation', False)
        self._addBoolProperty('collectableVehiclesAvailable', False)
        self._addStringProperty('selectedNation', NationEnum.CZECHOSLOVAKIA.value)
        self._addArrayProperty('availableNations', Array())
        self._addMapProperty('techTreeNodes', Map(int, unicode))
        self._addMapProperty('nodeOverrides', Map(int, unicode))
        self.onOpenAboutVehicle = self._addCommand('onOpenAboutVehicle')
        self.onAddToCompare = self._addCommand('onAddToCompare')
        self.onOpenCollectableVehicles = self._addCommand('onOpenCollectableVehicles')
        self.onOpenPremiumShop = self._addCommand('onOpenPremiumShop')
