# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/collection/collection_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.collection.item_model import ItemModel
from gui.impl.gen.view_models.views.lobby.collection.reward_info_model import RewardInfoModel
from gui.impl.gen.view_models.views.lobby.collection.tab_model import TabModel

class CollectionViewModel(ViewModel):
    __slots__ = ('onSetItemReceived', 'onSetRewardReceived', 'onSetProgressItemsReceived', 'onOpenItemPreview', 'onFinishTutorial', 'onTabSelected', 'onPageChanged', 'onClose')

    def __init__(self, properties=11, commands=8):
        super(CollectionViewModel, self).__init__(properties=properties, commands=commands)

    def getBackButtonText(self):
        return self._getString(0)

    def setBackButtonText(self, value):
        self._setString(0, value)

    def getCurrentCollection(self):
        return self._getString(1)

    def setCurrentCollection(self, value):
        self._setString(1, value)

    def getIsCompleted(self):
        return self._getBool(2)

    def setIsCompleted(self, value):
        self._setBool(2, value)

    def getIsTutorial(self):
        return self._getBool(3)

    def setIsTutorial(self, value):
        self._setBool(3, value)

    def getPage(self):
        return self._getNumber(4)

    def setPage(self, value):
        self._setNumber(4, value)

    def getTabs(self):
        return self._getArray(5)

    def setTabs(self, value):
        self._setArray(5, value)

    @staticmethod
    def getTabsType():
        return TabModel

    def getItems(self):
        return self._getArray(6)

    def setItems(self, value):
        self._setArray(6, value)

    @staticmethod
    def getItemsType():
        return ItemModel

    def getMaxItemsCount(self):
        return self._getNumber(7)

    def setMaxItemsCount(self, value):
        self._setNumber(7, value)

    def getReceivedItemsCount(self):
        return self._getNumber(8)

    def setReceivedItemsCount(self, value):
        self._setNumber(8, value)

    def getPrevReceivedItemsCount(self):
        return self._getNumber(9)

    def setPrevReceivedItemsCount(self, value):
        self._setNumber(9, value)

    def getRewardsInfo(self):
        return self._getArray(10)

    def setRewardsInfo(self, value):
        self._setArray(10, value)

    @staticmethod
    def getRewardsInfoType():
        return RewardInfoModel

    def _initialize(self):
        super(CollectionViewModel, self)._initialize()
        self._addStringProperty('backButtonText', '')
        self._addStringProperty('currentCollection', 'defaultConfig')
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('isTutorial', True)
        self._addNumberProperty('page', -1)
        self._addArrayProperty('tabs', Array())
        self._addArrayProperty('items', Array())
        self._addNumberProperty('maxItemsCount', 0)
        self._addNumberProperty('receivedItemsCount', 0)
        self._addNumberProperty('prevReceivedItemsCount', 0)
        self._addArrayProperty('rewardsInfo', Array())
        self.onSetItemReceived = self._addCommand('onSetItemReceived')
        self.onSetRewardReceived = self._addCommand('onSetRewardReceived')
        self.onSetProgressItemsReceived = self._addCommand('onSetProgressItemsReceived')
        self.onOpenItemPreview = self._addCommand('onOpenItemPreview')
        self.onFinishTutorial = self._addCommand('onFinishTutorial')
        self.onTabSelected = self._addCommand('onTabSelected')
        self.onPageChanged = self._addCommand('onPageChanged')
        self.onClose = self._addCommand('onClose')
