# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_album_main_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class NewYearAlbumMainModel(ViewModel):
    __slots__ = ('onSwitchContent', 'onCloseBtnClick', 'onPictureBtnClick')

    def __init__(self, properties=2, commands=3):
        super(NewYearAlbumMainModel, self).__init__(properties=properties, commands=commands)

    def getItemsTabBar(self):
        return self._getArray(0)

    def setItemsTabBar(self, value):
        self._setArray(0, value)

    def getStartIndex(self):
        return self._getNumber(1)

    def setStartIndex(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NewYearAlbumMainModel, self)._initialize()
        self._addArrayProperty('itemsTabBar', Array())
        self._addNumberProperty('startIndex', 0)
        self.onSwitchContent = self._addCommand('onSwitchContent')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onPictureBtnClick = self._addCommand('onPictureBtnClick')
