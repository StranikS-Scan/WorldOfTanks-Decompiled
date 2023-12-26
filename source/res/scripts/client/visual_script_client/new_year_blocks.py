# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/new_year_blocks.py
from visual_script import ASPECT
from visual_script.block import Meta, Block, EDITOR_TYPE
from visual_script.slot_types import SLOT_TYPE
from visual_script.dependency import dependencyImporter
from skeletons.account_helpers.settings_core import ISettingsCore
CGF, Physics, GenericComponents, navigation, hangar_camera_manager, dependency, newYearSkeletons, nyConstants, fade_manager, adisp, ClientUpdateManager, celebrity_quests_helpers, event_dispatcher, events, guiShared, InputHandler, gui_decorators, settings_constants, ny_gui_constants, ny_client_constants = dependencyImporter('CGF', 'Physics', 'GenericComponents', 'gui.impl.new_year.navigation', 'cgf_components.hangar_camera_manager', 'helpers.dependency', 'skeletons.new_year', 'items.components.ny_constants', 'gui.Scaleform.managers.fade_manager', 'adisp', 'gui.ClientUpdateManager', 'new_year.celebrity.celebrity_quests_helpers', 'gui.shared.event_dispatcher', 'gui.shared.events', 'gui.shared', 'gui.InputHandler', 'gui.app_loader.decorators', 'account_helpers.settings_core.settings_constants', 'gui.impl.gen.view_models.views.lobby.new_year.ny_constants', 'new_year.ny_constants')

class NewYearMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.HANGAR]


class NavigateTo(Block, NewYearMeta):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __nyController = dependency.descriptor(newYearSkeletons.INewYearController)
    __friendsService = dependency.descriptor(newYearSkeletons.IFriendServiceController)

    def __init__(self, *args, **kwargs):
        super(NavigateTo, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._customizationName = self._makeDataInputSlot('customizationName', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        name = self._customizationName.getValue()
        countOfSacks = self.__nyController.sacksHelper.getSacksCount()
        isSelfHangar = self.__friendsService.friendHangarSpaId is None
        if self.__settingsCore.serverSettings.getNewYearStorage().get(settings_constants.NewYearStorageKeys.TUTORIAL_STATE) < ny_gui_constants.TutorialStates.UI:
            if not navigation.NewYearNavigation.getCurrentObject():
                navigation.NewYearNavigation.switchTo(ny_client_constants.NYObjects.TOWN, True)
        elif name == ny_client_constants.NYObjects.CHALLENGE and countOfSacks > 0 and isSelfHangar:
            navigation.NewYearNavigation.switchTo(ny_client_constants.NYObjects.CELEBRITY_D, False, doAutoRouting=True)
        else:
            navigation.NewYearNavigation.switchTo(name, False, doAutoRouting=True)
        self._out.call()
        return


class OpenAdventCalendar(Block, NewYearMeta):

    def __init__(self, *args, **kwargs):
        super(OpenAdventCalendar, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self, *_):
        event_dispatcher.showAdventCalendarMainWindow()


class SwitchCamera(Block, NewYearMeta):

    def __init__(self, *args, **kwargs):
        super(SwitchCamera, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._cameraName = self._makeDataInputSlot('cameraName', SLOT_TYPE.STR)
        self._spaceId = self._makeDataInputSlot('spaceId', SLOT_TYPE.INT)
        self._instantly = self._makeDataInputSlot('instantly', SLOT_TYPE.BOOL)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        cameraName = self._cameraName.getValue()
        spaceId = self._spaceId.getValue()
        cameraManager = CGF.getManager(spaceId, hangar_camera_manager.HangarCameraManager)
        if cameraManager:
            cameraManager.switchByCameraName(cameraName, self._instantly.getValue())
        self._out.call()


class OnCameraSwitched(Block, NewYearMeta):

    def __init__(self, *args, **kwargs):
        super(OnCameraSwitched, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._initialize)
        self._spaceID = self._makeDataInputSlot('spaceID', SLOT_TYPE.INT)
        self._out = self._makeEventOutputSlot('out')
        self._cameraName = self._makeDataOutputSlot('cameraName', SLOT_TYPE.STR, None)
        return

    def _initialize(self):
        cameraManager = CGF.getManager(self._spaceID.getValue(), hangar_camera_manager.HangarCameraManager)
        if cameraManager:
            cameraManager.onCameraSwitched += self._onCameraSwitched

    def _onCameraSwitched(self, cameraName):
        self._cameraName.setValue(cameraName)
        self._out.call()


class GetCameraName(Block, NewYearMeta):

    def __init__(self, *args, **kwargs):
        super(GetCameraName, self).__init__(*args, **kwargs)
        self._spaceId = self._makeDataInputSlot('spaceId', SLOT_TYPE.INT)
        self._cameraName = self._makeDataOutputSlot('cameraName', SLOT_TYPE.STR, self._execute)

    def _execute(self):
        spaceId = self._spaceId.getValue()
        cameraManager = CGF.getManager(spaceId, hangar_camera_manager.HangarCameraManager)
        if cameraManager:
            self._cameraName.setValue(cameraManager.getCurrentCameraName())


class OnNavigation(Block, NewYearMeta):

    def __init__(self, *args, **kwargs):
        super(OnNavigation, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')
        self._customizationName = self._makeDataOutputSlot('customizationName', SLOT_TYPE.STR, None)
        return

    def onStartScript(self):
        navigation.NewYearNavigation.onObjectStateChanged.append(self._onObjectStateChanged)

    def onFinishScript(self):
        navigation.NewYearNavigation.onObjectStateChanged.remove(self._onObjectStateChanged)

    def _onObjectStateChanged(self):
        objectName = navigation.NewYearNavigation.getCurrentObject()
        self._customizationName.setValue(objectName if objectName is not None else '')
        self._out.call()
        return


class OnFriendHangarSwitched(Block, NewYearMeta):
    __friendsService = dependency.descriptor(newYearSkeletons.IFriendServiceController)

    def __init__(self, *args, **kwargs):
        super(OnFriendHangarSwitched, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')

    def onStartScript(self):
        self.__friendsService.onFriendHangarEnter += self._execute
        self.__friendsService.onFriendHangarExit += self._execute

    def onFinishScript(self):
        self.__friendsService.onFriendHangarEnter -= self._execute
        self.__friendsService.onFriendHangarExit -= self._execute

    def _execute(self, *_):
        self._out.call()


class OnGuestTokenReceived(Block, NewYearMeta):
    __nyController = dependency.descriptor(newYearSkeletons.INewYearController)
    __celebrityController = dependency.descriptor(newYearSkeletons.ICelebrityController)
    __friendsService = dependency.descriptor(newYearSkeletons.IFriendServiceController)

    def __init__(self, *args, **kwargs):
        super(OnGuestTokenReceived, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._initialize)
        self._out = self._makeEventOutputSlot('out')
        self._guestName = self._makeDataOutputSlot('guestName', SLOT_TYPE.STR, None)
        self._actionType = self._makeDataOutputSlot('actionType', SLOT_TYPE.STR, None)
        self._actionLevel = self._makeDataOutputSlot('actionLevel', SLOT_TYPE.INT, None)
        self._isReceived = self._makeDataOutputSlot('isReceived', SLOT_TYPE.BOOL, None)
        self._justBought = self._makeDataOutputSlot('justBought', SLOT_TYPE.BOOL, None)
        self._initialized = False
        return

    def onStartScript(self):
        self.__friendsService.onFriendHangarEnter += self._initialize
        self.__friendsService.onFriendHangarExit += self._initialize
        self.__celebrityController.onCelebActionTokenUpdated += self._handleTokenUpdate

    def onFinishScript(self):
        self.__friendsService.onFriendHangarEnter -= self._initialize
        self.__friendsService.onFriendHangarExit -= self._initialize
        self.__celebrityController.onCelebActionTokenUpdated -= self._handleTokenUpdate

    def _initialize(self, *_):
        self._initialized = False
        tokens = self.__celebrityController.getAllTokens()
        for token in tokens:
            self._exec(token)

        self._initialized = True

    def _handleTokenUpdate(self, token):
        self.__nyController.setHangToyEffectEnabled(True)
        self._exec(token)

    def _exec(self, token):
        guestName, actionType, level = ny_client_constants.parseCelebrityTokenActionType(token)
        self._guestName.setValue(guestName)
        self._actionType.setValue(actionType)
        self._actionLevel.setValue(level)
        self._isReceived.setValue(self.__nyController.isTokenReceived(token))
        self._justBought.setValue(self._initialized)
        self._out.call()


class OnResourcesUpdate(Block, NewYearMeta):
    __nyController = dependency.descriptor(newYearSkeletons.INewYearController)

    def __init__(self, *args, **kwargs):
        super(OnResourcesUpdate, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._initialize)
        self._out = self._makeEventOutputSlot('out')
        self._state = self._makeDataOutputSlot('state', SLOT_TYPE.STR, None)
        return

    def onStartScript(self):
        self.__nyController.resourceCollecting.onResources3DStateUpdate += self._handleUpdate

    def onFinishScript(self):
        self.__nyController.resourceCollecting.onResources3DStateUpdate -= self._handleUpdate

    def _initialize(self, *_):
        self._state.setValue(self.__nyController.resourceCollecting.getInitial3DState())
        self._out.call()

    def _handleUpdate(self, state):
        self._state.setValue(state)
        self._out.call()


class ShowCelebrityStory(Block, NewYearMeta):

    def __init__(self, *args, **kwargs):
        super(ShowCelebrityStory, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._level = self._makeDataInputSlot('storyLevel', SLOT_TYPE.INT)
        self._justReceived = self._makeDataInputSlot('justReceived', SLOT_TYPE.BOOL)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        event_dispatcher.showCelebrityStories(self._level.getValue(), self._justReceived.getValue())
        self._out.call()


class OnCelebQuestReroll(Block, NewYearMeta):
    __celebrityController = dependency.descriptor(newYearSkeletons.ICelebrityController)

    def __init__(self, *args, **kwargs):
        super(OnCelebQuestReroll, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')

    def onStartScript(self):
        self.__celebrityController.onCelebRerollTokenRecieved.append(self._execute)

    def onFinishScript(self):
        self.__celebrityController.onCelebRerollTokenRecieved.remove(self._execute)

    def _execute(self):
        self._out.call()


class IsGuestQuestsCompletedFully(Block, NewYearMeta):
    __celebrityController = dependency.descriptor(newYearSkeletons.ICelebrityController)

    def __init__(self, *args, **kwargs):
        super(IsGuestQuestsCompletedFully, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._guestName = self._makeDataInputSlot('guestName', SLOT_TYPE.STR)
        self._questsCompleted = self._makeDataOutputSlot('completed', SLOT_TYPE.BOOL, None)
        self._out = self._makeEventOutputSlot('out')
        return

    def _execute(self):
        guestName = self._guestName.getValue()
        if guestName in ny_client_constants.GuestsQuestsTokens.GUESTS_ALL:
            completed = self.__celebrityController.isGuestQuestsCompletedFully([guestName])
            self._questsCompleted.setValue(completed)
            self._out.call()


class IsChallengeMainQuestsCompleted(Block, NewYearMeta):
    __celebritySceneController = dependency.descriptor(newYearSkeletons.ICelebritySceneController)

    def __init__(self, *args, **kwargs):
        super(IsChallengeMainQuestsCompleted, self).__init__(*args, **kwargs)
        self._questsCompleted = self._makeDataOutputSlot('completed', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        self._questsCompleted.setValue(self.__celebritySceneController.isAllMainQuestsCompleted)


class IsChallengeUpdated(Block, NewYearMeta):
    __celebritySceneController = dependency.descriptor(newYearSkeletons.ICelebritySceneController)

    def __init__(self, *args, **kwargs):
        super(IsChallengeUpdated, self).__init__(*args, **kwargs)
        self._updated = self._makeDataOutputSlot('updated', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        self._updated.setValue(self.__celebritySceneController.hasNewCompletedQuests)


class OnChallengeUpdated(Block, NewYearMeta):
    __celebritySceneController = dependency.descriptor(newYearSkeletons.ICelebritySceneController)

    def __init__(self, *args, **kwargs):
        super(OnChallengeUpdated, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')

    def onStartScript(self):
        self.__celebritySceneController.onQuestsUpdated += self._onQuestsUpdated

    def onFinishScript(self):
        self.__celebritySceneController.onQuestsUpdated -= self._onQuestsUpdated

    def _onQuestsUpdated(self, *args):
        if self.__celebritySceneController.hasNewCompletedQuests:
            self._out.call()


class OnGuestDoAction(Block, NewYearMeta):
    __celebrityController = dependency.descriptor(newYearSkeletons.ICelebrityController)

    def __init__(self, *args, **kwargs):
        super(OnGuestDoAction, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')
        self._guestName = self._makeDataOutputSlot('guestName', SLOT_TYPE.STR, None)
        self._actionType = self._makeDataOutputSlot('actionType', SLOT_TYPE.STR, None)
        self._actionLevel = self._makeDataOutputSlot('actionLevel', SLOT_TYPE.INT, None)
        return

    def onStartScript(self):
        self.__celebrityController.onDoActionByCelebActionToken += self._exec

    def onFinishScript(self):
        self.__celebrityController.onDoActionByCelebActionToken -= self._exec

    def _exec(self, guestName, actionType, level):
        self._guestName.setValue(guestName)
        self._actionType.setValue(actionType)
        self._actionLevel.setValue(level)
        self._out.call()


class ShowPreviewUI(Block, NewYearMeta):

    def __init__(self, *args, **kwargs):
        super(ShowPreviewUI, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._justReceived = self._makeDataInputSlot('justReceived', SLOT_TYPE.BOOL)
        self._previewType = self._makeDataInputSlot('previewType', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        event_dispatcher.showCelebrityAnimationWindow(self._justReceived.getValue(), self._previewType.getValue())
        self._out.call()


class HidePreviewUI(Block, NewYearMeta):

    def __init__(self, *args, **kwargs):
        super(HidePreviewUI, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        guiShared.g_eventBus.handleEvent(guiShared.events.NyCelebrityAnimationEvent(eventType=guiShared.events.NyCelebrityAnimationEvent.CLOSE_ANIMATION_VIEW), scope=guiShared.EVENT_BUS_SCOPE.DEFAULT)
        self._out.call()


class OnExitPreview(Block, NewYearMeta):

    def __init__(self, *args, **kwargs):
        super(OnExitPreview, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')
        self._previewType = self._makeDataOutputSlot('previewType', SLOT_TYPE.STR, None)
        return

    def onStartScript(self):
        guiShared.g_eventBus.addListener(guiShared.events.NyCelebrityAnimationEvent.ANIMATION_VIEW_CLOSED, self._execute, scope=guiShared.EVENT_BUS_SCOPE.DEFAULT)

    def onFinishScript(self):
        guiShared.g_eventBus.removeListener(guiShared.events.NyCelebrityAnimationEvent.ANIMATION_VIEW_CLOSED, self._execute, scope=guiShared.EVENT_BUS_SCOPE.DEFAULT)

    def _execute(self, event):
        self._previewType.setValue(event.ctx['previewType'])
        self._out.call()


class OnCloseCelebrityStories(Block, NewYearMeta):

    def __init__(self, *args, **kwargs):
        super(OnCloseCelebrityStories, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')

    def onStartScript(self):
        guiShared.g_eventBus.addListener(guiShared.events.NyCelebrityStoriesEvent.STORIES_VIEW_CLOSED, self._execute, scope=guiShared.EVENT_BUS_SCOPE.DEFAULT)

    def onFinishScript(self):
        guiShared.g_eventBus.removeListener(guiShared.events.NyCelebrityStoriesEvent.STORIES_VIEW_CLOSED, self._execute, scope=guiShared.EVENT_BUS_SCOPE.DEFAULT)

    def _execute(self, _):
        self._out.call()


class Fade(Block, NewYearMeta):

    def __init__(self, *args, **kwargs):
        super(Fade, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')

    @gui_decorators.sf_lobby
    def _app(self):
        return None

    @adisp.adisp_process
    def _execute(self):
        yield self._app.fadeManager.startFade()
        self._out.call()


class GetCurrentObject(Block, NewYearMeta):

    def __init__(self, *args, **kwargs):
        super(GetCurrentObject, self).__init__(*args, **kwargs)
        self._objectName = self._makeDataOutputSlot('objectName', SLOT_TYPE.STR, self._execute)

    def _execute(self):
        objectName = navigation.NewYearNavigation.getCurrentObject()
        self._objectName.setValue(objectName if objectName is not None else '')
        return


class OnDogTokenReceived(Block, NewYearMeta):
    __nyController = dependency.descriptor(newYearSkeletons.INewYearController)
    __friendsService = dependency.descriptor(newYearSkeletons.IFriendServiceController)

    def __init__(self, *args, **kwargs):
        super(OnDogTokenReceived, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._out = self._makeEventOutputSlot('out')
        self._isReceived = self._makeDataOutputSlot('isReceived', SLOT_TYPE.BOOL, None)
        return

    def onStartScript(self):
        ClientUpdateManager.g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__friendsService.onFriendHangarEnter += self._exec
        self.__friendsService.onFriendHangarExit += self._exec

    def onFinishScript(self):
        ClientUpdateManager.g_clientUpdateManager.removeObjectCallbacks(self)
        self.__friendsService.onFriendHangarEnter -= self._exec
        self.__friendsService.onFriendHangarExit -= self._exec

    def _exec(self, *_):
        isReceived = self.__nyController.isDogTokenReceived()
        self._isReceived.setValue(isReceived)
        self._out.call()

    def __onTokensUpdate(self, tokens):
        if ny_client_constants.GuestsQuestsTokens.TOKEN_DOG in tokens and not self.__friendsService.isInFriendHangar:
            self._exec()


class OnCatTokenReceived(Block, NewYearMeta):
    __nyController = dependency.descriptor(newYearSkeletons.INewYearController)
    __friendsService = dependency.descriptor(newYearSkeletons.IFriendServiceController)

    def __init__(self, *args, **kwargs):
        super(OnCatTokenReceived, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._out = self._makeEventOutputSlot('out')
        self._isReceived = self._makeDataOutputSlot('isReceived', SLOT_TYPE.BOOL, None)
        return

    def onStartScript(self):
        ClientUpdateManager.g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__friendsService.onFriendHangarEnter += self._exec
        self.__friendsService.onFriendHangarExit += self._exec

    def onFinishScript(self):
        ClientUpdateManager.g_clientUpdateManager.removeObjectCallbacks(self)
        self.__friendsService.onFriendHangarEnter -= self._exec
        self.__friendsService.onFriendHangarExit -= self._exec

    def _exec(self, *_):
        isReceived = self.__nyController.isCatTokenReceived()
        self._isReceived.setValue(isReceived)
        self._out.call()

    def __onTokensUpdate(self, tokens):
        if ny_client_constants.GuestsQuestsTokens.TOKEN_CAT in tokens and not self.__friendsService.isInFriendHangar:
            self._exec()


class OnMegaTokenReceived(Block, NewYearMeta):
    __nyController = dependency.descriptor(newYearSkeletons.INewYearController)
    __friendsService = dependency.descriptor(newYearSkeletons.IFriendServiceController)

    def __init__(self, *args, **kwargs):
        super(OnMegaTokenReceived, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._init)
        self._out = self._makeEventOutputSlot('out')
        self._name = self._makeDataOutputSlot('name', SLOT_TYPE.STR, None)
        self._isReceived = self._makeDataOutputSlot('isReceived', SLOT_TYPE.BOOL, None)
        self._isInitialize = self._makeDataOutputSlot('isInitialize', SLOT_TYPE.BOOL, None)
        return

    def onStartScript(self):
        ClientUpdateManager.g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__friendsService.onFriendHangarEnter += self._init
        self.__friendsService.onFriendHangarExit += self._init

    def onFinishScript(self):
        ClientUpdateManager.g_clientUpdateManager.removeObjectCallbacks(self)
        self.__friendsService.onFriendHangarEnter -= self._init
        self.__friendsService.onFriendHangarExit -= self._init

    def _init(self, *_):
        self._isInitialize.setValue(True)
        for decoration in nyConstants.NYFriendServiceDataTokens.HANGAR_DECORATIONS:
            self.__execForToken(decoration)

        self._isInitialize.setValue(False)

    def __onTokensUpdate(self, tokens):
        for megaToken in nyConstants.NYFriendServiceDataTokens.HANGAR_DECORATIONS:
            if megaToken in tokens and not self.__friendsService.isInFriendHangar:
                self.__nyController.setHangToyEffectEnabled(True)
                self.__execForToken(megaToken)

    def __execForToken(self, token):
        isReceived = self.__nyController.isTokenReceived(token)
        self._isReceived.setValue(isReceived)
        self._name.setValue(token.split(':')[-1])
        self._out.call()


class GiftMachineButtonPress(Block, NewYearMeta):
    __nyGiftMachineCtrl = dependency.descriptor(newYearSkeletons.IGiftMachineController)

    def __init__(self, *args, **kwargs):
        super(GiftMachineButtonPress, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        self.__nyGiftMachineCtrl.onRedButtonPress()
        self._out.call()


class OnGiftMachineRedButtonPressStateChange(Block, NewYearMeta):
    __nyGiftMachineCtrl = dependency.descriptor(newYearSkeletons.IGiftMachineController)

    def __init__(self, *args, **kwargs):
        super(OnGiftMachineRedButtonPressStateChange, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._out = self._makeEventOutputSlot('out')
        self._canRedButtonPress = self._makeDataOutputSlot('canRedButtonPress', SLOT_TYPE.BOOL, None)
        return

    def onStartScript(self):
        self.__nyGiftMachineCtrl.onRedButtonStateChanged += self.__onRedButtonStateChanged

    def onFinishScript(self):
        self.__nyGiftMachineCtrl.onRedButtonStateChanged -= self.__onRedButtonStateChanged

    def _exec(self):
        self._canRedButtonPress.setValue(self.__nyGiftMachineCtrl.canRedButtonPress)
        self._out.call()

    def __onRedButtonStateChanged(self):
        self._exec()


class NyCoinsCount(Block, NewYearMeta):
    __nyController = dependency.descriptor(newYearSkeletons.INewYearController)

    def __init__(self, *args, **kwargs):
        super(NyCoinsCount, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._out = self._makeEventOutputSlot('out')
        self._coinsCount = self._makeDataOutputSlot('coinsCount', SLOT_TYPE.INT, None)
        return

    def _exec(self):
        self._coinsCount.setValue(self.__nyController.currencies.getCoinsCount())
        self._out.call()


class OnNyCoinsCountChange(Block, NewYearMeta):
    __nyController = dependency.descriptor(newYearSkeletons.INewYearController)

    def __init__(self, *args, **kwargs):
        super(OnNyCoinsCountChange, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._out = self._makeEventOutputSlot('out')
        self._coinsCount = self._makeDataOutputSlot('coinsCount', SLOT_TYPE.INT, None)
        return

    def onStartScript(self):
        self.__nyController.currencies.onNyCoinsUpdate += self.__onNyCoinsUpdate

    def onFinishScript(self):
        self.__nyController.currencies.onNyCoinsUpdate -= self.__onNyCoinsUpdate

    def _exec(self):
        self._coinsCount.setValue(self.__nyController.currencies.getCoinsCount())
        self._out.call()

    def __onNyCoinsUpdate(self):
        self._exec()


class OnRewardAnimationChange(Block, NewYearMeta):
    __nyGiftMachineCtrl = dependency.descriptor(newYearSkeletons.IGiftMachineController)

    def __init__(self, *args, **kwargs):
        super(OnRewardAnimationChange, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._exec)
        self._out = self._makeEventOutputSlot('out')
        self._canSkipAnim = self._makeDataOutputSlot('played', SLOT_TYPE.BOOL, None)
        return

    def onStartScript(self):
        self.__nyGiftMachineCtrl.onSkipAnimStateChanged += self.__onSkipAnimStateChanged

    def onFinishScript(self):
        self.__nyGiftMachineCtrl.onSkipAnimStateChanged -= self.__onSkipAnimStateChanged

    def _exec(self):
        self._canSkipAnim.setValue(self.__nyGiftMachineCtrl.canSkipAnim)
        self._out.call()

    def __onSkipAnimStateChanged(self):
        self._exec()


class SendObjectHoverEvent(Block, NewYearMeta):
    HOVER_IN = 'hoverIn'
    HOVER_OUT = 'hoverOut'

    def __init__(self, *args, **kwargs):
        super(SendObjectHoverEvent, self).__init__(*args, **kwargs)
        self._customizationName = self._makeDataInputSlot('customizationName', SLOT_TYPE.STR)
        self._eventName = eventName = self._makeDataInputSlot('eventName', SLOT_TYPE.STR, EDITOR_TYPE.ENUM_SELECTOR)
        eventName.setEditorData([self.HOVER_IN, self.HOVER_OUT])
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        guiShared.g_eventBus.handleEvent(guiShared.events.ObjectHoverEvent(eventType=self._eventName.getValue(), ctx={'customizationObjectName': self._customizationName.getValue()}), scope=guiShared.EVENT_BUS_SCOPE.DEFAULT)
        self._out.call()


class OnBoughtToy(Block, NewYearMeta):
    __nyController = dependency.descriptor(newYearSkeletons.INewYearController)

    def __init__(self, *args, **kwargs):
        super(OnBoughtToy, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')

    def onStartScript(self):
        self.__nyController.onBoughtToy += self._execute

    def onFinishScript(self):
        self.__nyController.onBoughtToy -= self._execute

    def _execute(self):
        self._out.call()


class OnHangToy(Block, NewYearMeta):
    __nyController = dependency.descriptor(newYearSkeletons.INewYearController)

    def __init__(self, *args, **kwargs):
        super(OnHangToy, self).__init__(*args, **kwargs)
        self._slotID = self._makeDataOutputSlot('slotID', SLOT_TYPE.INT, None)
        self._toyID = self._makeDataOutputSlot('toyID', SLOT_TYPE.INT, None)
        self._out = self._makeEventOutputSlot('out')
        return

    def onStartScript(self):
        self.__nyController.onUpdateSlot += self._execute

    def onFinishScript(self):
        self.__nyController.onUpdateSlot -= self._execute

    def _execute(self, slotID, toyID):
        self._slotID.setValue(slotID)
        self._toyID.setValue(toyID)
        self._out.call()


class GetSlotInfo(Block, NewYearMeta):
    __nyController = dependency.descriptor(newYearSkeletons.INewYearController)

    def __init__(self, *args, **kwargs):
        super(GetSlotInfo, self).__init__(*args, **kwargs)
        self._slotID = self._makeDataInputSlot('slotID', SLOT_TYPE.INT)
        self._hasInstalledToy = self._makeDataOutputSlot('hasInstalledToy', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        toyID = self.__nyController.getInstalledToyInSlot(self._slotID.getValue())
        self._hasInstalledToy.setValue(toyID != nyConstants.INVALID_TOY_ID)


class IsTokenReceived(Block, NewYearMeta):
    __nyController = dependency.descriptor(newYearSkeletons.INewYearController)

    def __init__(self, *args, **kwargs):
        super(IsTokenReceived, self).__init__(*args, **kwargs)
        self._token = self._makeDataInputSlot('token', SLOT_TYPE.STR)
        self._isReceived = self._makeDataOutputSlot('isReceived', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        self._isReceived.setValue(self.__nyController.isTokenReceived(self._token.getValue()))


class IsFriendHangar(Block, NewYearMeta):
    __friendsService = dependency.descriptor(newYearSkeletons.IFriendServiceController)

    def __init__(self, *args, **kwargs):
        super(IsFriendHangar, self).__init__(*args, **kwargs)
        self._isFriendHangar = self._makeDataOutputSlot('isFriendHangar', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        self._isFriendHangar.setValue(self.__friendsService.isInFriendHangar)


class SendJukeboxEvent(Block, NewYearMeta):
    ON_CLICK_SIDE_A = 'onClickSideA'
    ON_CLICK_SIDE_B = 'onClickSideB'
    ON_HIGHLIGHT_ON = 'onHighlightOn'
    ON_HIGHLIGHT_OFF = 'onHighlightOff'

    def __init__(self, *args, **kwargs):
        super(SendJukeboxEvent, self).__init__(*args, **kwargs)
        self._eventName = eventName = self._makeDataInputSlot('eventName', SLOT_TYPE.STR, EDITOR_TYPE.ENUM_SELECTOR)
        eventName.setEditorData([self.ON_CLICK_SIDE_A,
         self.ON_CLICK_SIDE_B,
         self.ON_HIGHLIGHT_ON,
         self.ON_HIGHLIGHT_OFF])
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        guiShared.g_eventBus.handleEvent(guiShared.events.NyJukeboxEvent(eventType=self._eventName.getValue()), scope=guiShared.EVENT_BUS_SCOPE.DEFAULT)
        self._out.call()

    def validate(self):
        return 'Event name value is required' if not self._eventName.hasValue() else super(SendJukeboxEvent, self).validate()


class JukeboxEventHandler(Block, NewYearMeta):
    ON_CLICK_SIDE_A = 'onClickSideA'
    ON_CLICK_SIDE_B = 'onClickSideB'
    ON_HIGHLIGHT_ON = 'onHighlightOn'
    ON_HIGHLIGHT_OFF = 'onHighlightOff'

    def __init__(self, *args, **kwargs):
        super(JukeboxEventHandler, self).__init__(*args, **kwargs)
        self._eventName = eventName = self._makeDataInputSlot('eventName', SLOT_TYPE.STR, EDITOR_TYPE.ENUM_SELECTOR)
        eventName.setEditorData([self.ON_CLICK_SIDE_A,
         self.ON_CLICK_SIDE_B,
         self.ON_HIGHLIGHT_ON,
         self.ON_HIGHLIGHT_OFF])
        self._in = self._makeEventInputSlot('subscribe', self._subscribe)
        self._outSubscribe = self._makeEventOutputSlot('outSubscribe')
        self._outHandleEvent = self._makeEventOutputSlot('outHandleEvent')

    def validate(self):
        return 'Event name value is required' if not self._eventName.hasValue() else super(JukeboxEventHandler, self).validate()

    def onFinishScript(self):
        guiShared.g_eventBus.removeListener(self._eventName.getValue(), self.__onHandleEvent, scope=guiShared.EVENT_BUS_SCOPE.DEFAULT)

    def _subscribe(self):
        guiShared.g_eventBus.addListener(self._eventName.getValue(), self.__onHandleEvent, scope=guiShared.EVENT_BUS_SCOPE.DEFAULT)
        self._outSubscribe.call()

    def __onHandleEvent(self, _):
        self._outHandleEvent.call()


class CreateCollider(Block, NewYearMeta):

    def __init__(self, *args, **kwargs):
        super(CreateCollider, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._gameObject = self._makeDataInputSlot('gameObject', SLOT_TYPE.GAME_OBJECT)
        self._resource = self._makeDataInputSlot('resource', SLOT_TYPE.STR)

    def _execute(self):
        if self._gameObject.hasValue() and not self._gameObject.getValue().findComponentByType(Physics.CollidersComponent):
            colliders = [Physics.MeshColliderDesc(self._resource.getValue(), 'default')]
            self._gameObject.getValue().createComponent(Physics.CollidersComponent, colliders)


class GetAnimatorState(Block, NewYearMeta):

    def __init__(self, *args, **kwargs):
        super(GetAnimatorState, self).__init__(*args, **kwargs)
        self._gameObject = self._makeDataInputSlot('gameObject', SLOT_TYPE.GAME_OBJECT)
        self._layer = self._makeDataInputSlot('layer', SLOT_TYPE.INT)
        self._state = self._makeDataOutputSlot('state', SLOT_TYPE.STR, self._execute)

    def _execute(self):
        if self._gameObject.hasValue():
            animatorComponent = self._gameObject.getValue().findComponentByType(GenericComponents.AnimatorComponent)
            if animatorComponent:
                self._state.setValue(animatorComponent.getStateNodeName(self._layer.getValue()))
