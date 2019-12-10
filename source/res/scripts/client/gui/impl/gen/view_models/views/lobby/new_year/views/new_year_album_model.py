# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_album_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NewYearAlbumModel(ViewModel):
    __slots__ = ('onBackBtnClick', 'onPictureBtnClick')

    def __init__(self, properties=2, commands=2):
        super(NewYearAlbumModel, self).__init__(properties=properties, commands=commands)

    def getBackViewName(self):
        return self._getResource(0)

    def setBackViewName(self, value):
        self._setResource(0, value)

    def getIsAlbum(self):
        return self._getBool(1)

    def setIsAlbum(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(NewYearAlbumModel, self)._initialize()
        self._addResourceProperty('backViewName', R.invalid())
        self._addBoolProperty('isAlbum', False)
        self.onBackBtnClick = self._addCommand('onBackBtnClick')
        self.onPictureBtnClick = self._addCommand('onPictureBtnClick')
