# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/bootcamp_controller.py
from collections import namedtuple
from functools import partial
import AccountCommands
import BigWorld
from constants import QUEUE_TYPE, BOOTCAMP
from wg_async import wg_async, wg_await
from account_helpers.AccountSettings import AccountSettings, BOOTCAMP_VEHICLE
from account_helpers import isLongDisconnectedFromCenter
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.bootcamp.bootcamp_exit_view import BootcampExitWindow
from gui.prb_control.prb_getters import getQueueType
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBootcampController, IDemoAccCompletionController, IHangarSpaceSwitchController
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.bootcamp.disabled_settings import BCDisabledSettings
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.Bootcamp import g_bootcamp
from PlayerEvents import g_playerEvents
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui import DialogsInterface, makeHtmlString
from debug_utils import LOG_ERROR
from gui.shared.event_dispatcher import showResSimpleDialog
from skeletons.gui.shared import IItemsCache
BootcampDialogConstants = namedtuple('BootcampDialogConstants', 'dialogType dialogKey focusedID needAwarding premiumType')
_GREEN = 'green'
_YELLOW = 'yellow'
_GRAY = 'gray'
_REWARD = '\n{}'

class BootcampController(IBootcampController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)
    demoAccController = dependency.descriptor(IDemoAccCompletionController)
    itemsCache = dependency.descriptor(IItemsCache)
    appLoader = dependency.descriptor(IAppLoader)
    spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)

    def __init__(self):
        super(BootcampController, self).__init__()
        self.__inBootcamp = False
        self.__automaticStart = False
        self.__inBootcampAccount = False
        self.__disabledSettings = BCDisabledSettings()
        g_bootcampEvents.onBootcampBecomePlayer += self.__onBootcampBecomePlayer
        g_bootcampEvents.onBootcampBecomeNonPlayer += self.__onBootcampBecomeNonPlayer
        g_bootcampEvents.onBootcampStarted += self.__onEnterBootcamp
        g_bootcampEvents.onBootcampFinished += self.__onExitBootcamp
        g_playerEvents.onBootcampStartChoice += self.__onBootcampStartChoice
        g_bootcampEvents.onGameplayChoice += self.__onGameplayChoice
        self.spaceSwitchController.onCheckSceneChange += self.__onCheckSceneChange

    @property
    def replayCtrl(self):
        return g_bootcamp.replayCtrl

    @property
    def nationData(self):
        return g_bootcamp.getNationData()

    @property
    def nation(self):
        return g_bootcamp.nation

    @property
    def version(self):
        return g_bootcamp.getVersion()

    def startBootcamp(self, inBattle):
        if g_playerEvents.isPlayerEntityChanging:
            return
        if self.__inBootcamp:
            LOG_ERROR('Trying to startBootcamp - is already started')
            return
        if not inBattle:
            self.__doStartBootcamp()

    def stopBootcamp(self, inBattle):
        if g_playerEvents.isPlayerEntityChanging:
            return
        if not self.__inBootcamp:
            LOG_ERROR('Trying to stop bootcamp - is already stopped')
            return
        if inBattle:
            g_bootcamp.requestBootcampFinishFromBattle = True
            self.sessionProvider.exit()
        elif self.demoAccController.isDemoAccount:
            self.demoAccController.runDemoAccRegistration()
        else:
            self.__doStopBootcamp()

    def isInBootcamp(self):
        return self.__inBootcamp

    def hasFinishedBootcampBefore(self):
        return g_bootcamp.getParameters().get('completed', 0) > 0

    def runCount(self):
        return g_bootcamp.getParameters().get('runCount', 0)

    def needAwarding(self):
        return g_bootcamp.getParameters().get('needAwarding', False)

    def isReferralEnabled(self):
        return g_bootcamp.isReferralEnabled()

    def isInBootcampAccount(self):
        return self.__inBootcampAccount

    def fini(self):
        g_bootcampEvents.onBootcampBecomePlayer -= self.__onBootcampBecomePlayer
        g_bootcampEvents.onBootcampBecomeNonPlayer -= self.__onBootcampBecomeNonPlayer
        g_bootcampEvents.onBootcampStarted -= self.__onEnterBootcamp
        g_bootcampEvents.onBootcampFinished -= self.__onExitBootcamp
        g_playerEvents.onBootcampStartChoice -= self.__onBootcampStartChoice
        g_bootcampEvents.onGameplayChoice -= self.__onGameplayChoice
        self.spaceSwitchController.onCheckSceneChange -= self.__onCheckSceneChange

    def onLobbyInited(self, event):
        if self.__automaticStart:
            self.__doStartBootcamp()
            self.__automaticStart = False

    def setAutomaticStart(self, enable):
        self.__automaticStart = enable

    def enqueueBootcamp(self):
        if g_bootcamp.isRunning():
            BigWorld.player().enqueueBootcamp(g_bootcamp.getLessonNum())

    def dequeueBootcamp(self):
        BigWorld.player().dequeueBootcamp()

    def showActionWaitWindow(self):
        g_bootcamp.showActionWaitWindow()

    def hideActionWaitWindow(self):
        g_bootcamp.hideActionWaitWindow()

    def getLessonNum(self):
        return g_bootcamp.getLessonNum()

    def getAwardVehicles(self):
        return [self.nationData['vehicle_first'], self.nationData['vehicle_second']] if self.nationData else []

    def isEnableCriticalDamageIcon(self):
        return g_bootcamp.isEnableCriticalDamageIcon()

    def getCheckpoint(self):
        return g_bootcamp.getCheckpoint()

    def saveCheckpoint(self, checkpoint):
        g_bootcamp.saveCheckpoint(checkpoint)

    def changeNation(self, nationIndex):
        g_bootcamp.changeNation(nationIndex)

    def getContext(self):
        return g_bootcamp.getContext()

    def getContextIntParameter(self, parameter, default=0):
        return g_bootcamp.getContextIntParameter(parameter, default)

    def getDisabledSettings(self):
        return self.__disabledSettings.disabledSetting

    def showFinalVideo(self, callback):
        pass

    def finishBootcamp(self):
        Waiting.show('login')
        if self.demoAccController.isDemoAccount:
            self.demoAccController.isInDemoAccRegistration = False
        currentLesson = self.getLessonNum()
        if g_bootcamp.isLastLesson(currentLesson):
            g_bootcampEvents.onGarageLessonFinished(currentLesson)
        g_bootcampEvents.onRequestBootcampFinish()

    def __onCheckSceneChange(self):
        if self.__inBootcamp:
            self.spaceSwitchController.hangarSpaceUpdate(BOOTCAMP)

    def __onEnterBootcamp(self):
        self.__inBootcamp = True

    def __onExitBootcamp(self):
        self.__inBootcamp = False

    def __doStartBootcamp(self):
        BigWorld.player().startBootcampCmd()

    def __doStopBootcamp(self):
        BigWorld.player().base.requestBootcampQuit(AccountSettings.getFavorites(BOOTCAMP_VEHICLE))

    def __onBootcampBecomePlayer(self):
        self.__inBootcampAccount = True
        Waiting.hide('login')

    def __onBootcampBecomeNonPlayer(self):
        self.__inBootcampAccount = False

    def __onBootcampStartChoice(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BOOTCAMP_INTRO), ctx=g_bootcamp.getIntroPageData(True)), EVENT_BUS_SCOPE.LOBBY)

    def __onGameplayChoice(self, gameplayType, gameplayChoice):
        BigWorld.player().base.doCmdIntStr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_GAMEPLAY_CHOICE, gameplayChoice, gameplayType)

    def runBootcamp(self):
        if self.isInBootcamp():
            self.__doBootcamp(isSkip=True)
        elif isLongDisconnectedFromCenter():
            DialogsInterface.showI18nInfoDialog('bootcampCenterUnavailable', lambda result: None)
        else:
            self.__doBootcamp(isSkip=False)

    def canRun(self):
        queueType = getQueueType()
        return self.lobbyContext.getServerSettings().isBootcampEnabled() and (not queueType or queueType == QUEUE_TYPE.BOOTCAMP)

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @wg_async
    def __doBootcamp(self, isSkip):
        isFromLobbyMenu = self.__isLobbyMenuOpened()
        if isFromLobbyMenu:
            g_eventBus.handleEvent(events.DestroyViewEvent(VIEW_ALIAS.LOBBY_MENU))
        if isSkip:
            self.__skipBootcamp()
        else:
            needAwarding = self.needAwarding()
            startAcc = R.strings.bootcamp.message.start if needAwarding else R.strings.bootcamp.message.restart
            iconAcc = R.images.gui.maps.icons.bootcamp.dialog
            icon = iconAcc.bc_enter_small() if needAwarding else iconAcc.bc_enter_1_small()
            if needAwarding:
                messageStartAcc = R.strings.bootcamp.message.start.message
                premiumStr = self.__format(messageStartAcc.premium(), _YELLOW)
                goldStr = self.__format(messageStartAcc.gold(), _YELLOW)
                crewStr = self.__format(messageStartAcc.crew(), _YELLOW)
                message = self.__format(startAcc.message(), _GRAY, premium=premiumStr, gold=goldStr, crew=crewStr)
            else:
                rewardStr = _REWARD.format(self.__format(startAcc.reward(), _GREEN))
                message = self.__format(startAcc.message(), _GRAY, reward=rewardStr)
            result = yield wg_await(showResSimpleDialog(startAcc, icon, message))
            if result:
                self.__goBootcamp()
            elif isFromLobbyMenu:
                g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    def __skipBootcamp(self):
        window = BootcampExitWindow(partial(self.stopBootcamp, not self.isInBootcampAccount()))
        window.load()

    def __goBootcamp(self):
        action = PrbAction(PREBATTLE_ACTION_NAME.BOOTCAMP)
        event = events.PrbActionEvent(action, events.PrbActionEvent.SELECT)
        g_eventBus.handleEvent(event, EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __format(text, style, **kwargs):
        return makeHtmlString('html_templates:bootcamp/message', style, ctx={'text': backport.text(text, **kwargs)})

    def __isLobbyMenuOpened(self):
        app = self.appLoader.getApp()
        container = app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        return container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}) is not None
