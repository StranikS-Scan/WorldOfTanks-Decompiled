# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_card_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.festival.festival_items_info_view_model import FestivalItemsInfoViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.festival.festival_card_apply_model import FestivalCardApplyModel
from gui.impl.gen.view_models.views.lobby.festival.festival_player_card_view_model import FestivalPlayerCardViewModel
from gui.impl.gen.view_models.views.lobby.selected_filters_model import SelectedFiltersModel

class FestivalCardViewModel(FestivalItemsInfoViewModel):
    __slots__ = ('onBuyItem', 'onItemTypeChange', 'onSelectItem', 'onMarkAsSeenItem', 'onDogtagGenerator', 'onOpenMiniGames')

    @property
    def playerCard(self):
        return self._getViewModel(2)

    @property
    def items(self):
        return self._getViewModel(3)

    @property
    def filterModel(self):
        return self._getViewModel(4)

    @property
    def applyModel(self):
        return self._getViewModel(5)

    def getData(self):
        return self._getString(6)

    def setData(self, value):
        self._setString(6, value)

    def getItemTypes(self):
        return self._getArray(7)

    def setItemTypes(self, value):
        self._setArray(7, value)

    def getStartIndex(self):
        return self._getNumber(8)

    def setStartIndex(self, value):
        self._setNumber(8, value)

    def getIsCanApply(self):
        return self._getBool(9)

    def setIsCanApply(self, value):
        self._setBool(9, value)

    def getNotReceivedItems(self):
        return self._getArray(10)

    def setNotReceivedItems(self, value):
        self._setArray(10, value)

    def getIsRandomBtnEnabled(self):
        return self._getBool(11)

    def setIsRandomBtnEnabled(self, value):
        self._setBool(11, value)

    def getTotalMiniGamesAttempts(self):
        return self._getNumber(12)

    def setTotalMiniGamesAttempts(self, value):
        self._setNumber(12, value)

    def getRemainedMiniGamesAttempts(self):
        return self._getNumber(13)

    def setRemainedMiniGamesAttempts(self, value):
        self._setNumber(13, value)

    def getMiniGamesCooldown(self):
        return self._getNumber(14)

    def setMiniGamesCooldown(self, value):
        self._setNumber(14, value)

    def getIsMiniGamesEnabled(self):
        return self._getBool(15)

    def setIsMiniGamesEnabled(self, value):
        self._setBool(15, value)

    def getLowestRandomPrice(self):
        return self._getNumber(16)

    def setLowestRandomPrice(self, value):
        self._setNumber(16, value)

    def _initialize(self):
        super(FestivalCardViewModel, self)._initialize()
        self._addViewModelProperty('playerCard', FestivalPlayerCardViewModel())
        self._addViewModelProperty('items', UserListModel())
        self._addViewModelProperty('filterModel', SelectedFiltersModel())
        self._addViewModelProperty('applyModel', FestivalCardApplyModel())
        self._addStringProperty('data', '')
        self._addArrayProperty('itemTypes', Array())
        self._addNumberProperty('startIndex', 0)
        self._addBoolProperty('isCanApply', False)
        self._addArrayProperty('notReceivedItems', Array())
        self._addBoolProperty('isRandomBtnEnabled', False)
        self._addNumberProperty('totalMiniGamesAttempts', 0)
        self._addNumberProperty('remainedMiniGamesAttempts', 0)
        self._addNumberProperty('miniGamesCooldown', 0)
        self._addBoolProperty('isMiniGamesEnabled', False)
        self._addNumberProperty('lowestRandomPrice', 0)
        self.onBuyItem = self._addCommand('onBuyItem')
        self.onItemTypeChange = self._addCommand('onItemTypeChange')
        self.onSelectItem = self._addCommand('onSelectItem')
        self.onMarkAsSeenItem = self._addCommand('onMarkAsSeenItem')
        self.onDogtagGenerator = self._addCommand('onDogtagGenerator')
        self.onOpenMiniGames = self._addCommand('onOpenMiniGames')
