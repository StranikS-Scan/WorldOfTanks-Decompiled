# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_album_main_model.py
import typing
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class NewYearAlbumMainModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onBackBtnClick', 'onPictureBtnClick')

    @property
    def sideBar(self):
        return self._getViewModel(0)

    def getCurrentAlbum(self):
        return self._getView(1)

    def setCurrentAlbum(self, value):
        self._setView(1, value)

    def getBackViewName(self):
        return self._getResource(2)

    def setBackViewName(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(NewYearAlbumMainModel, self)._initialize()
        self._addViewModelProperty('sideBar', UserListModel())
        self._addViewProperty('currentAlbum')
        self._addResourceProperty('backViewName', Resource.INVALID)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onBackBtnClick = self._addCommand('onBackBtnClick')
        self.onPictureBtnClick = self._addCommand('onPictureBtnClick')
