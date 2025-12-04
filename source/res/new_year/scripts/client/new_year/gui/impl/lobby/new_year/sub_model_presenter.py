# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/sub_model_presenter.py
import typing
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from new_year.gui.impl.new_year.history_navigation import NavigationHistory
from new_year.gui.impl.new_year.navigation import NewYearNavigation, NewYearTabCache
from new_year.ny_constants import ViewAliases
from new_year.gui.impl.new_year.sounds import NewYearSoundsManager
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.vignette_settings_switcher import checkVignetteSettings
from helpers import dependency
from new_year.gui.shared.events import NewYearEvent
from new_year.ny_constants import InternalViewState
from skeletons.gui.shared import IItemsCache
from new_year.skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from typing import Callable, Optional, Sequence, Tuple
    from Event import Event
    from frameworks.wulf import View
    from cgf_components.view_camera_sync import IViewCameraSync

class SubModelPresenter(object):
    __slots__ = ('__viewModel', '__isLoaded', '__parentView', '__soundsManager')
    _INTERNAL_VIEW_STATE = InternalViewState.DEFAULT

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(SubModelPresenter, self).__init__()
        self.__parentView = parentView
        self.__viewModel = viewModel
        self.__isLoaded = False
        self.__soundsManager = NewYearSoundsManager({} if soundConfig is None else soundConfig)
        return

    @property
    def isLoaded(self):
        return self.__isLoaded

    @property
    def parentView(self):
        return self.__parentView

    @property
    def skipCameraFlightOnInit(self):
        return False

    @property
    def skipCameraFlightOnClose(self):
        return True

    def setInternalViewState(self, state, skipFlight=None):
        self.parentView.setInternalViewState(state, skipFlight)

    def setSwitchState(self, state):
        self.__parentView.viewModel.setSwitchState(state)

    def getViewModel(self):
        return self.__viewModel

    def getParentWindow(self):
        return self.parentView.getParentWindow()

    def initialize(self, *args, **kwargs):
        self.__soundsManager.onEnterView()
        self.__subscribe()
        if self._INTERNAL_VIEW_STATE is not None:
            self.setInternalViewState(self._INTERNAL_VIEW_STATE, kwargs.get('skipFlight', None))
        self.__isLoaded = True
        return

    def finalize(self):
        self.__isLoaded = False
        self.__unsubscribe()
        self.__soundsManager.onExitView()

    def switchFinalize(self):
        self.__isLoaded = False
        self.__soundsManager.onExitView()

    def clear(self):
        self.__viewModel = None
        self.__parentView = None
        self.__soundsManager.clear()
        return

    def createToolTip(self, event):
        return None

    def createToolTipContent(self, event, ctID):
        return None

    def createPopOverContent(self, event):
        return None

    def createPopOver(self, event):
        return None

    def setCameraState(self, cameraState):
        pass

    def setCameraSubState(self, subState, cameraState):
        pass

    def _getCallbacks(self):
        pass

    def _getListeners(self):
        pass

    def _getEvents(self):
        pass

    def __subscribe(self):
        g_clientUpdateManager.addCallbacks(dict(self._getCallbacks()))
        for eventBusArgs in self._getListeners():
            g_eventBus.addListener(*eventBusArgs)

        for event, handler in self._getEvents():
            event += handler

    def __unsubscribe(self):
        for event, handler in reversed(self._getEvents()):
            event -= handler

        for eventBusArgs in reversed(self._getListeners()):
            g_eventBus.removeListener(*eventBusArgs[:3])

        g_clientUpdateManager.removeObjectCallbacks(self)


class HistorySubModelPresenter(SubModelPresenter):
    __slots__ = ('__isPreLoaded',)
    _navigationHistory = NavigationHistory()
    _tabCache = NewYearTabCache()
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)
    _isScopeWatcher = True
    _navigationAlias = None

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(HistorySubModelPresenter, self).__init__(viewModel, parentView, soundConfig)
        self.__isPreLoaded = False

    def preLoad(self, *args, **kwargs):
        self.__isPreLoaded = True

    def initialize(self, *args, **kwargs):
        if not self.__isPreLoaded:
            self.preLoad()
        super(HistorySubModelPresenter, self).initialize(*args, **kwargs)
        if kwargs.get('clearHistoryNavigation', False):
            self._navigationHistory.clear()
        if self._isScopeWatcher:
            checkVignetteSettings('ny_navigation')
        self._updateBackButton()

    def finalize(self):
        if self._isScopeWatcher:
            self._navigationHistory.invalidateViewState(self._getNavigationAlias())
        self.__isPreLoaded = False
        super(HistorySubModelPresenter, self).finalize()

    @classmethod
    def clearNavigationHistory(cls):
        cls._navigationHistory.clear()

    @classmethod
    def clearTabCache(cls):
        cls._tabCache.clear()

    def addToHistoryForced(self):
        self.__preserveHistory()

    @property
    def currentTab(self):
        return None

    def goToAlbumView(self, tabName=None, *args, **kwargs):
        self._switchToView(ViewAliases.ALBUM_VIEW, tabName, *args, **kwargs)

    def _goToRewardsView(self, tabName=None, *args, **kwargs):
        self._switchToView(ViewAliases.REWARDS_VIEW, tabName, *args, **kwargs)

    def _goToByViewAlias(self, viewAlias, tabName=None, instantly=False, *args, **kwargs):
        self._switchToView(viewAlias, tabName, instantly, *args, **kwargs)

    def _goToMainView(self, tabName=None, *args, **kwargs):
        self._switchToView(ViewAliases.CITY_VIEW, tabName, *args, **kwargs)

    def _switchToView(self, aliasName, *args, **kwargs):
        saveHistory = kwargs.pop('saveHistory', False)
        popHistory = kwargs.pop('popHistory', False)
        if popHistory:
            self._navigationHistory.pop()
        if saveHistory:
            self.__preserveHistory()
        NewYearNavigation.switchToView(aliasName, *args, **kwargs)

    def _goBack(self):
        if self._navigationHistory.isEmpty:
            return
        backPageAlias = self._navigationHistory.getLast()
        if backPageAlias:
            self._navigationHistory.setGoingBack(True)
            self._switchToView(backPageAlias, saveHistory=False, popHistory=True, **self.__getStateFromHistory())

    def _getInfoForHistory(self):
        return None

    def _getBackPageName(self):
        lastViewed = self._navigationHistory.getLast()
        return R.strings.ny.backButton.dyn(lastViewed)() if lastViewed else R.invalid()

    def _updateBackButton(self):
        lastViewed = self._navigationHistory.getLast()
        if lastViewed:
            ctx = {'isVisible': True,
             'goTo': backport.text(self._getBackPageName()),
             'callback': self._goBack}
        else:
            ctx = {'isVisible': False}
        g_eventBus.handleEvent(NewYearEvent(NewYearEvent.UPDATE_BACK_BUTTON, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)

    def _getNavigationAlias(self):
        return self._navigationAlias or self.__class__.__name__

    def __preserveHistory(self):
        viewInfo = self._getInfoForHistory()
        if viewInfo is not None:
            name = self._getNavigationAlias()
            self._navigationHistory.addToHistory(name, viewInfo)
        return

    def __getStateFromHistory(self):
        lastAlias = self._navigationHistory.getLast()
        stateInfo = self._navigationHistory.getState(lastAlias)
        return {} if stateInfo is None else stateInfo
