# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/albums/ny_album_view_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel
from gui.impl.gen.view_models.views.lobby.new_year.views.albums.ny_current_album_model import NyCurrentAlbumModel
from gui.impl.gen.view_models.views.lobby.new_year.views.albums.ny_old_album_model import NyOldAlbumModel

class NyAlbumViewModel(NyWithRomanNumbersModel):
    __slots__ = ('onCollectionSelected', 'onOldCollectionsPreviewAttempt', 'onFadeInDone')

    def __init__(self, properties=9, commands=3):
        super(NyAlbumViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def currentAlbum(self):
        return self._getViewModel(1)

    @staticmethod
    def getCurrentAlbumType():
        return NyCurrentAlbumModel

    @property
    def oldAlbum(self):
        return self._getViewModel(2)

    @staticmethod
    def getOldAlbumType():
        return NyOldAlbumModel

    def getYearName(self):
        return self._getString(3)

    def setYearName(self, value):
        self._setString(3, value)

    def getCurrentYear(self):
        return self._getString(4)

    def setCurrentYear(self, value):
        self._setString(4, value)

    def getIsFaded(self):
        return self._getBool(5)

    def setIsFaded(self, value):
        self._setBool(5, value)

    def getIsOpened(self):
        return self._getBool(6)

    def setIsOpened(self, value):
        self._setBool(6, value)

    def getIsCollectionsLocked(self):
        return self._getBool(7)

    def setIsCollectionsLocked(self, value):
        self._setBool(7, value)

    def getRealm(self):
        return self._getString(8)

    def setRealm(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(NyAlbumViewModel, self)._initialize()
        self._addViewModelProperty('currentAlbum', NyCurrentAlbumModel())
        self._addViewModelProperty('oldAlbum', NyOldAlbumModel())
        self._addStringProperty('yearName', '')
        self._addStringProperty('currentYear', '')
        self._addBoolProperty('isFaded', False)
        self._addBoolProperty('isOpened', False)
        self._addBoolProperty('isCollectionsLocked', False)
        self._addStringProperty('realm', '')
        self.onCollectionSelected = self._addCommand('onCollectionSelected')
        self.onOldCollectionsPreviewAttempt = self._addCommand('onOldCollectionsPreviewAttempt')
        self.onFadeInDone = self._addCommand('onFadeInDone')
