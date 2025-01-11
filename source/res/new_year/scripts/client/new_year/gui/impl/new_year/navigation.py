# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/new_year/navigation.py
import logging
import Event
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentPreviewVehicle
from adisp import adisp_process
from constants import DEFAULT_HANGAR_SCENE
from gui.Scaleform.managers.fade_manager import FadeState
from gui.app_loader import sf_lobby
from new_year.gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from new_year.gui.shared.event_dispatcher import showNewYearMainView, showNewYearOnboardingView
from helpers import dependency
from new_year.helpers.server_settings import getNewYearGeneralConfig
from new_year_common.items.components.ny_constants import CustomizationObjects, NewYearObjects
from new_year.ny_constants import ANCHOR_TO_OBJECT, NyWidgetTopMenu, Collections, ViewAliases, ANCHOR_TO_VIEW_ALIAS
from skeletons.gui.impl import INewYearNavigation
from skeletons.gui.game_control import IHangarSpaceSwitchController
from skeletons.gui.shared.utils import IHangarSpace
from new_year.skeletons.new_year import INewYearController
_logger = logging.getLogger(__name__)

class _NavigationState(object):

    def __init__(self):
        self.__currentObject = None
        self.__previousbject = None
        self.__currentViewName = None
        self.__exitParams = None
        self.__isSceneInFade = False
        self.__isClearing = False
        return

    def getCurrentObject(self):
        return self.__currentObject

    def getCurrentViewName(self):
        return self.__currentViewName

    @property
    def previousObject(self):
        return self.__previousbject

    def clear(self):
        self.__previousbject = None
        self.__exitParams = None
        self.__isSceneInFade = False
        return

    def setCurrentObject(self, objectName):
        self.__previousbject = self.__currentObject
        self.__currentObject = objectName

    def setCurrentView(self, currentView):
        self.__currentViewName = currentView

    def isCurrentView(self, viewName):
        return self.__currentViewName == viewName

    def setIsSceneInFade(self, value):
        self.__isSceneInFade = value

    @property
    def isSceneInFade(self):
        return self.__isSceneInFade

    def saveExitEventParams(self, instantly, withFade):
        self.__exitParams = (instantly, withFade)

    def getExitEventParams(self):
        return self.__exitParams

    def hasExitEvent(self):
        return self.__exitParams is not None

    def getIsClearing(self):
        return self.__isClearing

    def setIsClearing(self, value):
        self.__isClearing = value


VIEW_ALIAS_TO_MENU_NAME = {ViewAliases.CITY_VIEW: NyWidgetTopMenu.CITY,
 ViewAliases.QUESTS_VIEW: NyWidgetTopMenu.QUESTS,
 ViewAliases.SURPRISE_MACHINE_VIEW: NyWidgetTopMenu.SURPRISE_MACHINE,
 ViewAliases.REWARDS_VIEW: NyWidgetTopMenu.REWARDS,
 ViewAliases.PET_VIEW: NyWidgetTopMenu.PET,
 ViewAliases.INFO_VIEW: NyWidgetTopMenu.INFO}
OBJECTS_BY_VIEW = {ViewAliases.CITY_VIEW: CustomizationObjects.ALL + (NewYearObjects.CITY_VIEW,),
 ViewAliases.QUESTS_VIEW: CustomizationObjects.ALL + (NewYearObjects.CITY_VIEW,)}

class NewYearTabCache(object):
    COVER_STATE = 'coverState'
    PAGE_STATE = 'pageState'
    OPENED_INTRO_STATE = 'openedIntroState'
    VIEWED_INTRO_STATE = 'viewedIntroState'
    __slots__ = ('__cache', '__currentYear', '__rewardsTab', '__introScreenStates')

    def __init__(self):
        self.__cache = {}
        self.__rewardsTab = None
        self.__currentYear = Collections.CURRENT
        self.__introScreenStates = {}
        return

    def getState(self, yearName):
        return self.__cache[yearName] if yearName in self.__cache else (self.COVER_STATE, {})

    def saveState(self, yearName, state):
        self.__cache[yearName] = state

    def getRewardsTab(self):
        return self.__rewardsTab

    def setRewardsTab(self, tabName):
        self.__rewardsTab = tabName

    def setIntroScreenState(self, menuName, state):
        self.__introScreenStates.update({menuName: state})

    def getIntroScreenState(self, menuName):
        return self.__introScreenStates.get(menuName)

    def clear(self):
        self.__cache.clear()
        self.__rewardsTab = None
        self.__currentYear = Collections.CURRENT
        self.__introScreenStates.clear()
        return

    def saveCurrentYear(self, yearName):
        self.__currentYear = yearName

    def getCurrentYear(self):
        return self.__currentYear


class NewYearNavigation(INewYearNavigation):
    _navigationState = _NavigationState()
    _hangarSpace = dependency.descriptor(IHangarSpace)
    __nyController = dependency.descriptor(INewYearController)
    __spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)
    __needDelayedViewSwitch = False
    onObjectStateChanged = Event.Event()
    onUpdateCurrentView = Event.Event()
    onChangeView = Event.Event()

    @classmethod
    def closeMainView(cls, switchCamera=False):
        if cls._navigationState.getCurrentObject() is not None:
            from gui.shared.event_dispatcher import showHangar
            cls._navigationState.setCurrentObject(None)
            if switchCamera:
                if cls._hangarSpace.spaceInited and cls._hangarSpace.space.getVehicleEntity():
                    cls._hangarSpace.space.getVehicleEntity().onSelect()
            g_currentPreviewVehicle.selectNoVehicle()
            g_currentPreviewVehicle.resetAppearance()
            cls.onObjectStateChanged()
            cls.__nyController.switchFromNewYearPrebattle()
            showHangar()
        return

    @classmethod
    def showMainView(cls, objectName, instantly=False, viewAlias=None, *args, **kwargs):
        cls.switchTo(objectName, instantly, viewAlias, *args, **kwargs)

    @classmethod
    def showInfoView(cls, previousViewAlias=None, *args, **kwargs):
        kwargs.update({'previousViewAlias': previousViewAlias or cls.getCurrentViewName()})
        if cls.getCurrentObject() is None:
            cls.switchTo(CustomizationObjects.FIR, True, ViewAliases.INFO_VIEW, withFade=True, *args, **kwargs)
        else:
            cls.__switchUI(ViewAliases.INFO_VIEW, *args, **kwargs)
        return

    @classmethod
    def showNavigationView(cls, viewAlias=ViewAliases.CITY_VIEW):
        if cls.getCurrentObject() is None:
            cls.switchTo(NewYearObjects.CITY_VIEW, True, viewAlias=viewAlias)
        else:
            cls.__switchUI(viewAlias, instantly=True)
        return

    @classmethod
    def switchToIntro(cls):
        pass

    @classmethod
    def switchByAnchorName(cls, anchorName):
        if cls.getCurrentViewName() is None and anchorName in ANCHOR_TO_OBJECT:
            NewYearSoundsManager.playEvent(NewYearSoundEvents.TRANSITION_TREE)
            cls.switchTo(NewYearObjects.CITY_VIEW)
        elif anchorName in ANCHOR_TO_OBJECT:
            objectName = ANCHOR_TO_OBJECT[anchorName]
            cls.showMainView(objectName)
        elif anchorName in ANCHOR_TO_VIEW_ALIAS:
            viewAlias = ANCHOR_TO_VIEW_ALIAS[anchorName]
            cls.switchTo(NewYearObjects.CITY_VIEW, viewAlias=viewAlias)
        return

    @classmethod
    def switchFromStyle(cls, objectName, viewAlias=None, tabName=None, *args, **kwargs):
        cls._navigationState.setCurrentObject(objectName)
        cls.__switchUI(viewAlias=viewAlias, tabName=tabName, *args, **kwargs)
        cls.switchTo(objectName, instantly=True, viewAlias=viewAlias, withFade=True)

    @classmethod
    @adisp_process
    def switchToQuests(cls):
        if not cls.__nyController.ifNewYearBattleMode() and cls.__spaceSwitchController.currentSceneName != DEFAULT_HANGAR_SCENE:
            result = yield cls.__nyController.switchToNewYearPrebattle()
            if result:
                cls.__needDelayedViewSwitch = True
        else:
            cls.showNavigationView(ViewAliases.QUESTS_VIEW)

    @classmethod
    def onHeroTankReady(cls):
        if cls.__needDelayedViewSwitch:
            cls.__needDelayedViewSwitch = False
            cls.switchToQuests()

    @classmethod
    def getCurrentObject(cls):
        return cls._navigationState.getCurrentObject()

    @classmethod
    def getCurrentViewName(cls):
        return cls._navigationState.getCurrentViewName()

    @classmethod
    def getPreviousObject(cls):
        return cls._navigationState.previousObject

    @classmethod
    def switchToView(cls, aliasName, tabName=None, instantly=False, *args, **kwargs):
        if aliasName in OBJECTS_BY_VIEW and cls._navigationState.getCurrentObject() not in OBJECTS_BY_VIEW[aliasName]:
            prevObject = cls._navigationState.previousObject
            newObject = prevObject if prevObject in OBJECTS_BY_VIEW[aliasName] else OBJECTS_BY_VIEW[aliasName][0]
            cls.switchTo(newObject, True, viewAlias=aliasName, withFade=True, *args, **kwargs)
            return
        cls.__switchUI(viewAlias=aliasName, tabName=tabName, instantly=instantly, *args, **kwargs)

    @classmethod
    @adisp_process
    def switchTo(cls, objectName, instantly=False, viewAlias=None, withFade=False, *args, **kwargs):
        if cls._navigationState.isSceneInFade:
            _logger.warning("When fade isn't done, switching to obj=%s is locked.", objectName)
            return
        else:
            cls._navigationState.setCurrentObject(objectName)
            if withFade:
                cls._navigationState.setIsSceneInFade(True)
                result = yield cls._app.fadeManager.startFade()
                cls._navigationState.setIsSceneInFade(False)
                if result == FadeState.destroying:
                    return
                if cls._navigationState.getIsClearing():
                    cls._navigationState.setIsClearing(False)
                    objectName = None
                    viewAlias = None
                    cls._navigationState.setCurrentObject(None)
                if cls._navigationState.hasExitEvent():
                    instantly, withFade = cls._navigationState.getExitEventParams()
                    objectName = None
                    viewAlias = None
                    cls._navigationState.setCurrentObject(None)
            prevObjectName = cls._navigationState.getCurrentObject()
            if prevObjectName != objectName:
                _logger.warning('Current selected object has been changed during fading. Current=%s, New=%s', prevObjectName, objectName)
                return
            if objectName and viewAlias is None:
                viewAlias = ViewAliases.CITY_VIEW
            cls.__switchUI(viewAlias=viewAlias, instantly=instantly, *args, **kwargs)
            ClientSelectableCameraObject.deselectAll()
            cls.onObjectStateChanged()
            cls.__playTransitionSound(objectName)
            return

    @classmethod
    def clear(cls):
        cls._navigationState.setCurrentView(None)
        if cls._navigationState.isSceneInFade:
            cls._navigationState.setIsClearing(True)
        if cls.getCurrentObject() is not None:
            cls.switchTo(None, instantly=True)
        cls._navigationState.clear()
        cls.onChangeView(None)
        cls.__needDelayedViewSwitch = False
        return

    @sf_lobby
    def _app(self):
        return None

    @classmethod
    def __switchUI(cls, viewAlias=ViewAliases.CITY_VIEW, tabName=None, instantly=False, *args, **kwargs):
        currentObject = cls._navigationState.getCurrentObject()
        if currentObject is None:
            return
        else:
            if not cls.__nyController.isOnboardingFinished():
                viewAlias = ViewAliases.ONBOARDING_VIEW
            if viewAlias == ViewAliases.PET_VIEW:
                if not getNewYearGeneralConfig().getPetVisible():
                    _logger.error("Pet is hidden. View can't be shown!")
                    return
            if cls.isCurrentView(viewAlias):
                cls.onUpdateCurrentView(*args, **kwargs)
                return
            cls._navigationState.setCurrentView(viewAlias)
            cls.onChangeView(viewAlias)
            if viewAlias == ViewAliases.ONBOARDING_VIEW:
                showNewYearOnboardingView()
                return
            menuName = VIEW_ALIAS_TO_MENU_NAME[viewAlias]
            if menuName == NyWidgetTopMenu.CITY and tabName is None:
                tabName = currentObject
            showNewYearMainView(menuName, tabName, skipFlight=instantly, *args, **kwargs)
            return

    @classmethod
    def __playTransitionSound(cls, objectName):
        if cls._navigationState.previousObject == NewYearObjects.CITY_VIEW:
            NewYearSoundsManager.playEvent(NewYearSoundEvents.CITY_EXIT)
        if cls._navigationState.previousObject in CustomizationObjects.ALL:
            NewYearSoundsManager.playGladeEvent(cls._navigationState.previousObject, '_EXIT')
        if objectName == NewYearObjects.CITY_VIEW and cls._navigationState.previousObject is not None:
            NewYearSoundsManager.playEvent(NewYearSoundEvents.CITY)
        if cls.getCurrentViewName() != ViewAliases.CITY_VIEW:
            return
        else:
            if objectName in CustomizationObjects.ALL:
                if objectName == CustomizationObjects.FIR:
                    NewYearSoundsManager.playEvent(NewYearSoundEvents.TRANSITION_TREE)
                    return
                NewYearSoundsManager.playEvent(NewYearSoundEvents.ENTER_CUSTOME)
            return

    @classmethod
    def isCurrentView(cls, viewAlias):
        return cls._navigationState.isCurrentView(viewAlias)
