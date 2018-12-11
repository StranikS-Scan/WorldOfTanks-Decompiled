# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/navigation.py
from collections import namedtuple
from adisp import process
from frameworks.wulf import Resource
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.framework import ScopeTemplates
from gui.app_loader import sf_lobby
from gui.impl.gen import R
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.pub import ViewImpl
from gui.shared import event_dispatcher, g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.events import LobbyHeaderMenuEvent
from gui.shared.ny_vignette_settings_switcher import checkVignetteSettings
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from helpers import dependency
from items.components.ny_constants import CustomizationObjects
from new_year.ny_constants import OBJECT_TO_ANCHOR, ANCHOR_TO_OBJECT
from shared_utils import CONST_CONTAINER
from skeletons.new_year import ICustomizableObjectsManager, INewYearController
from soft_exception import SoftException
DEFAULT_CRAFT_FILTER = {'toyType': 0,
 'setting': 0,
 'rank': 0}
_SWITCH_OBJECT_SOUND_EVENTS = {CustomizationObjects.FIR: NewYearSoundEvents.TRANSITION_TREE,
 CustomizationObjects.PARKING: NewYearSoundEvents.TRANSITION_SNOWTANK,
 CustomizationObjects.FIELD_KITCHEN: NewYearSoundEvents.TRANSITION_KITCHEN,
 CustomizationObjects.ILLUMINATION: NewYearSoundEvents.TRANSITION_LIGHT}

class _NavigationState(object):

    def __init__(self):
        self.__currentObject = None
        self.__isInternalSwitch = False
        self.__lastViewedObject = None
        return

    def getCurrentObject(self):
        return self.__currentObject

    @property
    def lastViewedObject(self):
        return self.__lastViewedObject

    def setCurrentObject(self, objectName):
        self.__currentObject = objectName
        if objectName is not None:
            self.__lastViewedObject = objectName
        return

    def isInternalSwitch(self):
        return self.__isInternalSwitch

    def setIsInternalSwitch(self, isSwitching):
        self.__isInternalSwitch = isSwitching


_ViewLoadingParams = namedtuple('_ViewLoadingParams', 'layoutID, className')

class ViewAliases(CONST_CONTAINER):
    MAIN_VIEW = 'MAIN_VIEW'
    CRAFT_VIEW = 'NewYearCraftView'
    ALBUM_VIEW = 'AlbumMainView'
    ALBUM_PAGE19_VIEW = 'AlbumPage19View'
    ALBUM_PAGE18_VIEW = 'ALBUM_PAGE18_VIEW'
    REWARDS_VIEW = 'NewYearRewardsView'
    BREAK_VIEW = 'NewYearBreakDecorationsView'
    ALBUM_FACTS_VIEW = 'NewYearAlbumHistoricFactView'


class ViewLoadingParams(object):
    __viewsMap = None

    @classmethod
    def get(cls, paramsAlias):
        if cls.__viewsMap is None:
            cls.__viewsMap = cls._initLoadingParams()
        if paramsAlias not in cls.__viewsMap:
            raise SoftException('Unsupported view %', paramsAlias)
        return cls.__viewsMap[paramsAlias]

    @classmethod
    def _initLoadingParams(cls):
        from gui.impl.new_year.views.new_year_main_view import NewYearMainView
        from gui.impl.new_year.views.new_year_craft_view import NewYearCraftView
        from gui.impl.new_year.views.album.album_main_view import AlbumMainView
        from gui.impl.new_year.views.new_year_rewards_view import NewYearRewardsView
        from gui.impl.new_year.views.new_year_break_decorations_view import NewYearBreakDecorationsView
        from gui.impl.new_year.views.album.album_page19_view import AlbumPage19View
        from gui.impl.new_year.views.album.album_page18_view import AlbumPage18View
        from gui.impl.new_year.views.album.album_historic_fact_view import AlbumHistoricFactView
        return {ViewAliases.MAIN_VIEW: _ViewLoadingParams(R.views.newYearMainView, NewYearMainView),
         ViewAliases.CRAFT_VIEW: _ViewLoadingParams(R.views.newYearCraftView, NewYearCraftView),
         ViewAliases.ALBUM_VIEW: _ViewLoadingParams(R.views.newYearAlbumMainView, AlbumMainView),
         ViewAliases.ALBUM_PAGE19_VIEW: _ViewLoadingParams(R.views.newYearAlbumPageView, AlbumPage19View),
         ViewAliases.ALBUM_PAGE18_VIEW: _ViewLoadingParams(R.views.newYearAlbumPage18View, AlbumPage18View),
         ViewAliases.REWARDS_VIEW: _ViewLoadingParams(R.views.newYearRewardsView, NewYearRewardsView),
         ViewAliases.BREAK_VIEW: _ViewLoadingParams(R.views.newYearBreakDecorationsView, NewYearBreakDecorationsView),
         ViewAliases.ALBUM_FACTS_VIEW: _ViewLoadingParams(R.views.newYearAlbumHistoricFactView, AlbumHistoricFactView)}


class _NavigationHistory(object):

    def __init__(self):
        self.__chain = []
        self.__states = {}
        self.__goingBack = False

    def addToHistory(self, alias, state):
        self.__chain.append(alias)
        self.__states[alias] = state

    def getLast(self, pop=False):
        if self.__chain:
            if pop:
                return self.__chain.pop()
            return self.__chain[-1]

    def pop(self):
        self.__chain.pop()

    def getState(self, viewAlias):
        return self.__states.get(viewAlias)

    def setGoingBack(self, value):
        self.__goingBack = value

    def getGoingBack(self):
        return self.__goingBack

    def invalidateViewState(self, viewAlias):
        if viewAlias not in self.__chain and viewAlias in self.__states:
            del self.__states[viewAlias]

    def remove(self, viewAlias):
        if viewAlias in self.__chain:
            self.__chain.remove(viewAlias)
            del self.__states[viewAlias]

    def clear(self):
        self.__chain = []
        self.__states = {}

    @property
    def isEmpty(self):
        return len(self.__chain) == 0


class NewYearNavigation(ViewImpl):
    _navigationState = _NavigationState()
    _nyController = dependency.descriptor(INewYearController)
    _customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    _isScopeWatcher = True
    __craftFilter = DEFAULT_CRAFT_FILTER.copy()
    _navigationHistory = _NavigationHistory()
    _navigationAlias = None
    __slots__ = ('_newYearSounds',)

    def __init__(self, *args, **kwargs):
        super(NewYearNavigation, self).__init__(*args, **kwargs)
        self._newYearSounds = None
        return

    @classmethod
    def switchByObjectName(cls, objectName):
        if cls._navigationState.getCurrentObject() != objectName:
            cls.__switchTo(objectName)

    @classmethod
    def switchByAnchorName(cls, anchorName):
        objectName = ANCHOR_TO_OBJECT.get(anchorName)
        cls.__switchTo(objectName)

    @classmethod
    def getCurrentObject(cls):
        return cls._navigationState.getCurrentObject()

    @classmethod
    def resetCraftFilter(cls):
        cls.__craftFilter.update(DEFAULT_CRAFT_FILTER)

    @classmethod
    def _setCraftFilter(cls, toyType, setting, rank):
        cls.__craftFilter['toyType'] = toyType
        cls.__craftFilter['setting'] = setting
        cls.__craftFilter['rank'] = rank

    @classmethod
    def _getCraftFilter(cls):
        return (cls.__craftFilter['toyType'], cls.__craftFilter['setting'], cls.__craftFilter['rank'])

    def _initialize(self, soundConfig=None, *args, **kwargs):
        super(NewYearNavigation, self)._initialize(*args, **kwargs)
        self._newYearSounds = NewYearSoundsManager({} if soundConfig is None else soundConfig)
        self._nyController.onStateChanged += self.__onStateChanged
        if self._isScopeWatcher:
            checkVignetteSettings('ny_navigation')
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.handleEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)
            self.__restoreStateFromHistory()
            self._navigationHistory.remove(self.__getNavigationAlias())
        self._newYearSounds.onEnterView()
        return

    def _finalize(self):
        self._nyController.onStateChanged -= self.__onStateChanged
        self._newYearSounds.onExitView()
        if self._isScopeWatcher:
            if self._navigationState.isInternalSwitch():
                self._navigationState.setIsInternalSwitch(False)
                self._navigationHistory.invalidateViewState(self.__getNavigationAlias())
            else:
                self.__resetObject()
                g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
                g_eventBus.handleEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
                self._navigationHistory.clear()
        self._newYearSounds.clear()
        super(NewYearNavigation, self)._finalize()

    def _goToByViewAlias(self, viewAlias, *args, **kwargs):
        self._switchToView(ViewLoadingParams.get(viewAlias), *args, **kwargs)

    def _goToMainView(self):
        self._switchToView(ViewLoadingParams.get(ViewAliases.MAIN_VIEW), saveHistory=False)
        self._navigationHistory.clear()

    def _goToCraftView(self):
        self._switchToView(ViewLoadingParams.get(ViewAliases.CRAFT_VIEW))

    def _goToBreakView(self, toyType=None, craftInfo=None, blur3dScene=False, blurUI=False):
        self._switchToView(ViewLoadingParams.get(ViewAliases.BREAK_VIEW), toyType=toyType, craftInfo=craftInfo, blur3dScene=blur3dScene, blurUI=blurUI)

    def _goToAlbumView(self, *args, **kwargs):
        self._switchToView(ViewLoadingParams.get(ViewAliases.ALBUM_VIEW), *args, **kwargs)

    def _goToRewardsView(self):
        self._switchToView(ViewLoadingParams.get(ViewAliases.REWARDS_VIEW))

    def _goToHistoricFacts(self):
        self._switchToView(ViewLoadingParams.get(ViewAliases.ALBUM_FACTS_VIEW))

    @process
    def _switchToView(self, loadingParams, *args, **kwargs):
        saveHistory = kwargs.pop('saveHistory', True)
        popHistory = kwargs.pop('popHistory', False)
        readyToSwitch = yield self.__app.fadeManager.startFade()
        if readyToSwitch:
            self._navigationState.setIsInternalSwitch(True)
            if popHistory:
                self._navigationHistory.pop()
            if saveHistory:
                self.__preserveHistory()
            _loadView(loadingParams.layoutID, loadingParams.className, *args, **kwargs)

    @process
    def _switchObject(self, objectName):
        self.__playTransitionSound(objectName)
        readyToSwitch = yield self.__app.fadeManager.startFade()
        if readyToSwitch:
            self.__switchObject(objectName)
            self._afterObjectSwitch()

    def _afterObjectSwitch(self):
        pass

    def _getInfoForHistory(self):
        return None

    def _restoreState(self, stateInfo):
        pass

    def _getBackPageName(self):
        lastViewed = self._navigationHistory.getLast()
        return R.strings.ny.backButton.dyn(lastViewed) if lastViewed else Resource.INVALID

    def _goBack(self):
        if self._navigationHistory.isEmpty:
            return
        backPageAlias = self._navigationHistory.getLast()
        loadingParams = ViewLoadingParams.get(backPageAlias)
        if loadingParams:
            self._navigationHistory.setGoingBack(True)
            self._switchToView(loadingParams, saveHistory=False, popHistory=True)

    @sf_lobby
    def __app(self):
        return None

    @classmethod
    @process
    def __switchTo(cls, objectName):
        readyToSwitch = yield cls.__app.fadeManager.startFade()
        if readyToSwitch:
            cls.__switchUI(objectName)
            cls.__switchObject(objectName)

    @classmethod
    def __switchObject(cls, objectName):
        anchorName = OBJECT_TO_ANCHOR.get(objectName)
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.CUSTOMIZATION_CAMERA_ACTIVATED))
        cls._customizableObjectsMgr.switchCamera(anchorName)
        cls._navigationState.setCurrentObject(objectName)

    @classmethod
    def __switchUI(cls, objectName):
        currentObject = cls._navigationState.getCurrentObject()
        if objectName != currentObject:
            cls._navigationState.setCurrentObject(objectName)
            if currentObject is None:
                _loadView(*ViewLoadingParams.get(ViewAliases.MAIN_VIEW))
            elif objectName is None:
                event_dispatcher.showHangar()
        return

    def __resetObject(self):
        if self._navigationState.getCurrentObject() is not None:
            self.__switchObject(None)
        return

    def __playTransitionSound(self, objectName):
        eventName = _SWITCH_OBJECT_SOUND_EVENTS.get(objectName)
        if eventName:
            self._newYearSounds.playEvent(eventName)

    def __onStateChanged(self):
        if not self._nyController.isEnabled():
            NewYearNavigation.switchByObjectName(None)
        return

    def __getNavigationAlias(self):
        return self._navigationAlias or self.__class__.__name__

    def __preserveHistory(self):
        viewInfo = self._getInfoForHistory()
        if viewInfo is not None:
            name = self.__getNavigationAlias()
            self._navigationHistory.addToHistory(name, viewInfo)
        return

    def __restoreStateFromHistory(self):
        state = self._navigationHistory.getState(self.__getNavigationAlias())
        if self._navigationHistory.getGoingBack():
            if state:
                self._restoreState(state)
            self._navigationHistory.setGoingBack(False)


def _loadView(layoutID, viewClass, *args, **kwargs):
    g_eventBus.handleEvent(events.LoadUnboundViewEvent(layoutID, viewClass, ScopeTemplates.LOBBY_SUB_SCOPE, *args, **kwargs))
