# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/navigation.py
import logging
import CGF
import Event
from adisp import adisp_process
from cgf_components.hangar_camera_manager import HangarCameraManager
from gui.Scaleform.managers.fade_manager import FadeState
from gui.app_loader import sf_lobby
from gui.impl.gen import R
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from helpers import dependency
from items.components.ny_constants import CustomizationObjects
from new_year.ny_constants import OBJECT_TO_ANCHOR, ANCHOR_TO_OBJECT, NyWidgetTopMenu, AdditionalCameraObject, CHALLENGE_CAMERA_OBJ_TO_TAB, CHALLENGE_TAB_TO_CAMERA_OBJ, FRIEND_GLADE_TAB_TO_OBJECTS, CAMERA_OBJ_TO_FRIEND_GLADE_TAB, GuestsQuestsTokens
from shared_utils import CONST_CONTAINER, first
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController, IGiftMachineController, IFriendServiceController, ICelebrityController, ICelebritySceneController
from CurrentVehicle import g_currentPreviewVehicle
_logger = logging.getLogger(__name__)
_SWITCH_OBJECT_SOUND_EVENTS = {CustomizationObjects.FIR: NewYearSoundEvents.TRANSITION_TREE,
 CustomizationObjects.INSTALLATION: NewYearSoundEvents.TRANSITION_INSTALLATION,
 CustomizationObjects.FAIR: NewYearSoundEvents.TRANSITION_FAIR,
 AdditionalCameraObject.RESOURCES: NewYearSoundEvents.TRANSITION_RESOURCES,
 AdditionalCameraObject.CHALLENGE: NewYearSoundEvents.TRANSITION_CELEBRITY,
 AdditionalCameraObject.CELEBRITY_A: NewYearSoundEvents.TRANSITION_CELEBRITY,
 AdditionalCameraObject.CELEBRITY_M: NewYearSoundEvents.TRANSITION_CELEBRITY,
 AdditionalCameraObject.CELEBRITY_CAT: NewYearSoundEvents.TRANSITION_CELEBRITY,
 AdditionalCameraObject.CELEBRITY_D: NewYearSoundEvents.TRANSITION_CELEBRITY,
 AdditionalCameraObject.CELEBRITY: NewYearSoundEvents.TRANSITION_CELEBRITY}
_NEED_RESET_CURRENT_OBJECT_STATE = 'NeedReset'

class _NavigationState(object):

    def __init__(self):
        self.__currentObject = None
        self.__previousbject = None
        self.__currentViewName = None
        self.__exitParams = None
        self.__isSceneInFade = False
        self.__isClearing = False
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
        self.__exitParams = None
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
OBJECTS_BY_VIEW_MAIN = {ViewAliases.GLADE_VIEW: CustomizationObjects.ALL + (AdditionalCameraObject.RESOURCES, AdditionalCameraObject.UNDER_SPACE),
 ViewAliases.CELEBRITY_VIEW: AdditionalCameraObject.CELEBRITY_GROUP,
 ViewAliases.MARKETPLACE_VIEW: (AdditionalCameraObject.MARKETPLACE,),
 ViewAliases.GIFT_MACHINE: AdditionalCameraObject.GIFT_MACHINE_GROUP}
OBJECTS_BY_VIEW_FRIEND = {ViewAliases.FRIEND_GLADE_VIEW: CustomizationObjects.ALL + (AdditionalCameraObject.RESOURCES, AdditionalCameraObject.UNDER_SPACE),
 ViewAliases.FRIEND_CELEBRITY_VIEW: (AdditionalCameraObject.CELEBRITY,)}
OBJECTS_BY_VIEW = OBJECTS_BY_VIEW_MAIN.copy()
OBJECTS_BY_VIEW.update(OBJECTS_BY_VIEW_FRIEND)
VIEWS_WITH_AUTO_ROUTING = (ViewAliases.CELEBRITY_VIEW,)
_TABS_BY_VIEW_ALIAS = {ViewAliases.CELEBRITY_VIEW: CHALLENGE_TAB_TO_CAMERA_OBJ,
 ViewAliases.FRIEND_GLADE_VIEW: FRIEND_GLADE_TAB_TO_OBJECTS}
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
    onAnchorSelected = Event.Event()

    @classmethod
    def createBackButtonText(cls):
        viewName = cls._navigationState.getCurrentViewName()
        return R.strings.ny.backButton.dyn(viewName)() if viewName else R.invalid()

    @classmethod
    def closeMainViewInProcess(cls, isClose):
        cls._navigationState.setCloseMainViewInProcess(isClose)

    @classmethod
    def closeMainView(cls, switchCamera=False, toHangar=True):
        if cls._navigationState.getCurrentObject() is not None:
            cls._navigationState.setCurrentObject(None)
            cls.onAnchorSelected('')
            if switchCamera:
                if cls.__hangarSpace.spaceInited and cls.__hangarSpace.space.getVehicleEntity():
                    cls.__hangarSpace.space.getVehicleEntity().onSelect()
                cls.__switchCamera(None, False)
            cls.onObjectStateChanged()
            g_currentPreviewVehicle.selectNoVehicle()
            g_currentPreviewVehicle.resetAppearance()
            if toHangar:
                from gui.shared.event_dispatcher import showHangar
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
    def switchByAnchorName(cls, anchorName, viewAlias=None, **kwargs):
        objectName = ANCHOR_TO_OBJECT.get(anchorName)
        cls.showMainView(objectName, viewAlias=viewAlias, **kwargs)

    @classmethod
    def switchFromStyle(cls, viewAlias, objectName=None, tabName=None, executeAfterLoaded=None, *args, **kwargs):
        if NewYearNavigation.getNavigationState().isFriendView(viewAlias):
            _, tabName = NewYearNavigation.getMenuAndTabNames(viewAlias, None, objectName)
            NewYearNavigation.switchToFriendView(viewAlias, tabName=tabName, executeAfterLoaded=executeAfterLoaded)
        else:
            cls.__switchUI(viewAlias=viewAlias, tabName=tabName, *args, **kwargs)
            if objectName is not None:
                cls.switchTo(objectName, instantly=True, viewAlias=viewAlias, withFade=True, executeAfterLoaded=executeAfterLoaded)
        return

    @classmethod
    def getCurrentObject(cls):
        return cls._navigationState.getCurrentObject()

    @classmethod
    def getCurrentAnchor(cls):
        return OBJECT_TO_ANCHOR.get(cls._navigationState.getCurrentObject(), '')

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
            cls.switchTo(newObject, True, viewAlias=aliasName, withFade=True, tabName=tabName, *args, **kwargs)
            return
        if aliasName == ViewAliases.INFO_VIEW:
            cls.showInfoView()
        cls.__switchUI(viewAlias=aliasName, tabName=tabName, *args, **kwargs)

    @classmethod
    @adisp_process
    def switchToFriendView(cls, aliasName, tabName=None, *args, **kwargs):
        yield cls.__friendsService.enterFriendHangar(None)
        if cls.__friendsService.friendHangarSpaId:
            NewYearSoundsManager.setHangarPlaceFriends()
            cls.switchToView(aliasName, tabName=tabName, force=True, *args, **kwargs)
        return

    @classmethod
    @adisp_process
    def switchTo(cls, objectName, instantly=False, viewAlias=None, withFade=False, doAutoRouting=False, *args, **kwargs):
        if cls._navigationState.isSceneInFade:
            _logger.warning("When fade isn't done, switching to obj=%s is locked.", objectName)
            return
        else:
            if doAutoRouting:
                objectName = cls.__doAutoRouting(objectName)
            if cls._navigationState.isCurrentObject(objectName):
                if not viewAlias:
                    if cls.__friendsService.friendHangarSpaId:
                        hangarType = HangarTypes.FRIEND_HANGAR
                    else:
                        hangarType = HangarTypes.MAIN_HANGAR
                    viewAlias = cls.getViewAliasByObjectName(objectName=objectName, hangarType=hangarType)
                cls.__switchUI(viewAlias=viewAlias, isObjectSwitched=True, *args, **kwargs)
                return
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
            anchorName = OBJECT_TO_ANCHOR.get(objectName, '')
            cls.onAnchorSelected(anchorName)
            cls.__switchCamera(anchorName, instantly)
            hangarType = HangarTypes.MAIN_HANGAR if not cls.__friendsService.friendHangarSpaId else HangarTypes.FRIEND_HANGAR
            if not viewAlias:
                viewAlias = cls.getViewAliasByObjectName(objectName=objectName, hangarType=hangarType)
            cls.__switchUI(viewAlias=viewAlias, isObjectSwitched=True, *args, **kwargs)
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
        if cls._navigationState.isSceneInFade:
            cls._navigationState.setIsClearing(True)
        if cls.getCurrentObject() is not None:
            cls.switchTo(None, instantly=True)
        if cls.__hangarSpace.space:
            cameraManager = CGF.getManager(cls.__hangarSpace.spaceID, HangarCameraManager)
            if cameraManager and cameraManager.getCurrentCameraName() not in ('HeroTank',):
                cls.__hangarSpace.space.getVehicleEntity().onSelect()
        cls._navigationState.clear()
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
        if objectName == AdditionalCameraObject.CHALLENGE:
            if not cls.__celebritySceneController.isChallengeCompleted:
                objectName = AdditionalCameraObject.CHALLENGE
            elif not cls.__celebrityController.isGuestQuestsCompletedFully((GuestsQuestsTokens.GUEST_A,)):
                objectName = AdditionalCameraObject.CELEBRITY_A
            elif not cls.__celebrityController.isGuestQuestsCompletedFully((GuestsQuestsTokens.GUEST_M,)):
                objectName = AdditionalCameraObject.CELEBRITY_M
            elif cls.__nyController.isTokenReceived(GuestsQuestsTokens.TOKEN_CAT) and not cls.__celebrityController.isGuestQuestsCompletedFully((GuestsQuestsTokens.GUEST_C,)):
                objectName = AdditionalCameraObject.CELEBRITY_CAT
            else:
                objectName = AdditionalCameraObject.CELEBRITY
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
            if cameraManager:
                if cameraName:
                    cameraManager.switchByCameraName(cameraName, instantly)
                else:
                    cameraManager.switchToTank(instantly)
            return
