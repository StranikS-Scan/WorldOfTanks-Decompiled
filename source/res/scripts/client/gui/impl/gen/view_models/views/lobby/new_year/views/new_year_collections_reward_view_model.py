# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_collections_reward_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class NewYearCollectionsRewardViewModel(ViewModel):
    __slots__ = ('onGetStyleButton', 'onGoToCollectionButton', 'onPreviewStyleButton', 'onCollectionNameChanged')

    def __init__(self, properties=13, commands=4):
        super(NewYearCollectionsRewardViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def styleAdditionals(self):
        return self._getViewModel(0)

    @property
    def styleTabs(self):
        return self._getViewModel(1)

    @property
    def compatibleNations(self):
        return self._getViewModel(2)

    def getCost(self):
        return self._getNumber(3)

    def setCost(self, value):
        self._setNumber(3, value)

    def getCurrentCollectionName(self):
        return self._getString(4)

    def setCurrentCollectionName(self, value):
        self._setString(4, value)

    def getYear(self):
        return self._getString(5)

    def setYear(self, value):
        self._setString(5, value)

    def getCurrentYear(self):
        return self._getString(6)

    def setCurrentYear(self, value):
        self._setString(6, value)

    def getLevels(self):
        return self._getString(7)

    def setLevels(self, value):
        self._setString(7, value)

    def getIsEnough(self):
        return self._getBool(8)

    def setIsEnough(self, value):
        self._setBool(8, value)

    def getIsPremium(self):
        return self._getBool(9)

    def setIsPremium(self, value):
        self._setBool(9, value)

    def getIsAllNations(self):
        return self._getBool(10)

    def setIsAllNations(self, value):
        self._setBool(10, value)

    def getIsAllLevels(self):
        return self._getBool(11)

    def setIsAllLevels(self, value):
        self._setBool(11, value)

    def getIsMaxLvl(self):
        return self._getBool(12)

    def setIsMaxLvl(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(NewYearCollectionsRewardViewModel, self)._initialize()
        self._addViewModelProperty('styleAdditionals', UserListModel())
        self._addViewModelProperty('styleTabs', UserListModel())
        self._addViewModelProperty('compatibleNations', UserListModel())
        self._addNumberProperty('cost', 0)
        self._addStringProperty('currentCollectionName', 'NewYear')
        self._addStringProperty('year', 'ny21')
        self._addStringProperty('currentYear', '')
        self._addStringProperty('levels', '')
        self._addBoolProperty('isEnough', True)
        self._addBoolProperty('isPremium', True)
        self._addBoolProperty('isAllNations', True)
        self._addBoolProperty('isAllLevels', True)
        self._addBoolProperty('isMaxLvl', False)
        self.onGetStyleButton = self._addCommand('onGetStyleButton')
        self.onGoToCollectionButton = self._addCommand('onGoToCollectionButton')
        self.onPreviewStyleButton = self._addCommand('onPreviewStyleButton')
        self.onCollectionNameChanged = self._addCommand('onCollectionNameChanged')
