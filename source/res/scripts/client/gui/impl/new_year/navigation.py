# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/navigation.py
from collections import namedtuple
import Event
from adisp import process
from frameworks.wulf import ViewStatus
from gui.app_loader import sf_lobby
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.pub import ViewImpl
from gui.shared import event_dispatcher, g_eventBus
from gui.shared.event_dispatcher import showNewYearMainView
from gui.shared.ny_vignette_settings_switcher import checkVignetteSettings
from helpers import dependency
from items.components.ny_constants import CustomizationObjects, RANDOM_VALUE
from new_year.craft_machine import mapToyParamsFromSrvToCraftUi
from new_year.ny_constants import OBJECT_TO_ANCHOR, ANCHOR_TO_OBJECT, NyWidgetTopMenu, Collections, AdditionalCameraObject
from shared_utils import CONST_CONTAINER
from skeletons.new_year import ICustomizableObjectsManager, INewYearController, INewYearCraftMachineController, ICelebritySceneController
from soft_exception import SoftException
_SWITCH_OBJECT_SOUND_EVENTS = {CustomizationObjects.FIR: NewYearSoundEvents.TRANSITION_TREE,
 CustomizationObjects.INSTALLATION: NewYearSoundEvents.TRANSITION_SNOWTANK,
 CustomizationObjects.TABLEFUL: NewYearSoundEvents.TRANSITION_KITCHEN,
 CustomizationObjects.ILLUMINATION: NewYearSoundEvents.TRANSITION_LIGHT,
 AdditionalCameraObject.MASCOT: NewYearSoundEvents.TRANSITION_TALISMAN,
 AdditionalCameraObject.CELEBRITY: NewYearSoundEvents.TRANSITION_CELEBRITY}

class _NavigationState(object):

    def __init__(self):
        self.__currentObject = None
        self.__isInternalSwitch = False
        self.__lastViewedObject = None
        self.__currentViewName = None
        return

    def getCurrentObject(self):
        return self.__currentObject

    def getCurrentViewName(self):
        return self.__currentViewName

    @property
    def lastViewedObject(self):
        return self.__lastViewedObject

    def setCurrentObject(self, objectName):
        self.__currentObject = objectName
        if objectName is not None:
            self.__lastViewedObject = objectName
        return

    def setCurrentView(self, currentView):
        self.__currentViewName = currentView

    def isInternalSwitch(self):
        return self.__isInternalSwitch

    def setIsInternalSwitch(self, isSwitching):
        self.__isInternalSwitch = isSwitching


class ViewTypes(object):
    UNBOUND = 1
    GAMEFACE = 2
    ACTION_SCRIPT = 3


ViewParams = namedtuple('ViewParams', ('clazz', 'menuName', 'type'))

class ViewAliases(CONST_CONTAINER):
    CRAFT_VIEW = 'NewYearCraftView'
    ALBUM_VIEW = 'AlbumMainView'
    ALBUM_PAGE21_VIEW = 'AlbumPage21View'
    ALBUM_PAGE20_VIEW = 'AlbumPage20View'
    ALBUM_PAGE19_VIEW = 'AlbumPage19View'
    ALBUM_PAGE18_VIEW = 'AlbumPage18View'
    REWARDS_VIEW = 'NewYearRewardsView'
    BREAK_VIEW = 'NewYearBreakDecorationsView'
    INFO_VIEW = 'NewYearInfoView'
    GLADE_VIEW = 'NewYearGladeView'
    CELEBRITY_VIEW = 'NewYearCelebrityView'


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
        from gui.impl.new_year.views.new_year_craft_view import NewYearCraftView
        from gui.impl.new_year.views.album.album_main_view import AlbumMainView
        from gui.impl.new_year.views.new_year_rewards_view import NewYearRewardsView
        from gui.impl.new_year.views.new_year_break_decorations_view import NewYearBreakDecorationsView
        from gui.impl.new_year.views.album.album_page20_view import AlbumPage20View
        from gui.impl.new_year.views.album.album_page19_view import AlbumPage19View
        from gui.impl.new_year.views.album.album_page18_view import AlbumPage18View
        from gui.impl.new_year.views.new_year_info_view import NewYearInfoView
        from gui.impl.new_year.views.new_year_glade_view import NewYearGladeView
        from gui.impl.lobby.new_year.new_year_challenge import NewYearChallenge
        return {ViewAliases.CRAFT_VIEW: ViewParams(NewYearCraftView, NyWidgetTopMenu.DECORATIONS, ViewTypes.UNBOUND),
         ViewAliases.ALBUM_VIEW: ViewParams(AlbumMainView, NyWidgetTopMenu.COLLECTIONS, ViewTypes.UNBOUND),
         ViewAliases.ALBUM_PAGE20_VIEW: ViewParams(AlbumPage20View, NyWidgetTopMenu.COLLECTIONS, ViewTypes.UNBOUND),
         ViewAliases.ALBUM_PAGE19_VIEW: ViewParams(AlbumPage19View, NyWidgetTopMenu.COLLECTIONS, ViewTypes.UNBOUND),
         ViewAliases.ALBUM_PAGE18_VIEW: ViewParams(AlbumPage18View, NyWidgetTopMenu.COLLECTIONS, ViewTypes.UNBOUND),
         ViewAliases.REWARDS_VIEW: ViewParams(NewYearRewardsView, NyWidgetTopMenu.REWARDS, ViewTypes.UNBOUND),
         ViewAliases.BREAK_VIEW: ViewParams(NewYearBreakDecorationsView, NyWidgetTopMenu.SHARDS, ViewTypes.UNBOUND),
         ViewAliases.INFO_VIEW: ViewParams(NewYearInfoView, NyWidgetTopMenu.INFO, ViewTypes.GAMEFACE),
         ViewAliases.GLADE_VIEW: ViewParams(NewYearGladeView, NyWidgetTopMenu.GLADE, ViewTypes.UNBOUND),
         ViewAliases.CELEBRITY_VIEW: ViewParams(NewYearChallenge, NyWidgetTopMenu.GLADE, ViewTypes.GAMEFACE)}


class NewYearTabCache(object):
    COVER_STATE = 'coverState'
    PAGE_STATE = 'pageState'
    __slots__ = ('__cache', '__currentYear', '__rewardsTab')

    def __init__(self):
        self.__cache = {}
        self.__rewardsTab = None
        self.__currentYear = Collections.NewYear21
        return

    def getState(self, yearName):
        return self.__cache[yearName] if yearName in self.__cache else (self.COVER_STATE, {})

    def saveState(self, yearName, state):
        self.__cache[yearName] = state

    def getRewardsTab(self):
        return self.__rewardsTab

    def setRewardsTab(self, tabName):
        self.__rewardsTab = tabName

    def clear(self):
        self.__cache.clear()
        self.__rewardsTab = None
        self.__currentYear = Collections.NewYear21
        return

    def saveCurrentYear(self, yearName):
        self.__currentYear = yearName

    def getCurrentYear(self):
        return self.__currentYear


class NewYearNavigation(ViewImpl):
    _navigationState = _NavigationState()
    _tabCache = NewYearTabCache()
    _nyController = dependency.descriptor(INewYearController)
    _customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    _craftCtrl = dependency.descriptor(INewYearCraftMachineController)
    _celebrityController = dependency.descriptor(ICelebritySceneController)
    _isScopeWatcher = True
    _navigationAlias = None
    onObjectStateChanged = Event.Event()
    __slots__ = ('_newYearSounds',)

    def __init__(self, *args, **kwargs):
        super(NewYearNavigation, self).__init__(*args, **kwargs)
        self._newYearSounds = None
        self._app.setBackgroundAlpha(0.0)
        return

    @classmethod
    def closeMainView(cls):
        if cls._navigationState.getCurrentObject() is not None:
            cls.__switchTo(None)
            cls._navigationState.setCurrentView(None)
        return

    @classmethod
    def showMainView(cls, objectName, viewAlias=None, *args, **kwargs):
        if viewAlias is None:
            showCelebrityView = objectName == AdditionalCameraObject.CELEBRITY
            viewAlias = ViewAliases.CELEBRITY_VIEW if showCelebrityView else ViewAliases.GLADE_VIEW
        if not cls._app.fadeManager.isInFade():
            cls.__switchUI(objectName, viewAlias, *args, **kwargs)
            cls._initObject(objectName)
        return

    @classmethod
    def switchByAnchorName(cls, anchorName, viewAlias=None):
        objectName = ANCHOR_TO_OBJECT.get(anchorName)
        cls.switchByObjectName(objectName, viewAlias)

    @classmethod
    def switchByObjectName(cls, objectName, viewAlias=None):
        cls.showMainView(objectName, viewAlias)
        cls.__playTransitionSound(objectName)

    @classmethod
    def switchToTalismans(cls):
        cls.__switchUI(AdditionalCameraObject.MASCOT)
        cls.__switchObject(AdditionalCameraObject.MASCOT)

    @classmethod
    def switchToTree(cls):
        cls.__switchUI(CustomizationObjects.FIR)
        cls.__switchObject(CustomizationObjects.FIR)

    @classmethod
    def getCurrentObject(cls):
        return cls._navigationState.getCurrentObject()

    @classmethod
    def isTalismanObject(cls):
        return cls.getCurrentObject() == AdditionalCameraObject.MASCOT

    @classmethod
    def getCurrentViewName(cls):
        return cls._navigationState.getCurrentViewName()

    @classmethod
    def clearCache(cls):
        cls._tabCache.clear()

    def _initialize(self, soundConfig=None, *args, **kwargs):
        super(NewYearNavigation, self)._initialize(*args, **kwargs)
        self._newYearSounds = NewYearSoundsManager({} if soundConfig is None else soundConfig)
        if self._isScopeWatcher:
            checkVignetteSettings('ny_navigation')
        self._newYearSounds.onEnterView()
        return

    def _finalize(self):
        if self._isScopeWatcher:
            if self._navigationState.isInternalSwitch():
                self._navigationState.setIsInternalSwitch(False)
        if self._newYearSounds is not None:
            self._newYearSounds.onExitView()
            self._newYearSounds.clear()
        super(NewYearNavigation, self)._finalize()
        return

    def _goToByViewAlias(self, viewAlias, tabName=None, *args, **kwargs):
        self._switchToView(viewAlias, tabName, *args, **kwargs)

    def _goToMainView(self, tabName=None, *args, **kwargs):
        self._switchToView(ViewAliases.GLADE_VIEW, tabName, *args, **kwargs)

    def _goToInfoView(self):
        self._switchToView(ViewAliases.INFO_VIEW)

    def _goToCraftView(self, toyTypeID=RANDOM_VALUE, settingID=RANDOM_VALUE, rank=RANDOM_VALUE, isMegaOn=False, *args, **kwargs):
        self._craftCtrl.isMegaDeviceTurnedOn = isMegaOn
        if not isMegaOn:
            toyTypeID, settingID, rank = mapToyParamsFromSrvToCraftUi(toyTypeID, settingID, rank)
            self._craftCtrl.selectedToyTypeIdx = toyTypeID
            self._craftCtrl.selectedToySettingIdx = settingID
            self._craftCtrl.selectedToyRankIdx = rank
        self._switchToView(ViewAliases.CRAFT_VIEW, *args, **kwargs)

    def _goToAlbumView(self, tabName=None, *args, **kwargs):
        self._switchToView(ViewAliases.ALBUM_VIEW, tabName, *args, **kwargs)

    def _goToRewardsView(self, tabName=None, *args, **kwargs):
        self._switchToView(ViewAliases.REWARDS_VIEW, tabName, *args, **kwargs)

    def _goToCelebrityView(self, *args, **kwargs):
        self._switchToView(ViewAliases.CELEBRITY_VIEW, *args, **kwargs)

    def _switchToView(self, aliasName, tabName=None, *args, **kwargs):
        self._navigationState.setIsInternalSwitch(True)
        self._navigationState.setCurrentView(aliasName)
        showNewYearMainView(ViewLoadingParams.get(aliasName), tabName, *args, **kwargs)

    @process
    def _switchObject(self, objectName):
        readyToSwitch = yield self._app.fadeManager.startFade()
        if readyToSwitch and self.viewStatus == ViewStatus.LOADED:
            self.__switchObject(objectName)
            self._afterObjectSwitch()
        self.__playTransitionSound(objectName)

    @process
    def _resetObject(self):
        yield self._app.fadeManager.startFade()
        self._navigationState.setCurrentView(None)
        self.__switchObject(None)
        return

    @classmethod
    @process
    def _initObject(cls, objectName):
        yield cls._app.fadeManager.startFade()
        if objectName == cls.getCurrentObject():
            cls.__switchObject(objectName)

    def _afterObjectSwitch(self):
        pass

    @sf_lobby
    def _app(self):
        return None

    @classmethod
    @process
    def __switchTo(cls, objectName):
        readyToSwitch = yield cls._app.fadeManager.startFade()
        if readyToSwitch:
            cls.__switchUI(objectName)
            cls.__switchObject(objectName)

    @classmethod
    def __switchObject(cls, objectName):
        anchorName = OBJECT_TO_ANCHOR.get(objectName)
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.CUSTOMIZATION_CAMERA_ACTIVATED))
        cls._customizableObjectsMgr.switchCamera(anchorName)
        cls._navigationState.setCurrentObject(objectName)
        cls.onObjectStateChanged()

    @classmethod
    def __switchUI(cls, objectName, viewAlias=ViewAliases.GLADE_VIEW, tabName=None, *args, **kwargs):
        cls._navigationState.setCurrentView(viewAlias)
        cls._navigationState.setCurrentObject(objectName)
        if objectName is None:
            event_dispatcher.showHangar()
        else:
            viewLoadingParams = ViewLoadingParams.get(viewAlias)
            if viewLoadingParams.menuName == NyWidgetTopMenu.GLADE and tabName is None:
                tabName = objectName
            showNewYearMainView(ViewLoadingParams.get(viewAlias), tabName, *args, **kwargs)
        return

    @classmethod
    def __playTransitionSound(cls, objectName):
        if objectName == AdditionalCameraObject.CELEBRITY and not cls._celebrityController.isChallengeVisited:
            eventName = NewYearSoundEvents.CELEBRITY_INTRO
        else:
            eventName = _SWITCH_OBJECT_SOUND_EVENTS.get(objectName)
        if eventName:
            NewYearSoundsManager.playEvent(eventName)
