# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_album_cover_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class NewYearAlbumCoverViewModel(ViewModel):
    __slots__ = ('onPictureBtnClick', 'onOpenFactsBtnClick')

    def __init__(self, properties=2, commands=2):
        super(NewYearAlbumCoverViewModel, self).__init__(properties=properties, commands=commands)

    def getIsMaxLvl(self):
        return self._getBool(0)

    def setIsMaxLvl(self, value):
        self._setBool(0, value)

    def getTypesList(self):
        return self._getArray(1)

    def setTypesList(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(NewYearAlbumCoverViewModel, self)._initialize()
        self._addBoolProperty('isMaxLvl', False)
        self._addArrayProperty('typesList', Array())
        self.onPictureBtnClick = self._addCommand('onPictureBtnClick')
        self.onOpenFactsBtnClick = self._addCommand('onOpenFactsBtnClick')
