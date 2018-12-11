# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_album_page19_view_model.py
from gui.impl.gen.view_models.new_year.views.new_year_album_page_view_model import NewYearAlbumPageViewModel

class NewYearAlbumPage19ViewModel(NewYearAlbumPageViewModel):
    __slots__ = ('onCountAnimFinish', 'onBonusAnimFinish', 'onToysAnimFinish', 'onStampAnimFinish')

    def getTotalToys(self):
        return self._getNumber(12)

    def setTotalToys(self, value):
        self._setNumber(12, value)

    def getCurrentToys(self):
        return self._getNumber(13)

    def setCurrentToys(self, value):
        self._setNumber(13, value)

    def getBonusValue(self):
        return self._getNumber(14)

    def setBonusValue(self, value):
        self._setNumber(14, value)

    def getNewCurrentToys(self):
        return self._getNumber(15)

    def setNewCurrentToys(self, value):
        self._setNumber(15, value)

    def getNewBonusValue(self):
        return self._getNumber(16)

    def setNewBonusValue(self, value):
        self._setNumber(16, value)

    def getIsToysShow(self):
        return self._getBool(17)

    def setIsToysShow(self, value):
        self._setBool(17, value)

    def getIsStampShow(self):
        return self._getBool(18)

    def setIsStampShow(self, value):
        self._setBool(18, value)

    def getNewToysCount(self):
        return self._getNumber(19)

    def setNewToysCount(self, value):
        self._setNumber(19, value)

    def getIsAnimation(self):
        return self._getBool(20)

    def setIsAnimation(self, value):
        self._setBool(20, value)

    def getFadeIn(self):
        return self._getBool(21)

    def setFadeIn(self, value):
        self._setBool(21, value)

    def _initialize(self):
        super(NewYearAlbumPage19ViewModel, self)._initialize()
        self._addNumberProperty('totalToys', 0)
        self._addNumberProperty('currentToys', -1)
        self._addNumberProperty('bonusValue', -1)
        self._addNumberProperty('newCurrentToys', -1)
        self._addNumberProperty('newBonusValue', -1)
        self._addBoolProperty('isToysShow', False)
        self._addBoolProperty('isStampShow', False)
        self._addNumberProperty('newToysCount', 0)
        self._addBoolProperty('isAnimation', False)
        self._addBoolProperty('fadeIn', False)
        self.onCountAnimFinish = self._addCommand('onCountAnimFinish')
        self.onBonusAnimFinish = self._addCommand('onBonusAnimFinish')
        self.onToysAnimFinish = self._addCommand('onToysAnimFinish')
        self.onStampAnimFinish = self._addCommand('onStampAnimFinish')
