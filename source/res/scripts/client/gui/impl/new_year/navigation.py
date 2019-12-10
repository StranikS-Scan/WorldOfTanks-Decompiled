# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/navigation.py
from collections import namedtuple
import Event
from adisp import process
from frameworks.wulf import ViewStatus
from gui.Scaleform.framework import ScopeTemplates
from gui.app_loader import sf_lobby
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.pub import ViewImpl
from gui.shared import event_dispatcher, g_eventBus, events
from gui.shared.event_dispatcher import showNewYearMainView
from gui.shared.ny_vignette_settings_switcher import checkVignetteSettings
from helpers import dependency
from items.components.ny_constants import CustomizationObjects, RANDOM_VALUE
from new_year.craft_machine import CraftSettingsNames, mapToyParamsFromSrvToCraftUi
from new_year.ny_constants import OBJECT_TO_ANCHOR, ANCHOR_TO_OBJECT, NyWidgetTopMenu, Collections, AdditionalCameraObject
from shared_utils import CONST_CONTAINER
from skeletons.new_year import ICustomizableObjectsManager, INewYearController, ICraftMachineSettingsStorage
from soft_exception import SoftException
_SWITCH_OBJECT_SOUND_EVENTS = {CustomizationObjects.FIR: NewYearSoundEvents.TRANSITION_TREE,
 CustomizationObjects.INSTALLATION: NewYearSoundEvents.TRANSITION_SNOWTANK,
 CustomizationObjects.TABLEFUL: NewYearSoundEvents.TRANSITION_KITCHEN,
 CustomizationObjects.ILLUMINATION: NewYearSoundEvents.TRANSITION_LIGHT,
 AdditionalCameraObject.MASCOT: NewYearSoundEvents.TRANSITION_TALISMAN}

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


_ViewLoadingParams = namedtuple('_ViewLoadingParams', 'className, menuName')

class ViewAliases(CONST_CONTAINER):
    MAIN_VIEW = 'MAIN_VIEW'
    CRAFT_VIEW = 'NewYearCraftView'
    ALBUM_VIEW = 'AlbumMainView'
    ALBUM_PAGE20_VIEW = 'AlbumPage20View'
    ALBUM_PAGE19_VIEW = 'AlbumPage19View'
    ALBUM_PAGE18_VIEW = 'AlbumPage18View'
    REWARDS_VIEW = 'NewYearRewardsView'
    BREAK_VIEW = 'NewYearBreakDecorationsView'
    INFO_VIEW = 'NewYearInfoView'
    GLADE_VIEW = 'NewYearGladeView'


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
        return {ViewAliases.CRAFT_VIEW: _ViewLoadingParams(NewYearCraftView, NyWidgetTopMenu.DECORATIONS),
         ViewAliases.ALBUM_VIEW: _ViewLoadingParams(AlbumMainView, NyWidgetTopMenu.COLLECTIONS),
         ViewAliases.ALBUM_PAGE20_VIEW: _ViewLoadingParams(AlbumPage20View, NyWidgetTopMenu.COLLECTIONS),
         ViewAliases.ALBUM_PAGE19_VIEW: _ViewLoadingParams(AlbumPage19View, NyWidgetTopMenu.COLLECTIONS),
         ViewAliases.ALBUM_PAGE18_VIEW: _ViewLoadingParams(AlbumPage18View, NyWidgetTopMenu.COLLECTIONS),
         ViewAliases.REWARDS_VIEW: _ViewLoadingParams(NewYearRewardsView, NyWidgetTopMenu.REWARDS),
         ViewAliases.BREAK_VIEW: _ViewLoadingParams(NewYearBreakDecorationsView, NyWidgetTopMenu.SHARDS),
         ViewAliases.INFO_VIEW: _ViewLoadingParams(NewYearInfoView, NyWidgetTopMenu.INFO),
         ViewAliases.GLADE_VIEW: _ViewLoadingParams(NewYearGladeView, NyWidgetTopMenu.GLADE)}


class NewYearTabCache(object):
    COVER_STATE = 'coverState'
    PAGE_STATE = 'pageState'
    __slots__ = ('__cache', '__currentYear', '__rewardsTab')

    def __init__(self):
        self.__cache = {}
        self.__rewardsTab = None
        self.__currentYear = Collections.NewYear20
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
        self.__currentYear = Collections.NewYear20
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
    _craftSettings = dependency.descriptor(ICraftMachineSettingsStorage)
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
    def showMainView(cls, objectName, viewAlias=ViewAliases.GLADE_VIEW, *args, **kwargs):
        if not cls._app.fadeManager.isInFade():
            cls.__switchUI(objectName, viewAlias, *args, **kwargs)
            cls._initObject(objectName)

    @classmethod
    def switchByAnchorName(cls, anchorName):
        objectName = ANCHOR_TO_OBJECT.get(anchorName)
        cls.showMainView(objectName)
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
    def getCurrentViewName(cls):
        return cls._navigationState.getCurrentViewName()

    def _initialize(self, soundConfig=None, *args, **kwargs):
        super(NewYearNavigation, self)._initialize(*args, **kwargs)
        self._newYearSounds = NewYearSoundsManager({} if soundConfig is None else soundConfig)
        if self._isScopeWatcher:
            checkVignetteSettings('ny_navigation')
        self._newYearSounds.onEnterView()
        return

    def _finalize(self):
        self._newYearSounds.onExitView()
        if self._isScopeWatcher:
            if self._navigationState.isInternalSwitch():
                self._navigationState.setIsInternalSwitch(False)
        self._newYearSounds.clear()
        super(NewYearNavigation, self)._finalize()

    def _goToByViewAlias(self, viewAlias, *args, **kwargs):
        self._switchToView(viewAlias, *args, **kwargs)

    def _goToMainView(self):
        self._switchToView(ViewAliases.GLADE_VIEW)

    def _goToInfoView(self):
        self._switchToView(ViewAliases.INFO_VIEW)

    def _goToCraftView(self, toyTypeID=RANDOM_VALUE, settingID=RANDOM_VALUE, rank=RANDOM_VALUE, isMegaOn=False, *args, **kwargs):
        self._craftSettings.setValue(CraftSettingsNames.MEGA_DEVICE_TURNED_ON, isMegaOn)
        if not isMegaOn:
            toyTypeID, settingID, rank = mapToyParamsFromSrvToCraftUi(toyTypeID, settingID, rank)
            self._craftSettings.setValue(CraftSettingsNames.TOY_TYPE_ID, toyTypeID)
            self._craftSettings.setValue(CraftSettingsNames.TOY_SETTING_ID, settingID)
            self._craftSettings.setValue(CraftSettingsNames.TOY_RANK_ID, rank)
        self._switchToView(ViewAliases.CRAFT_VIEW, *args, **kwargs)

    def _goToAlbumView(self, *args, **kwargs):
        self._switchToView(ViewAliases.ALBUM_VIEW, *args, **kwargs)

    def _goToRewardsView(self, *args, **kwargs):
        self._switchToView(ViewAliases.REWARDS_VIEW, *args, **kwargs)

    def _switchToView(self, aliasName, *args, **kwargs):
        self._navigationState.setIsInternalSwitch(True)
        self._navigationState.setCurrentView(aliasName)
        loadingParams = ViewLoadingParams.get(aliasName)
        showNewYearMainView(loadingParams, *args, **kwargs)

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
    def __switchUI(cls, objectName, viewAlias=ViewAliases.GLADE_VIEW, *args, **kwargs):
        cls._navigationState.setCurrentView(viewAlias)
        cls._navigationState.setCurrentObject(objectName)
        if objectName is None:
            event_dispatcher.showHangar()
        else:
            showNewYearMainView(ViewLoadingParams.get(viewAlias), *args, **kwargs)
        return

    @staticmethod
    def __playTransitionSound(objectName):
        eventName = _SWITCH_OBJECT_SOUND_EVENTS.get(objectName)
        if eventName:
            NewYearSoundsManager.playEvent(eventName)


def _loadView(layoutID, viewClass, *args, **kwargs):
    g_eventBus.handleEvent(events.LoadUnboundViewEvent(layoutID, viewClass, ScopeTemplates.LOBBY_SUB_SCOPE, *args, **kwargs))
