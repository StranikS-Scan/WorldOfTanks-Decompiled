# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_album_main_model.py
from frameworks.wulf import ViewModel

class NewYearAlbumMainModel(ViewModel):
    __slots__ = ('onSwitchContent', 'onPictureBtnClick')

    def __init__(self, properties=1, commands=2):
        super(NewYearAlbumMainModel, self).__init__(properties=properties, commands=commands)

    def getNextViewName(self):
        return self._getString(0)

    def setNextViewName(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(NewYearAlbumMainModel, self)._initialize()
        self._addStringProperty('nextViewName', '')
        self.onSwitchContent = self._addCommand('onSwitchContent')
        self.onPictureBtnClick = self._addCommand('onPictureBtnClick')
