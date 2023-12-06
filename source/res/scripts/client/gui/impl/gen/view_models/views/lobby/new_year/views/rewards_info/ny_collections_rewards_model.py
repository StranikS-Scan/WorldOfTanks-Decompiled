# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/rewards_info/ny_collections_rewards_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.new_year_collection_additional import NewYearCollectionAdditional
from gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.new_year_collection_style_tab import NewYearCollectionStyleTab

class CollectionState(IntEnum):
    CURRENTYEAR = 0
    MAXLVLNOTREACHED = 1
    LACKSHARDS = 2
    READYTOGET = 3
    RECEIVED = 4
    RECEIVEDEARLIER = 5


class NyCollectionsRewardsModel(ViewModel):
    __slots__ = ('onGetStyleButton', 'onGoToCollectionButton', 'onPreviewStyleButton', 'onCollectionNameChanged')

    def __init__(self, properties=11, commands=4):
        super(NyCollectionsRewardsModel, self).__init__(properties=properties, commands=commands)

    def getStyleName(self):
        return self._getString(0)

    def setStyleName(self, value):
        self._setString(0, value)

    def getNations(self):
        return self._getArray(1)

    def setNations(self, value):
        self._setArray(1, value)

    @staticmethod
    def getNationsType():
        return unicode

    def getLevels(self):
        return self._getArray(2)

    def setLevels(self, value):
        self._setArray(2, value)

    @staticmethod
    def getLevelsType():
        return int

    def getStyleTooltipId(self):
        return self._getNumber(3)

    def setStyleTooltipId(self, value):
        self._setNumber(3, value)

    def getCost(self):
        return self._getNumber(4)

    def setCost(self, value):
        self._setNumber(4, value)

    def getCollectionState(self):
        return CollectionState(self._getNumber(5))

    def setCollectionState(self, value):
        self._setNumber(5, value.value)

    def getCurrentCollectionName(self):
        return self._getString(6)

    def setCurrentCollectionName(self, value):
        self._setString(6, value)

    def getYear(self):
        return self._getString(7)

    def setYear(self, value):
        self._setString(7, value)

    def getIsPremium(self):
        return self._getBool(8)

    def setIsPremium(self, value):
        self._setBool(8, value)

    def getStyleAdditionals(self):
        return self._getArray(9)

    def setStyleAdditionals(self, value):
        self._setArray(9, value)

    @staticmethod
    def getStyleAdditionalsType():
        return NewYearCollectionAdditional

    def getStyleTabs(self):
        return self._getArray(10)

    def setStyleTabs(self, value):
        self._setArray(10, value)

    @staticmethod
    def getStyleTabsType():
        return NewYearCollectionStyleTab

    def _initialize(self):
        super(NyCollectionsRewardsModel, self)._initialize()
        self._addStringProperty('styleName', '')
        self._addArrayProperty('nations', Array())
        self._addArrayProperty('levels', Array())
        self._addNumberProperty('styleTooltipId', 0)
        self._addNumberProperty('cost', 0)
        self._addNumberProperty('collectionState')
        self._addStringProperty('currentCollectionName', 'NewYear')
        self._addStringProperty('year', 'ny21')
        self._addBoolProperty('isPremium', False)
        self._addArrayProperty('styleAdditionals', Array())
        self._addArrayProperty('styleTabs', Array())
        self.onGetStyleButton = self._addCommand('onGetStyleButton')
        self.onGoToCollectionButton = self._addCommand('onGoToCollectionButton')
        self.onPreviewStyleButton = self._addCommand('onPreviewStyleButton')
        self.onCollectionNameChanged = self._addCommand('onCollectionNameChanged')
