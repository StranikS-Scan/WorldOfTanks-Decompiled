# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/navigation.py
import logging
from functools import partial
import CGF
import Event
from adisp import adisp_process
from cgf_components.hangar_camera_manager import HangarCameraManager
from gui.Scaleform.managers.fade_manager import FadeState
from gui.app_loader import sf_lobby
from gui.impl.gen import R
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from new_year.ny_constants import NyWidgetTopMenu, NYObjects, CHALLENGE_CAMERA_OBJ_TO_TAB, CHALLENGE_TAB_TO_CAMERA_OBJ, FRIEND_GLADE_TAB_TO_OBJECTS, GLADE_TAB_TO_OBJECTS, CAMERA_OBJ_TO_FRIEND_GLADE_TAB, GuestsQuestsTokens
from shared_utils import CONST_CONTAINER, first
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController, IGiftMachineController, IFriendServiceController, ICelebrityController, ICelebritySceneController
from ClientSelectableCameraObject import ClientSelectableCameraObject
_logger = logging.getLogger(__name__)
_SWITCH_OBJECT_SOUND_EVENTS = {NYObjects.TREE: NewYearSoundEvents.TRANSITION_TREE,
 NYObjects.SCULPTURE: NewYearSoundEvents.TRANSITION_INSTALLATION,
 NYObjects.FIELD_KITCHEN: NewYearSoundEvents.TRANSITION_FAIR,
 NYObjects.RESOURCES: NewYearSoundEvents.TRANSITION_RESOURCES,
 NYObjects.CHALLENGE: NewYearSoundEvents.TRANSITION_CELEBRITY,
 NYObjects.CELEBRITY_A: NewYearSoundEvents.TRANSITION_CELEBRITY,
 NYObjects.CELEBRITY_CAT: NewYearSoundEvents.TRANSITION_CELEBRITY,
 NYObjects.CELEBRITY_D: NewYearSoundEvents.TRANSITION_CELEBRITY,
 NYObjects.CELEBRITY: NewYearSoundEvents.TRANSITION_CELEBRITY}
_NEED_RESET_CURRENT_OBJECT_STATE = 'NeedReset'
_DEFAULT_CAMERAS = ('HeroTank', 'Customization', 'Tank', 'Platoon')

class _NavigationState(object):

    def __init__(self):
        self.__currentObject = None
        self.__previousbject = None
        self.__currentViewName = None
        self.__isSceneInFade = False
        self.__isCloseMainViewInProcess = False
        return

    def getCurrentObject(self):
        return self.__currentObject

    def getCurrentViewName(self):
        return self.__currentViewName

    @property
    def previousObject(self):
        return self.__previousbject

    @property
    def isCloseMainViewInProcess(self):
        return self.__isCloseMainViewInProcess

    def setCloseMainViewInProcess(self, isClose):
        self.__isCloseMainViewInProcess = isClose

    def clear(self):
        self.__previousbject = None
        self.__isSceneInFade = False
        return

    def setCurrentObject(self, objectName):
        self.__previousbject = self.__currentObject
        self.__currentObject = objectName

    def setCurrentView(self, currentView):
        self.__currentViewName = currentView

    @property
    def needResetCurrentObject(self):
        return self.__currentObject == _NEED_RESET_CURRENT_OBJECT_STATE

    def resetObject(self, aliasName, force):
        if force and self.__currentObject is None:
            self.__previousbject = None
            self.__currentObject = _NEED_RESET_CURRENT_OBJECT_STATE
            return
        elif not self.__isFriendChange(aliasName):
            return
        else:
            isToFriend = self.isFriendView(aliasName) and not self.isFriendView(self.__currentViewName)
            objectsMap = OBJECTS_BY_VIEW_FRIEND if isToFriend else OBJECTS_BY_VIEW_MAIN
            for objects in objectsMap.values():
                if self.__currentObject in objects:
                    self.__previousbject = None
                    self.__currentObject = _NEED_RESET_CURRENT_OBJECT_STATE
                    return

            return

    def isCurrentView(self, viewName):
        return self.__currentViewName == viewName

    def isCurrentObject(self, objectName):
        return self.__currentObject == objectName

    def setIsSceneInFade(self, value):
        self.__isSceneInFade = value

    @property
    def isSceneInFade(self):
        return self.__isSceneInFade

    def isFriendView(self, aliasName):
        return aliasName in FRIENDS_VIEWS

    def __isFriendChange(self, aliasName):
        return self.isFriendView(aliasName) != self.isFriendView(self.__currentViewName)


class ViewAliases(CONST_CONTAINER):
    MARKETPLACE_VIEW = 'NyMarketplaceView'
    FRIENDS_VIEW = 'NyFriendsView'
    REWARDS_VIEW = 'NyRewardsInfoView'
    GIFT_MACHINE = 'NyGiftMachineView'
    INFO_VIEW = 'NyInfoView'
    GLADE_VIEW = 'NyGladeView'
    CELEBRITY_VIEW = 'NewYearCelebrityView'
    FRIEND_GLADE_VIEW = 'NyFriendGladeView'
    FRIEND_CELEBRITY_VIEW = 'NyFriendCelebrityView'
    FRIEND_INFO_VIEW = 'NyFriendInfoView'


VIEW_ALIAS_TO_MENU_NAME = {ViewAliases.GLADE_VIEW: NyWidgetTopMenu.GLADE,
 ViewAliases.CELEBRITY_VIEW: NyWidgetTopMenu.CHALLENGE,
 ViewAliases.FRIENDS_VIEW: NyWidgetTopMenu.FRIENDS,
 ViewAliases.GIFT_MACHINE: NyWidgetTopMenu.GIFT_MACHINE,
 ViewAliases.MARKETPLACE_VIEW: NyWidgetTopMenu.MARKETPLACE,
 ViewAliases.REWARDS_VIEW: NyWidgetTopMenu.REWARDS,
 ViewAliases.INFO_VIEW: NyWidgetTopMenu.INFO,
 ViewAliases.FRIEND_INFO_VIEW: NyWidgetTopMenu.FRIEND_INFO,
 ViewAliases.FRIEND_GLADE_VIEW: NyWidgetTopMenu.FRIEND_GLADE,
 ViewAliases.FRIEND_CELEBRITY_VIEW: NyWidgetTopMenu.FRIEND_CHALLENGE}
OBJECTS_BY_VIEW_MAIN = {ViewAliases.GLADE_VIEW: NYObjects.UPGRADABLE_GROUP + (NYObjects.RESOURCES, NYObjects.TOWN),
 ViewAliases.CELEBRITY_VIEW: NYObjects.CELEBRITY_GROUP,
 ViewAliases.MARKETPLACE_VIEW: (NYObjects.MARKETPLACE,),
 ViewAliases.GIFT_MACHINE: (NYObjects.GIFT_MACHINE,)}
OBJECTS_BY_VIEW_FRIEND = {ViewAliases.FRIEND_GLADE_VIEW: NYObjects.UPGRADABLE_GROUP + (NYObjects.RESOURCES, NYObjects.TOWN),
 ViewAliases.FRIEND_CELEBRITY_VIEW: (NYObjects.CELEBRITY,)}
OBJECTS_BY_VIEW = OBJECTS_BY_VIEW_MAIN.copy()
OBJECTS_BY_VIEW.update(OBJECTS_BY_VIEW_FRIEND)
VIEWS_WITH_AUTO_ROUTING = (ViewAliases.CELEBRITY_VIEW,)
_TABS_BY_VIEW_ALIAS = {ViewAliases.CELEBRITY_VIEW: CHALLENGE_TAB_TO_CAMERA_OBJ,
 ViewAliases.FRIEND_GLADE_VIEW: FRIEND_GLADE_TAB_TO_OBJECTS,
 ViewAliases.GLADE_VIEW: GLADE_TAB_TO_OBJECTS}
FRIENDS_VIEWS = (ViewAliases.FRIEND_GLADE_VIEW, ViewAliases.FRIEND_INFO_VIEW, ViewAliases.FRIEND_CELEBRITY_VIEW)

class HangarTypes(CONST_CONTAINER):
    MAIN_HANGAR = 'mainHangar'
    FRIEND_HANGAR = 'friendHangar'


class NewYearTabCache(object):
    COVER_STATE = 'coverState'
    PAGE_STATE = 'pageState'
    OPENED_INTRO_STATE = 'openedIntroState'
    VIEWED_INTRO_STATE = 'viewedIntroState'
    __slots__ = ('__cache', '__rewardsTab', '__marketplaceTab', '__introScreenStates')

    def __init__(self):
        self.__cache = {}
        self.__rewardsTab = None
        self.__marketplaceTab = None
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

    def getMarketplaceTab(self):
        return self.__marketplaceTab

    def setMarketplaceTab(self, tabName):
        if self.__marketplaceTab != tabName:
            self.__marketplaceTab = tabName
            return True
        return False

    def setIntroScreenState(self, menuName, state):
        self.__introScreenStates.update({menuName: state})

    def getIntroScreenState(self, menuName):
        return self.__introScreenStates.get(menuName)

    def clear(self):
        self.__cache.clear()
        self.__rewardsTab = None
        self.__introScreenStates.clear()
        self.__marketplaceTab = None
        return


class NewYearNavigation(object):
    _navigationState = _NavigationState()
    __nyController = dependency.descriptor(INewYearController)
    __nyGiftMachineCtrl = dependency.descriptor(IGiftMachineController)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __friendsService = dependency.descriptor(IFriendServiceController)
    __celebrityController = dependency.descriptor(ICelebrityController)
    __celebritySceneController = dependency.descriptor(ICelebritySceneController)
    onObjectStateChanged = Event.Event()
    onUpdateCurrentView = Event.Event()
    onBreakToysFilterApplied = Event.Event()
    onPreSwitchView = Event.Event()
    onSwitchView = Event.Event()
    onSidebarSelected = Event.Event()
    selectSidebarTabOutside = Event.Event()
    updateBackButton = Event.Event()

    @classmethod
    def createBackButtonText(cls):
        viewName = cls._navigationState.getCurrentViewName()
        return R.strings.ny.backButton.dyn(viewName)() if viewName else R.invalid()

    @classmethod
    def closeMainViewInProcess(cls, isClose):
        cls._navigationState.setCloseMainViewInProcess(isClose)

    @classmethod
    def closeMainView(cls):
        g_eventBus.handleEvent(events.NyDogEvent(events.NyDogEvent.TO_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        showHangar()

    @classmethod
    def showInfoView(cls, previousViewAlias=None, *args, **kwargs):
        kwargs.update({'previousViewAlias': previousViewAlias or cls.getCurrentViewName()})
        if cls.getCurrentObject() is None:
            cls.switchTo(NYObjects.TREE, True, ViewAliases.INFO_VIEW, *args, **kwargs)
        else:
            cls.__switchUI(ViewAliases.INFO_VIEW, *args, **kwargs)
        return

    @classmethod
    def switchFromStyle(cls, viewAlias, objectName=None, tabName=None, executeAfterLoaded=None, *args, **kwargs):
        if NewYearNavigation.getNavigationState().isFriendView(viewAlias):
            _, tabName = NewYearNavigation.getMenuAndTabNames(viewAlias, None, objectName)
            NewYearNavigation.switchToFriendView(viewAlias, tabName=tabName, executeAfterLoaded=executeAfterLoaded)
        else:
            cls.__switchUI(viewAlias=viewAlias, tabName=tabName, *args, **kwargs)
            if objectName is not None:
                cls.switchTo(objectName, instantly=True, viewAlias=viewAlias, executeAfterLoaded=executeAfterLoaded, *args, **kwargs)
        return

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
    def switchToView(cls, aliasName, tabName=None, force=False, *args, **kwargs):
        cls._navigationState.resetObject(aliasName, force)
        if aliasName in OBJECTS_BY_VIEW and (cls._navigationState.needResetCurrentObject or cls._navigationState.getCurrentObject() not in OBJECTS_BY_VIEW[aliasName]):
            newObject = cls.__getNewObject(aliasName, tabName, *args, **kwargs)
            cls.switchTo(newObject, True, viewAlias=aliasName, tabName=tabName, *args, **kwargs)
            return
        if aliasName == ViewAliases.INFO_VIEW:
            cls.showInfoView()
        cls.__switchUI(viewAlias=aliasName, tabName=tabName, *args, **kwargs)

    @classmethod
    @adisp_process
    def switchToFriendView(cls, aliasName, tabName=None, *args, **kwargs):
        yield cls.__friendsService.enterFriendHangar(None)
        if cls.__friendsService.isInFriendHangar:
            NewYearSoundsManager.setHangarPlaceFriends()
            cls.switchToView(aliasName, tabName=tabName, force=True, *args, **kwargs)
        return

    @classmethod
    @adisp_process
    def switchTo(cls, objectName, instantly=False, viewAlias=None, doAutoRouting=False, *args, **kwargs):
        if cls._navigationState.isSceneInFade:
            _logger.warning("When fade isn't done, switching to obj=%s is locked.", objectName)
            return
        else:
            if doAutoRouting:
                objectName = cls.__doAutoRouting(objectName)
            if not cls.getCurrentObject():
                ClientSelectableCameraObject.deselectAll()
            cls._navigationState.setCurrentObject(objectName)
            if instantly:
                cls._navigationState.setIsSceneInFade(True)
                result = yield cls._app.fadeManager.startFade()
                cls._navigationState.setIsSceneInFade(False)
                if result == FadeState.destroying:
                    return
            prevObjectName = cls._navigationState.getCurrentObject()
            if prevObjectName != objectName:
                _logger.warning('Current selected object has been changed during fading. Current=%s, New=%s', prevObjectName, objectName)
                return
            if cls.getPreviousObject() is not None or instantly:
                cls.__switchCamera(objectName, instantly)
            else:
                kwargs['executeAfterLoaded'] = partial(cls.__switchCamera, objectName, False)
            hangarType = HangarTypes.MAIN_HANGAR if not cls.__friendsService.isInFriendHangar else HangarTypes.FRIEND_HANGAR
            if not viewAlias:
                viewAlias = cls.getViewAliasByObjectName(objectName=objectName, hangarType=hangarType)
            cls.__switchUI(viewAlias=viewAlias, isObjectSwitched=True, *args, **kwargs)
            if objectName != cls.getPreviousObject():
                cls.onObjectStateChanged()
            cls.__playTransitionSound(objectName)
            return

    @classmethod
    def getViewAliasByObjectName(cls, objectName, hangarType=HangarTypes.MAIN_HANGAR):
        views = [ viewKey for viewKey, objects in (OBJECTS_BY_VIEW_MAIN if hangarType == HangarTypes.MAIN_HANGAR else (OBJECTS_BY_VIEW_FRIEND if hangarType == HangarTypes.FRIEND_HANGAR else {})).iteritems() if objectName in objects ]
        if views:
            return first(views)
        return ViewAliases.GLADE_VIEW if hangarType == HangarTypes.MAIN_HANGAR else ViewAliases.FRIENDS_VIEW

    @classmethod
    def clear(cls):
        cls._navigationState.setCurrentView(None)
        cls._navigationState.setCurrentObject(None)
        cls._navigationState.clear()
        cls.onObjectStateChanged()
        cls.__switchCameraToTank()
        return

    @classmethod
    def getNavigationState(cls):
        return cls._navigationState

    @classmethod
    def getMenuAndTabNames(cls, viewAlias, tabName, currentObject):
        menuName = VIEW_ALIAS_TO_MENU_NAME[viewAlias]
        if tabName is None:
            if menuName == NyWidgetTopMenu.GLADE:
                tabName = currentObject
            elif menuName == NyWidgetTopMenu.CHALLENGE:
                tabName = CHALLENGE_CAMERA_OBJ_TO_TAB.get(currentObject)
            elif menuName == NyWidgetTopMenu.FRIEND_GLADE:
                tabName = CAMERA_OBJ_TO_FRIEND_GLADE_TAB.get(currentObject)
        return (menuName, tabName)

    @sf_lobby
    def _app(self):
        return None

    @classmethod
    def __getNewObject(cls, aliasName, tabName, doAutoRouting=False, *args, **kwargs):
        groupObjects = OBJECTS_BY_VIEW[aliasName]
        if tabName is not None:
            tabsToCamObj = _TABS_BY_VIEW_ALIAS.get(aliasName, {})
            camObj = tabsToCamObj.get(tabName, None)
            if camObj:
                return camObj
        firstObjectFromGroup = first(groupObjects)
        if doAutoRouting and aliasName in VIEWS_WITH_AUTO_ROUTING:
            return firstObjectFromGroup
        else:
            prevObject = cls._navigationState.previousObject
            return prevObject if prevObject in groupObjects else firstObjectFromGroup

    @classmethod
    def __switchUI(cls, viewAlias=ViewAliases.GLADE_VIEW, tabName=None, *args, **kwargs):
        from gui.shared.event_dispatcher import showNewYearMainView
        currentObject = cls._navigationState.getCurrentObject()
        if currentObject is None:
            return
        elif cls._navigationState.isCurrentView(viewAlias):
            cls.onUpdateCurrentView(viewAlias=viewAlias, currentObject=currentObject, *args, **kwargs)
            return
        else:
            if 'isObjectSwitched' in kwargs:
                kwargs['isObjectSwitched'] = kwargs['isObjectSwitched'] and cls.getCurrentViewName() in OBJECTS_BY_VIEW
            cls._navigationState.setCurrentView(viewAlias)
            menuName, tabName = cls.getMenuAndTabNames(viewAlias, tabName, currentObject)
            showNewYearMainView(menuName, tabName, *args, **kwargs)
            return

    @classmethod
    def __doAutoRouting(cls, objectName):
        if objectName == NYObjects.CHALLENGE:
            if not cls.__celebritySceneController.isChallengeCompleted:
                objectName = NYObjects.CHALLENGE
            elif not cls.__celebrityController.isGuestQuestsCompletedFully((GuestsQuestsTokens.GUEST_A,)):
                objectName = NYObjects.CELEBRITY_A
            elif cls.__nyController.isTokenReceived(GuestsQuestsTokens.TOKEN_CAT) and not cls.__celebrityController.isGuestQuestsCompletedFully((GuestsQuestsTokens.GUEST_C,)):
                objectName = NYObjects.CELEBRITY_CAT
            else:
                objectName = NYObjects.CELEBRITY
        return objectName

    @classmethod
    def __playTransitionSound(cls, objectName):
        if cls.getCurrentViewName() not in (ViewAliases.GLADE_VIEW, ViewAliases.CELEBRITY_VIEW):
            return
        eventName = _SWITCH_OBJECT_SOUND_EVENTS.get(objectName)
        if eventName:
            NewYearSoundsManager.playEvent(eventName)

    @classmethod
    def __switchCamera(cls, cameraName, instantly=False):
        if cls.__hangarSpace.space is None:
            return
        else:
            cameraManager = CGF.getManager(cls.__hangarSpace.spaceID, HangarCameraManager)
            if cameraManager and cameraName:
                if cameraName == cameraManager.getCurrentCameraName():
                    return
                cameraManager.switchByCameraName(cameraName, instantly)
            return

    @classmethod
    def __switchCameraToTank(cls):
        if cls.__hangarSpace.space is None:
            return
        else:
            cameraManager = CGF.getManager(cls.__hangarSpace.spaceID, HangarCameraManager)
            if not cameraManager:
                return
            if cameraManager.getCurrentCameraName() != 'HeroTank' and cls.__hangarSpace.space.getVehicleEntity():
                cls.__hangarSpace.space.getVehicleEntity().onSelect()
            if cameraManager.getCurrentCameraName() not in _DEFAULT_CAMERAS:
                cameraManager.switchToTank(instantly=not cls.__nyController.isEnabled())
            return
