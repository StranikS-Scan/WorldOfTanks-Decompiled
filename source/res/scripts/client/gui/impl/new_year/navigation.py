# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/navigation.py
import logging
import Event
from adisp import process
from gui.Scaleform.managers.fade_manager import FadeState
from gui.app_loader import sf_lobby
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showNewYearMainView
from helpers import dependency
from items.components.ny_constants import CustomizationObjects
from new_year.ny_constants import OBJECT_TO_ANCHOR, ANCHOR_TO_OBJECT, NyWidgetTopMenu, Collections, AdditionalCameraObject, AnchorNames
from shared_utils import CONST_CONTAINER
from skeletons.new_year import ICustomizableObjectsManager, INewYearController, ICelebritySceneController
_logger = logging.getLogger(__name__)
_SWITCH_OBJECT_SOUND_EVENTS = {CustomizationObjects.FIR: NewYearSoundEvents.TRANSITION_TREE,
 CustomizationObjects.INSTALLATION: NewYearSoundEvents.TRANSITION_INSTALLATION,
 CustomizationObjects.FAIR: NewYearSoundEvents.TRANSITION_FAIR,
 CustomizationObjects.MEGAZONE: NewYearSoundEvents.TRANSITION_MEGAZONE,
 AdditionalCameraObject.CELEBRITY: NewYearSoundEvents.TRANSITION_CELEBRITY}

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


class ViewAliases(CONST_CONTAINER):
    CRAFT_VIEW = 'NyCraftView'
    ALBUM_VIEW = 'NyAlbumView'
    REWARDS_VIEW = 'NyRewardsInfoView'
    BREAK_VIEW = 'NyBreakDecorationsView'
    INFO_VIEW = 'NyInfoView'
    GLADE_VIEW = 'NyGladeView'
    CELEBRITY_VIEW = 'NewYearCelebrityView'
    GIFT_SYSTEM_VIEW = 'NyGiftSystemView'
    VEHICLES_VIEW = 'NewYearVehiclesView'


VIEW_ALIAS_TO_MENU_NAME = {ViewAliases.GLADE_VIEW: NyWidgetTopMenu.GLADE,
 ViewAliases.CELEBRITY_VIEW: NyWidgetTopMenu.CHALLENGE,
 ViewAliases.GIFT_SYSTEM_VIEW: NyWidgetTopMenu.GIFT_SYSTEM,
 ViewAliases.VEHICLES_VIEW: NyWidgetTopMenu.VEHICLES,
 ViewAliases.BREAK_VIEW: NyWidgetTopMenu.SHARDS,
 ViewAliases.CRAFT_VIEW: NyWidgetTopMenu.DECORATIONS,
 ViewAliases.ALBUM_VIEW: NyWidgetTopMenu.COLLECTIONS,
 ViewAliases.REWARDS_VIEW: NyWidgetTopMenu.REWARDS,
 ViewAliases.INFO_VIEW: NyWidgetTopMenu.INFO}
OBJECTS_BY_VIEW = {ViewAliases.GLADE_VIEW: CustomizationObjects.ALL,
 ViewAliases.CELEBRITY_VIEW: (AdditionalCameraObject.CELEBRITY,)}

class NewYearTabCache(object):
    COVER_STATE = 'coverState'
    PAGE_STATE = 'pageState'
    OPENED_INTRO_STATE = 'openedIntroState'
    VIEWED_INTRO_STATE = 'viewedIntroState'
    __slots__ = ('__cache', '__currentYear', '__rewardsTab', '__introScreenStates')

    def __init__(self):
        self.__cache = {}
        self.__rewardsTab = None
        self.__currentYear = Collections.NewYear22
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
        self.__currentYear = Collections.NewYear22
        self.__introScreenStates.clear()
        return

    def saveCurrentYear(self, yearName):
        self.__currentYear = yearName

    def getCurrentYear(self):
        return self.__currentYear


class NewYearNavigation(object):
    _navigationState = _NavigationState()
    _nyController = dependency.descriptor(INewYearController)
    _customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    _celebrityController = dependency.descriptor(ICelebritySceneController)
    onObjectStateChanged = Event.Event()
    onUpdateCurrentView = Event.Event()

    @classmethod
    def closeMainView(cls, instantly=True, withFade=True):
        if cls._navigationState.getCurrentObject() is not None:
            cls.switchTo(None, instantly, isCloseEvent=True, withFade=withFade)
        return

    @classmethod
    def showMainView(cls, objectName, instantly=False, viewAlias=None, *args, **kwargs):
        cls.switchTo(objectName, instantly, viewAlias, *args, **kwargs)

    @classmethod
    def showGiftSystemView(cls, *args, **kwargs):
        objectName = cls.getCurrentObject() or CustomizationObjects.FIR
        kwargs.update({'clearHistoryNavigation': cls.getCurrentViewName() is not None})
        cls.switchTo(objectName, True, ViewAliases.GIFT_SYSTEM_VIEW, withFade=True, *args, **kwargs)
        return

    @classmethod
    def showVehiclesView(cls, *args, **kwargs):
        objectName = cls.getCurrentObject() or CustomizationObjects.FIR
        kwargs.update({'clearHistoryNavigation': cls.getCurrentViewName() is not None})
        cls.switchTo(objectName, True, ViewAliases.VEHICLES_VIEW, withFade=True, *args, **kwargs)
        return

    @classmethod
    def showInfoView(cls, previousViewAlias=None, *args, **kwargs):
        kwargs.update({'previousViewAlias': previousViewAlias or cls.getCurrentViewName()})
        if cls.getCurrentObject() is None:
            cls.switchTo(CustomizationObjects.FIR, True, ViewAliases.INFO_VIEW, withFade=True, *args, **kwargs)
        else:
            cls.__switchUI(ViewAliases.INFO_VIEW, *args, **kwargs)
        return

    @classmethod
    def switchByAnchorName(cls, anchorName, viewAlias=None):
        objectName = ANCHOR_TO_OBJECT.get(anchorName)
        cls.showMainView(objectName, viewAlias=viewAlias)

    @classmethod
    def switchToHeroTank(cls):
        cls._navigationState.setCurrentObject(None)
        cls._customizableObjectsMgr.switchCamera(AnchorNames.HEROTANK)
        return

    @classmethod
    def switchFromHeroTank(cls):
        if cls._customizableObjectsMgr.getCurrentCameraAnchor() == AnchorNames.HEROTANK:
            cls._navigationState.setCurrentObject(None)
            cls._customizableObjectsMgr.switchCamera(None, False)
        return

    @classmethod
    def switchFromStyle(cls, objectName, viewAlias=None, tabName=None, *args, **kwargs):
        cls._navigationState.setCurrentObject(objectName)
        cls.__switchUI(viewAlias=viewAlias, tabName=tabName, *args, **kwargs)
        cls.switchTo(objectName, instantly=True, viewAlias=viewAlias, withFade=True)

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
    def switchToView(cls, aliasName, tabName=None, *args, **kwargs):
        if aliasName in OBJECTS_BY_VIEW and cls._navigationState.getCurrentObject() not in OBJECTS_BY_VIEW[aliasName]:
            prevObject = cls._navigationState.previousObject
            newObject = prevObject if prevObject in OBJECTS_BY_VIEW[aliasName] else OBJECTS_BY_VIEW[aliasName][0]
            cls.switchTo(newObject, True, viewAlias=aliasName, withFade=True, *args, **kwargs)
            return
        cls.__switchUI(viewAlias=aliasName, tabName=tabName, *args, **kwargs)

    @classmethod
    @process
    def switchTo(cls, objectName, instantly=False, viewAlias=None, withFade=False, *args, **kwargs):
        if objectName == AdditionalCameraObject.CELEBRITY:
            instantly = True
            withFade = True
        isCloseEvent = kwargs.get('isCloseEvent', False)
        if cls._navigationState.isSceneInFade:
            _logger.warning("When fade isn't done, switching to obj=%s is locked.", objectName)
            if isCloseEvent:
                cls._navigationState.saveExitEventParams(instantly, withFade)
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
                    isCloseEvent = True
                    objectName = None
                    viewAlias = None
                    cls._navigationState.setCurrentObject(None)
            prevObjectName = cls._navigationState.getCurrentObject()
            if prevObjectName != objectName:
                _logger.warning('Current selected object has been changed during fading. Current=%s, New=%s', prevObjectName, objectName)
                return
            anchorName = OBJECT_TO_ANCHOR.get(objectName)
            cls._customizableObjectsMgr.switchCamera(anchorName, instantly)
            if objectName and viewAlias is None:
                showCelebrityView = objectName == AdditionalCameraObject.CELEBRITY
                viewAlias = ViewAliases.CELEBRITY_VIEW if showCelebrityView else ViewAliases.GLADE_VIEW
            cls.__switchUI(viewAlias=viewAlias, isObjectSwitched=True, *args, **kwargs)
            cls.onObjectStateChanged()
            cls.__playTransitionSound(objectName)
            if isCloseEvent:
                event_dispatcher.showHangar()
            return

    @classmethod
    def clear(cls):
        cls._navigationState.setCurrentView(None)
        if cls._navigationState.isSceneInFade:
            cls._navigationState.setIsClearing(True)
        if cls.getCurrentObject() is not None:
            cls.switchTo(None, True)
        cls._navigationState.clear()
        return

    @sf_lobby
    def _app(self):
        return None

    @classmethod
    def __switchUI(cls, viewAlias=ViewAliases.GLADE_VIEW, tabName=None, *args, **kwargs):
        currentObject = cls._navigationState.getCurrentObject()
        if currentObject is None:
            return
        elif cls._navigationState.isCurrentView(viewAlias):
            cls.onUpdateCurrentView(*args, **kwargs)
            return
        else:
            if 'isObjectSwitched' in kwargs:
                kwargs['isObjectSwitched'] = kwargs['isObjectSwitched'] and cls.getCurrentViewName() in OBJECTS_BY_VIEW
            cls._navigationState.setCurrentView(viewAlias)
            menuName = VIEW_ALIAS_TO_MENU_NAME[viewAlias]
            if menuName == NyWidgetTopMenu.GLADE and tabName is None:
                tabName = currentObject
            showNewYearMainView(menuName, tabName, *args, **kwargs)
            return

    @classmethod
    def __playTransitionSound(cls, objectName):
        if cls.getCurrentViewName() not in (ViewAliases.GLADE_VIEW, ViewAliases.CELEBRITY_VIEW):
            return
        if objectName == AdditionalCameraObject.CELEBRITY and not cls._celebrityController.isChallengeVisited:
            eventName = NewYearSoundEvents.CELEBRITY_INTRO
        else:
            eventName = _SWITCH_OBJECT_SOUND_EVENTS.get(objectName)
        if eventName:
            NewYearSoundsManager.playEvent(eventName)
