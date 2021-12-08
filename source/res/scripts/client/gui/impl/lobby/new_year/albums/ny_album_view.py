# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/albums/ny_album_view.py
import typing
from account_helpers.AccountSettings import NY_OLD_COLLECTIONS_BY_YEAR_VISITED
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.albums.ny_album_view_model import NyAlbumViewModel
from gui.impl.lobby.new_year.albums.current_album_sub_model_presenter import CurrentAlbumSubModelPresenter
from gui.impl.lobby.new_year.albums.old_album_sub_model_presenter import OldAlbumSubModelPresenter
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.new_year.navigation import ViewAliases, NewYearTabCache as TabState
from gui.impl.new_year.new_year_helper import IS_ROMAN_NUMBERS_ALLOWED
from gui.impl.lobby.new_year.tooltips.ny_total_bonus_tooltip import NyTotalBonusTooltip
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import uniprof
from items.components.ny_constants import YEARS_INFO
from new_year.ny_constants import NyWidgetTopMenu, Collections, SyncDataKeys
from realm import CURRENT_REALM
from uilogging.ny.loggers import NyCurrentYearAlbumFlowLogger
if typing.TYPE_CHECKING:
    from gui.shared.event_dispatcher import NYTabCtx
    from gui.impl.lobby.new_year.albums.album_sub_model_presenter import AlbumSubModelPresenter
CURRENT_YEAR = Collections.NewYear22

class NyAlbumView(HistorySubModelPresenter):
    _navigationAlias = ViewAliases.ALBUM_VIEW
    __slots__ = ('__yearName', '_currentAlbumPresenter', '_oldAlbumPresenter')
    __currentYearFlowLogger = NyCurrentYearAlbumFlowLogger()

    def __init__(self, collectionsModel, parentView, *args, **kwargs):
        super(NyAlbumView, self).__init__(collectionsModel, parentView, *args, **kwargs)
        self._currentAlbumPresenter = CurrentAlbumSubModelPresenter(collectionsModel.currentAlbum, self)
        self._oldAlbumPresenter = OldAlbumSubModelPresenter(collectionsModel.oldAlbum, self)
        self.__yearName = CURRENT_YEAR

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def isCurrentYear(self):
        return self.__yearName == CURRENT_YEAR

    @property
    def albumPresenter(self):
        return self._currentAlbumPresenter if self.isCurrentYear else self._oldAlbumPresenter

    @property
    def currentTab(self):
        return self.__yearName

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.lobby.new_year.tooltips.new_year_album_toy_tooltip_content.NewYearAlbumToyTooltipContent():
            return self._currentAlbumPresenter.createToyTooltip(event)
        elif ctID == R.views.lobby.new_year.tooltips.new_year_toy_old_tooltip_content.NewYearAlbumToyOldTooltipContent():
            return self._oldAlbumPresenter.createToyTooltip(event)
        elif ctID == R.views.lobby.new_year.tooltips.NyCollectionBonusTooltip():
            return self._currentAlbumPresenter.createCollectionBonusTooltip()
        else:
            return NyTotalBonusTooltip() if ctID == R.views.lobby.new_year.tooltips.NyTotalBonusTooltip() else None

    @uniprof.regionDecorator(label='ny.album', scope='enter')
    def initialize(self, tabName=None, state=None, soundConfig=None, *args, **kwargs):
        self.__yearName = tabName if tabName else self._tabCache.getCurrentYear()
        g_eventBus.addListener(events.NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.onFadeInDone += self.__onAlbumFaded
        self.viewModel.onCollectionSelected += self.__onCollectionSelected
        self.viewModel.onOldCollectionsPreviewAttempt += self.__onOldCollectionsPreviewAttempt
        self._nyController.onDataUpdated += self.__onDataUpdated
        with self.viewModel.transaction() as model:
            model.setYearName(self.__yearName)
            model.setCurrentYear(CURRENT_YEAR)
            model.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
            model.setRealm(CURRENT_REALM)
            self.__initPreview(model)
        if state is not None:
            tabState, stateInfo = state
            self._tabCache.saveState(self.__yearName, state)
        else:
            tabState, stateInfo = self._tabCache.getState(self.__yearName)
        if tabState == TabState.PAGE_STATE:
            collection = stateInfo.get('collectionType')
            rank = stateInfo.get('rankToCollection', {}).get(collection, self.albumPresenter.DEFAULT_RANK)
            self.__fillSubModel(tabState, collection, rank)
        super(NyAlbumView, self).initialize(*args, **kwargs)
        return

    @uniprof.regionDecorator(label='ny.album', scope='exit')
    def finalize(self):
        g_eventBus.removeListener(events.NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.onCollectionSelected -= self.__onCollectionSelected
        self.viewModel.onOldCollectionsPreviewAttempt -= self.__onOldCollectionsPreviewAttempt
        self.viewModel.onFadeInDone -= self.__onAlbumFaded
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self._tabCache.saveCurrentYear(self.__yearName)
        self.__saveCurrentTabState()
        if self._currentAlbumPresenter.isLoaded:
            self._currentAlbumPresenter.finalize()
        if self._oldAlbumPresenter.isLoaded:
            self._oldAlbumPresenter.finalize()
        super(NyAlbumView, self).finalize()

    def clear(self):
        self._currentAlbumPresenter.clear()
        self._currentAlbumPresenter = None
        self._oldAlbumPresenter.clear()
        self._oldAlbumPresenter = None
        super(NyAlbumView, self).clear()
        return

    def _getInfoForHistory(self):
        return {}

    def _updateBackButton(self):
        tabState, _ = self._tabCache.getState(self.__yearName)
        if tabState == TabState.COVER_STATE:
            ctx = {'isVisible': False}
        else:
            ctx = {'isVisible': True,
             'caption': backport.text(R.strings.ny.backButton.label()),
             'goTo': backport.text(self._getBackPageName() or R.strings.ny.backButton.NyAlbumView()),
             'callback': self.__onBack}
        g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.UPDATE_BACK_BUTTON, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)

    def __initPreview(self, model):
        isCurrentYearSelected = self.__yearName == YEARS_INFO.CURRENT_YEAR_STR
        isMaxLevel = self._nyController.isMaxAtmosphereLevel()
        model.setIsCollectionsLocked(not isCurrentYearSelected and not isMaxLevel)
        self._nyController.markPreviousYearTabVisited(self.__yearName, NY_OLD_COLLECTIONS_BY_YEAR_VISITED)

    def __onSideBarSelected(self, event):
        ctx = event.ctx
        if ctx.menuName != NyWidgetTopMenu.COLLECTIONS:
            return
        if self.__yearName == ctx.tabName:
            return
        self.__saveCurrentTabState()
        self.__yearName = ctx.tabName
        with self.viewModel.transaction() as model:
            model.setIsFaded(True)

    def __onCollectionSelected(self, args):
        if args is None or 'collectionName' not in args:
            return
        else:
            state = (TabState.PAGE_STATE, {'collectionType': args['collectionName'],
              'rankToCollection': {args['collectionName']: self.albumPresenter.DEFAULT_RANK}})
            self._tabCache.saveState(self.__yearName, state)
            with self.viewModel.transaction() as model:
                model.setIsFaded(True)
            return

    def __onAlbumFaded(self):
        tabState, stateInfo = self._tabCache.getState(self.__yearName)
        collection = stateInfo.get('collectionType')
        rank = stateInfo.get('rankToCollection', {}).get(collection, self.albumPresenter.DEFAULT_RANK)
        self.__fillSubModel(tabState, collection, rank)
        self._updateBackButton()

    def __fillSubModel(self, tabState, collection, rank):
        albumBuilder = self.albumPresenter
        if albumBuilder.isLoaded:
            if not self.isCurrentYear:
                self._oldAlbumPresenter.updateBuilder(self.__yearName)
            albumBuilder.update(collectionType=collection, rank=rank)
        elif tabState == TabState.PAGE_STATE:
            albumBuilder.initialize(self.__yearName, collection, rank=rank)
        with self.viewModel.transaction() as model:
            model.setYearName(self.__yearName)
            model.setIsOpened(tabState == TabState.PAGE_STATE)
            model.setIsFaded(False)
            self.__initPreview(model)

    def __goToCoverState(self):
        state = (TabState.COVER_STATE, {})
        self._tabCache.saveState(self.__yearName, state)
        if self.albumPresenter.isLoaded:
            self.albumPresenter.finalize()
        with self.viewModel.transaction() as model:
            model.setIsFaded(True)

    def __saveCurrentTabState(self):
        stateInfo = self.albumPresenter.stateInfo
        tabState = TabState.COVER_STATE if stateInfo['collectionType'] is None else TabState.PAGE_STATE
        self._tabCache.saveState(self.__yearName, (tabState, stateInfo))
        return

    def __onBack(self):
        if self._navigationHistory.getLast():
            self._goBack()
        else:
            self.__goToCoverState()

    def __onOldCollectionsPreviewAttempt(self):
        self.__currentYearFlowLogger.logClick(self.__yearName, CURRENT_YEAR)
        self.__yearName = CURRENT_YEAR
        self.__goToCoverState()
        g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.SELECT_SIDEBAR_TAB_OUTSIDE, ctx={'menuName': NyWidgetTopMenu.COLLECTIONS,
         'tabName': Collections.NewYear22}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onDataUpdated(self, keys):
        if SyncDataKeys.LEVEL in keys:
            with self.viewModel.transaction() as model:
                self.__initPreview(model)
