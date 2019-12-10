# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_album_page_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class NewYearAlbumPageViewModel(ViewModel):
    __slots__ = ('onGoToRewards', 'onChangeData', 'onFadeOnFinish', 'onCloseBtnClick', 'onToyClick', 'onPreChangeTypeName', 'onPreChangeRank')

    def __init__(self, properties=16, commands=7):
        super(NewYearAlbumPageViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def toysList(self):
        return self._getViewModel(0)

    def getCurrentType(self):
        return self._getString(1)

    def setCurrentType(self, value):
        self._setString(1, value)

    def getCurrentRank(self):
        return self._getNumber(2)

    def setCurrentRank(self, value):
        self._setNumber(2, value)

    def getTypesList(self):
        return self._getArray(3)

    def setTypesList(self, value):
        self._setArray(3, value)

    def getIsStampShow(self):
        return self._getBool(4)

    def setIsStampShow(self, value):
        self._setBool(4, value)

    def getHasStamp(self):
        return self._getBool(5)

    def setHasStamp(self, value):
        self._setBool(5, value)

    def getIsGetStamp(self):
        return self._getBool(6)

    def setIsGetStamp(self, value):
        self._setBool(6, value)

    def getFadeOut(self):
        return self._getBool(7)

    def setFadeOut(self, value):
        self._setBool(7, value)

    def getFadeOutList(self):
        return self._getBool(8)

    def setFadeOutList(self, value):
        self._setBool(8, value)

    def getCurrentToys(self):
        return self._getNumber(9)

    def setCurrentToys(self, value):
        self._setNumber(9, value)

    def getTotalToys(self):
        return self._getNumber(10)

    def setTotalToys(self, value):
        self._setNumber(10, value)

    def getIsNeedShowScroll(self):
        return self._getBool(11)

    def setIsNeedShowScroll(self, value):
        self._setBool(11, value)

    def getCurrentRomanRank(self):
        return self._getString(12)

    def setCurrentRomanRank(self, value):
        self._setString(12, value)

    def getCanChange(self):
        return self._getBool(13)

    def setCanChange(self, value):
        self._setBool(13, value)

    def getFadeIn(self):
        return self._getBool(14)

    def setFadeIn(self, value):
        self._setBool(14, value)

    def getNewToysCount(self):
        return self._getNumber(15)

    def setNewToysCount(self, value):
        self._setNumber(15, value)

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
        self._addBoolProperty('isNeedShowScroll', False)
        self._addStringProperty('currentRomanRank', '')
        self._addBoolProperty('canChange', True)
        self._addBoolProperty('fadeIn', False)
        self._addNumberProperty('newToysCount', 0)
        self.onGoToRewards = self._addCommand('onGoToRewards')
        self.onChangeData = self._addCommand('onChangeData')
        self.onFadeOnFinish = self._addCommand('onFadeOnFinish')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onToyClick = self._addCommand('onToyClick')
        self.onPreChangeTypeName = self._addCommand('onPreChangeTypeName')
        self.onPreChangeRank = self._addCommand('onPreChangeRank')
