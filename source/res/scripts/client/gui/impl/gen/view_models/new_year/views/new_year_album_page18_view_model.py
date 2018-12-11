# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_album_page18_view_model.py
from gui.impl.gen.view_models.new_year.views.new_year_album_page_view_model import NewYearAlbumPageViewModel

class NewYearAlbumPage18ViewModel(NewYearAlbumPageViewModel):
    __slots__ = ()

    def getFadeIn(self):
        return self._getBool(12)

    def setFadeIn(self, value):
        self._setBool(12, value)

    def getTotalShards(self):
        return self._getNumber(13)

    def setTotalShards(self, value):
        self._setNumber(13, value)

    def getCurrentToys(self):
        return self._getNumber(14)

    def setCurrentToys(self, value):
        self._setNumber(14, value)

    def getTotalToys(self):
        return self._getNumber(15)

    def setTotalToys(self, value):
        self._setNumber(15, value)

    def getIsStampShow(self):
        return self._getBool(16)

    def setIsStampShow(self, value):
        self._setBool(16, value)

    def _initialize(self):
        super(NewYearAlbumPage18ViewModel, self)._initialize()
        self._addBoolProperty('fadeIn', False)
        self._addNumberProperty('totalShards', 0)
        self._addNumberProperty('currentToys', 0)
        self._addNumberProperty('totalToys', 0)
        self._addBoolProperty('isStampShow', False)
