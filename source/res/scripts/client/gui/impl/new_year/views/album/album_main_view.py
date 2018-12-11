# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_main_view.py
from adisp import process
from frameworks.wulf import ViewFlags
from gui.app_loader import sf_lobby
from gui.impl.gen.view_models.new_year.components.new_year_album_side_bar_button_model import NewYearAlbumSideBarButtonModel
from gui.impl.gen.view_models.new_year.views.new_year_album_main_model import NewYearAlbumMainModel
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates
from gui.impl.new_year.sounds import NewYearSoundsManager
from gui.impl.new_year.views.album.album_cover_view import AlbumCoverView
from helpers import dependency
from items import ny19, collectibles
from items.components.ny_constants import TOY_SETTING_IDS_BY_NAME
from new_year.ny_constants import Collections, COLLECTIONS_SETTINGS
from skeletons.gui.shared import IItemsCache

def _getCollectionsCount(settings, collectionDistributions):
    result = 0
    for toySetting in settings:
        result += sum(collectionDistributions[TOY_SETTING_IDS_BY_NAME[toySetting]])

    return result


class _NY19CollectionPresenter(object):

    @staticmethod
    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def getCount(itemsCache=None):
        return _getCollectionsCount(COLLECTIONS_SETTINGS[Collections.NewYear19], itemsCache.items.festivity.getCollectionDistributions())

    @staticmethod
    def getName():
        return Collections.NewYear19

    @staticmethod
    def getTotalCount():
        return len(ny19.g_cache.toys)


class _NY18CollectionPresenter(object):

    @staticmethod
    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def getCount(itemsCache=None):
        return _getCollectionsCount(COLLECTIONS_SETTINGS[Collections.NewYear18], itemsCache.items.festivity.getCollectionDistributions())

    @staticmethod
    def getName():
        return Collections.NewYear18

    @staticmethod
    def getTotalCount():
        return len(collectibles.g_cache.ny18.toys)


_COLLECTIONS = [_NY19CollectionPresenter, _NY18CollectionPresenter]
_DEFAULT_COLLECTION_NAME = Collections.NewYear19

class AlbumMainView(NewYearNavigation):
    __slots__ = ('__collectionName',)

    def __init__(self, layoutID, collectionName=_DEFAULT_COLLECTION_NAME, *args, **kwargs):
        super(AlbumMainView, self).__init__(layoutID, ViewFlags.LOBBY_SUB_VIEW, NewYearAlbumMainModel, collectionName, *args, **kwargs)
        self.__collectionName = collectionName
        if not self._navigationHistory.getGoingBack():
            NewYearSoundsManager.playEvent(NewYearSoundEvents.ALBUM_SELECT)
            if collectionName == Collections.NewYear18:
                NewYearSoundsManager.playEvent(NewYearSoundEvents.ALBUM_SELECT_2018)
            else:
                NewYearSoundsManager.playEvent(NewYearSoundEvents.ALBUM_SELECT_2019)

    @property
    def viewModel(self):
        return super(AlbumMainView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        soundConfig = {NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.ALBUM_SELECT}
        super(AlbumMainView, self)._initialize(soundConfig)
        self.viewModel.sideBar.onUserSelectionChanged += self.__onSidebarClick
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick
        self.viewModel.onBackBtnClick += self.__onBackBtnClick
        self.viewModel.setBackViewName(self._getBackPageName())
        sideBar = self.viewModel.sideBar.getItems()
        with self.viewModel.transaction() as tx:
            for index, presenter in enumerate(_COLLECTIONS):
                btn = NewYearAlbumSideBarButtonModel()
                btn.setCollectionName(presenter.getName())
                btn.setCurrentValue(presenter.getCount())
                btn.setTotalValue(presenter.getTotalCount())
                btn.setIsSelected(presenter.getName() == self.__collectionName)
                sideBar.addViewModel(btn)
                if presenter.getName() == self.__collectionName:
                    tx.sideBar.addSelectedIndex(index)
                    tx.setCurrentAlbum(AlbumCoverView(presenter.getName()))

    def _finalize(self):
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        self.viewModel.onBackBtnClick -= self.__onBackBtnClick
        self.viewModel.sideBar.onUserSelectionChanged -= self.__onSidebarClick
        super(AlbumMainView, self)._finalize()

    def _restoreState(self, stateInfo):
        self.__collectionName = stateInfo

    @sf_lobby
    def __app(self):
        return None

    def __onCloseBtnClick(self, _=None):
        self.__playAlbumExitSounds()
        self._goToMainView()

    def __onBackBtnClick(self, _=None):
        self.__playAlbumExitSounds()
        self._goBack()

    def __playAlbumExitSounds(self):
        self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_EXIT)
        if self.__collectionName == Collections.NewYear18:
            self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_2018_EXIT)
        else:
            self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_2019_EXIT)

    @process
    def __onSidebarClick(self, item):
        readyToSwitch = yield self.__app.fadeManager.startFade()
        if readyToSwitch:
            name = item.getCollectionName()
            if name == Collections.NewYear18:
                self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_2019_EXIT)
                self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_2018)
            else:
                self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_2018_EXIT)
                self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_2019)
            self.viewModel.setCurrentAlbum(AlbumCoverView(name))
            self.__collectionName = name
