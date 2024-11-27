# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/battle_page/prebattle_carousel_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.battle.battle_page.prebattle_vehicle_model import PrebattleVehicleModel

class PrebattleCarouselViewModel(ViewModel):
    __slots__ = ('onVehicleClick', 'onVehicleSelect', 'onApplyFavoritesFilter', 'onApplyRentedFilter', 'onClearFilters', 'onSetDualRow')

    def __init__(self, properties=6, commands=6):
        super(PrebattleCarouselViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicles(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehiclesType():
        return PrebattleVehicleModel

    def getIsLoading(self):
        return self._getBool(1)

    def setIsLoading(self, value):
        self._setBool(1, value)

    def getRentedFilter(self):
        return self._getBool(2)

    def setRentedFilter(self, value):
        self._setBool(2, value)

    def getFavoritesFilter(self):
        return self._getBool(3)

    def setFavoritesFilter(self, value):
        self._setBool(3, value)

    def getIsDualRow(self):
        return self._getBool(4)

    def setIsDualRow(self, value):
        self._setBool(4, value)

    def getIsPopoverOpen(self):
        return self._getBool(5)

    def setIsPopoverOpen(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(PrebattleCarouselViewModel, self)._initialize()
        self._addViewModelProperty('vehicles', UserListModel())
        self._addBoolProperty('isLoading', False)
        self._addBoolProperty('rentedFilter', False)
        self._addBoolProperty('favoritesFilter', False)
        self._addBoolProperty('isDualRow', False)
        self._addBoolProperty('isPopoverOpen', False)
        self.onVehicleClick = self._addCommand('onVehicleClick')
        self.onVehicleSelect = self._addCommand('onVehicleSelect')
        self.onApplyFavoritesFilter = self._addCommand('onApplyFavoritesFilter')
        self.onApplyRentedFilter = self._addCommand('onApplyRentedFilter')
        self.onClearFilters = self._addCommand('onClearFilters')
        self.onSetDualRow = self._addCommand('onSetDualRow')
