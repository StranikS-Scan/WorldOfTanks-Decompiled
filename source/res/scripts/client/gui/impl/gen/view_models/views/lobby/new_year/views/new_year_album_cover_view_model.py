# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_album_cover_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel

class NewYearAlbumCoverViewModel(NyWithRomanNumbersModel):
    __slots__ = ('onPictureBtnClick', 'onOpenFactsBtnClick', 'onGotoBtnClick')

    def __init__(self, properties=4, commands=3):
        super(NewYearAlbumCoverViewModel, self).__init__(properties=properties, commands=commands)

    def getIsMaxLvl(self):
        return self._getBool(1)

    def setIsMaxLvl(self, value):
        self._setBool(1, value)

    def getIsNeedToShowCover(self):
        return self._getBool(2)

    def setIsNeedToShowCover(self, value):
        self._setBool(2, value)

    def getTypesList(self):
        return self._getArray(3)

    def setTypesList(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(NewYearAlbumCoverViewModel, self)._initialize()
        self._addBoolProperty('isMaxLvl', False)
        self._addBoolProperty('isNeedToShowCover', False)
        self._addArrayProperty('typesList', Array())
        self.onPictureBtnClick = self._addCommand('onPictureBtnClick')
        self.onOpenFactsBtnClick = self._addCommand('onOpenFactsBtnClick')
        self.onGotoBtnClick = self._addCommand('onGotoBtnClick')
