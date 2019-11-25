# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/prem_dashboard_maps_blacklist_card_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class PremDashboardMapsBlacklistCardModel(ViewModel):
    __slots__ = ('onGoToMapsBlacklistView',)

    def __init__(self, properties=4, commands=1):
        super(PremDashboardMapsBlacklistCardModel, self).__init__(properties=properties, commands=commands)

    @property
    def disabledMaps(self):
        return self._getViewModel(0)

    def getIsAvailable(self):
        return self._getBool(1)

    def setIsAvailable(self, value):
        self._setBool(1, value)

    def getIsBasePremiumActive(self):
        return self._getBool(2)

    def setIsBasePremiumActive(self, value):
        self._setBool(2, value)

    def getIsTankPremiumActive(self):
        return self._getBool(3)

    def setIsTankPremiumActive(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(PremDashboardMapsBlacklistCardModel, self)._initialize()
        self._addViewModelProperty('disabledMaps', ListModel())
        self._addBoolProperty('isAvailable', True)
        self._addBoolProperty('isBasePremiumActive', False)
        self._addBoolProperty('isTankPremiumActive', True)
        self.onGoToMapsBlacklistView = self._addCommand('onGoToMapsBlacklistView')
