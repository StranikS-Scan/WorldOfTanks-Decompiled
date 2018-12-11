# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_album_model.py
from frameworks.wulf import ViewModel

class NewYearAlbumModel(ViewModel):
    __slots__ = ('onCloseBtnClick',)

    def getIsAlbum(self):
        return self._getBool(0)

    def setIsAlbum(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(NewYearAlbumModel, self)._initialize()
        self._addBoolProperty('isAlbum', False)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
