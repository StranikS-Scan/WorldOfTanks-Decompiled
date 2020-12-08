# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_album_page21_view_model.py
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_album_page_view_model import NewYearAlbumPageViewModel

class NewYearAlbumPage21ViewModel(NewYearAlbumPageViewModel):
    __slots__ = ('onHangMegaToy',)

    def __init__(self, properties=23, commands=7):
        super(NewYearAlbumPage21ViewModel, self).__init__(properties=properties, commands=commands)

    def getBonusValue(self):
        return self._getReal(19)

    def setBonusValue(self, value):
        self._setReal(19, value)

    def getCreditBonusValue(self):
        return self._getReal(20)

    def setCreditBonusValue(self, value):
        self._setReal(20, value)

    def getIsToysShow(self):
        return self._getBool(21)

    def setIsToysShow(self, value):
        self._setBool(21, value)

    def getIsAnimation(self):
        return self._getBool(22)

    def setIsAnimation(self, value):
        self._setBool(22, value)

    def _initialize(self):
        super(NewYearAlbumPage21ViewModel, self)._initialize()
        self._addRealProperty('bonusValue', 0.0)
        self._addRealProperty('creditBonusValue', 0.0)
        self._addBoolProperty('isToysShow', False)
        self._addBoolProperty('isAnimation', False)
        self.onHangMegaToy = self._addCommand('onHangMegaToy')
