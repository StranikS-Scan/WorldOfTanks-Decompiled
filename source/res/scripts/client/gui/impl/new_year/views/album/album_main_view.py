# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_main_view.py
from frameworks.wulf import ViewSettings
from gui.app_loader import sf_lobby
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_album_main_model import NewYearAlbumMainModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates
from gui.impl.new_year.sounds import NewYearSoundsManager
from gui.impl.new_year.views.album.album_tab_view import AlbumTabView
from gui.impl.new_year.views.tabs_controller import AlbumsTabsController
from helpers import uniprof
from new_year.collection_presenters import NY18CollectionPresenter, NY19CollectionPresenter
from new_year.ny_constants import Collections, SyncDataKeys
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from items import new_year
_COLLECTIONS = [NY19CollectionPresenter, NY18CollectionPresenter]
_DEFAULT_COLLECTION_NAME = Collections.NewYear19
_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {Collections.NewYear18: NewYearSoundEvents.ALBUM_SELECT_2018,
                                         Collections.NewYear19: NewYearSoundEvents.ALBUM_SELECT_2019,
                                         Collections.NewYear20: NewYearSoundEvents.ALBUM_SELECT_2020},
 NewYearSoundConfigKeys.EXIT_EVENT: {Collections.NewYear18: NewYearSoundEvents.ALBUM_SELECT_2018_EXIT,
                                     Collections.NewYear19: NewYearSoundEvents.ALBUM_SELECT_2019_EXIT,
                                     Collections.NewYear20: NewYearSoundEvents.ALBUM_SELECT_2020_EXIT}}

class AlbumMainView(NewYearHistoryNavigation):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__yearName', '__tabsController')

    def __init__(self, yearName=None, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_album_view.NewYearAlbumMainView())
        settings.model = NewYearAlbumMainModel()
        settings.args = (yearName,) + args
        settings.kwargs = kwargs
        super(AlbumMainView, self).__init__(settings)
        self.__tabsController = AlbumsTabsController()

    @property
    def viewModel(self):
        return super(AlbumMainView, self).getViewModel()

    @uniprof.regionDecorator(label='ny20.album', scope='enter')
    def _initialize(self, yearName=None, stateInfo=None):
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: NewYearSoundEvents.ALBUM_SELECT,
         NewYearSoundConfigKeys.EXIT_EVENT: NewYearSoundEvents.ALBUM_SELECT_EXIT,
         NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.ALBUM_SELECT}
        super(AlbumMainView, self)._initialize(soundConfig)
        self.viewModel.onPictureBtnClick += self.__onPictureBtnClick
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick
        self.viewModel.onSwitchContent += self.__onSwitchContent
        self._nyController.onDataUpdated += self.__onDataUpdated
        self.__yearName = yearName if yearName else self._tabCache.getCurrentYear()
        maxLevel = self._itemsCache.items.festivity.getMaxLevel()
        if self.__yearName == Collections.NewYear20 or maxLevel == new_year.CONSTS.MAX_ATMOSPHERE_LVL:
            NewYearSoundsManager.playEvent(_SOUNDS_MAP.get(NewYearSoundConfigKeys.ENTRANCE_EVENT, {}).get(self.__yearName))
        with self.viewModel.transaction() as tx:
            self.setChildView(R.dynamic_ids.newYearAlbumMain(), AlbumTabView(self.__yearName, stateInfo))
            self.__tabsController.updateTabModels(tx.getItemsTabBar())
            tx.setStartIndex(self.__tabsController.tabOrderKey(self.__yearName))

    @uniprof.regionDecorator(label='ny20.album', scope='exit')
    def _finalize(self):
        self.viewModel.onPictureBtnClick -= self.__onPictureBtnClick
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        self.viewModel.onSwitchContent -= self.__onSwitchContent
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self._tabCache.saveCurrentYear(self.__yearName)
        maxLevel = self._itemsCache.items.festivity.getMaxLevel()
        if self.__yearName == Collections.NewYear20 or maxLevel == new_year.CONSTS.MAX_ATMOSPHERE_LVL:
            NewYearSoundsManager.playEvent(_SOUNDS_MAP.get(NewYearSoundConfigKeys.EXIT_EVENT, {}).get(self.__yearName))
        super(AlbumMainView, self)._finalize()

    def _restoreState(self, stateInfo):
        self.__yearName = stateInfo

    @sf_lobby
    def __app(self):
        return None

    def __onCloseBtnClick(self, _=None):
        self._goToMainView()

    def __onPictureBtnClick(self, args):
        pass

    def __onSwitchContent(self, args):
        name = args['view']
        self._navigationHistory.clear()
        self.getChildView(R.dynamic_ids.newYearAlbumMain()).switchYear(name)
        maxLevel = self._itemsCache.items.festivity.getMaxLevel()
        if maxLevel == new_year.CONSTS.MAX_ATMOSPHERE_LVL:
            NewYearSoundsManager.playEvent(_SOUNDS_MAP.get(NewYearSoundConfigKeys.EXIT_EVENT, {}).get(self.__yearName))
        if maxLevel == new_year.CONSTS.MAX_ATMOSPHERE_LVL:
            NewYearSoundsManager.playEvent(_SOUNDS_MAP.get(NewYearSoundConfigKeys.ENTRANCE_EVENT, {}).get(name))
        self.__yearName = name

    def __onDataUpdated(self, keys):
        if SyncDataKeys.TOY_COLLECTION in keys:
            self.__tabsController.updateTabModels(self.viewModel.getItemsTabBar())
