# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_album_page_view_model.py
from frameworks.wulf import Array
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel

class NewYearAlbumPageViewModel(NyWithRomanNumbersModel):
    __slots__ = ('onGoToRewards', 'onChangeData', 'onFadeOnFinish', 'onToyClick', 'onPreChangeTypeName', 'onPreChangeRank')

    def __init__(self, properties=19, commands=6):
        super(NewYearAlbumPageViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def toysList(self):
        return self._getViewModel(1)

    def getCurrentType(self):
        return self._getString(2)

    def setCurrentType(self, value):
        self._setString(2, value)

    def getCurrentRank(self):
        return self._getNumber(3)

    def setCurrentRank(self, value):
        self._setNumber(3, value)

    def getTypesList(self):
        return self._getArray(4)

    def setTypesList(self, value):
        self._setArray(4, value)

    def getIsStampShow(self):
        return self._getBool(5)

    def setIsStampShow(self, value):
        self._setBool(5, value)

    def getHasStamp(self):
        return self._getBool(6)

    def setHasStamp(self, value):
        self._setBool(6, value)

    def getIsGetStamp(self):
        return self._getBool(7)

    def setIsGetStamp(self, value):
        self._setBool(7, value)

    def getFadeOut(self):
        return self._getBool(8)

    def setFadeOut(self, value):
        self._setBool(8, value)

    def getFadeOutList(self):
        return self._getBool(9)

    def setFadeOutList(self, value):
        self._setBool(9, value)

    def getCurrentToys(self):
        return self._getNumber(10)

    def setCurrentToys(self, value):
        self._setNumber(10, value)

    def getTotalToys(self):
        return self._getNumber(11)

    def setTotalToys(self, value):
        self._setNumber(11, value)

    def getCurrentRankToys(self):
        return self._getNumber(12)

    def setCurrentRankToys(self, value):
        self._setNumber(12, value)

    def getTotalRankToys(self):
        return self._getNumber(13)

    def setTotalRankToys(self, value):
        self._setNumber(13, value)

    def getIsNeedShowScroll(self):
        return self._getBool(14)

    def setIsNeedShowScroll(self, value):
        self._setBool(14, value)

    def getCurrentRomanRank(self):
        return self._getString(15)

    def setCurrentRomanRank(self, value):
        self._setString(15, value)

    def getCanChange(self):
        return self._getBool(16)

    def setCanChange(self, value):
        self._setBool(16, value)

    def getFadeIn(self):
        return self._getBool(17)

    def setFadeIn(self, value):
        self._setBool(17, value)

    def getNewToysCount(self):
        return self._getNumber(18)

    def setNewToysCount(self, value):
        self._setNumber(18, value)

    def _initialize(self):
        super(NewYearAlbumPageViewModel, self)._initialize()
        self._addViewModelProperty('toysList', UserListModel())
        self._addStringProperty('currentType', '')
        self._addNumberProperty('currentRank', 0)
        self._addArrayProperty('typesList', Array())
        self._addBoolProperty('isStampShow', False)
        self._addBoolProperty('hasStamp', False)
        self._addBoolProperty('isGetStamp', False)
        self._addBoolProperty('fadeOut', False)
        self._addBoolProperty('fadeOutList', False)
        self._addNumberProperty('currentToys', 0)
        self._addNumberProperty('totalToys', 0)
        self._addNumberProperty('currentRankToys', 0)
        self._addNumberProperty('totalRankToys', 0)
        self._addBoolProperty('isNeedShowScroll', False)
        self._addStringProperty('currentRomanRank', '')
        self._addBoolProperty('canChange', True)
        self._addBoolProperty('fadeIn', False)
        self._addNumberProperty('newToysCount', 0)
        self.onGoToRewards = self._addCommand('onGoToRewards')
        self.onChangeData = self._addCommand('onChangeData')
        self.onFadeOnFinish = self._addCommand('onFadeOnFinish')
        self.onToyClick = self._addCommand('onToyClick')
        self.onPreChangeTypeName = self._addCommand('onPreChangeTypeName')
        self.onPreChangeRank = self._addCommand('onPreChangeRank')
