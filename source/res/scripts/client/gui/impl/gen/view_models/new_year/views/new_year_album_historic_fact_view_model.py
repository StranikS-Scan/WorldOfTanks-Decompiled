# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_album_historic_fact_view_model.py
from frameworks.wulf import ViewModel

class NewYearAlbumHistoricFactViewModel(ViewModel):
    __slots__ = ('onBackBtnClick', 'onPrevBtnClick', 'onNextBtnClick', 'onCloseBtnClick')

    def getMaxProgressLevel(self):
        return self._getNumber(0)

    def setMaxProgressLevel(self, value):
        self._setNumber(0, value)

    def getCurrentProgressLevel(self):
        return self._getNumber(1)

    def setCurrentProgressLevel(self, value):
        self._setNumber(1, value)

    def getCurrentFactIndex(self):
        return self._getNumber(2)

    def setCurrentFactIndex(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(NewYearAlbumHistoricFactViewModel, self)._initialize()
        self._addNumberProperty('maxProgressLevel', 0)
        self._addNumberProperty('currentProgressLevel', 0)
        self._addNumberProperty('currentFactIndex', 0)
        self.onBackBtnClick = self._addCommand('onBackBtnClick')
        self.onPrevBtnClick = self._addCommand('onPrevBtnClick')
        self.onNextBtnClick = self._addCommand('onNextBtnClick')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
