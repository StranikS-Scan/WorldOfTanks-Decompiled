# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/bootcamp_controller.py
from collections import namedtuple
import AccountCommands
import BigWorld
from adisp import process
from account_helpers.AccountSettings import CURRENT_VEHICLE, AccountSettings
from account_helpers import isLongDisconnectedFromCenter
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.bootcamp.disabled_settings import BCDisabledSettings
from gui.Scaleform.daapi.view.dialogs.bootcamp_dialogs_meta import ExecutionChooserDialogMeta
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from bootcamp.BootCampEvents import g_bootcampEvents
from PlayerEvents import g_playerEvents
from bootcamp.Bootcamp import g_bootcamp
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui import DialogsInterface
from debug_utils import LOG_ERROR
BootcampDialogConstants = namedtuple('BootcampDialogConstants', 'dialogType dialogKey focusedID needAwarding')

class BootcampController(IBootcampController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

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
        else:
            self.__doStopBootcamp()

    @property
    def replayCtrl(self):
        return g_bootcamp.replayCtrl

    @property
    def nationData(self):
        return g_bootcamp.getNationData()

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

    def isEnableDamageIcon(self):
        return g_bootcamp.isEnableDamageIcon()

    def getCheckpoint(self):
        return g_bootcamp.getCheckpoint()

    def saveCheckpoint(self, checkpoint):
        g_bootcamp.saveCheckpoint(checkpoint)

    @property
    def nation(self):
        return g_bootcamp.nation

    def changeNation(self, nationIndex):
        g_bootcamp.changeNation(nationIndex)

    def getContext(self):
        return g_bootcamp.getContext()

    def getContextIntParameter(self, parameter, default=0):
        return g_bootcamp.getContextIntParameter(parameter, default)

    def getDisabledSettings(self):
        return self.__disabledSettings.disabledSetting

    def showFinalVideo(self, callback):
        g_bootcamp.showFinalVideo(callback)

    def finishBootcamp(self):
        Waiting.show('login')
        g_bootcampEvents.onGarageLessonFinished(self.getLessonNum())
        g_bootcampEvents.onRequestBootcampFinish()

    def __onEnterBootcamp(self):
        self.__inBootcamp = True

    def __onExitBootcamp(self):
        self.__inBootcamp = False

    def __doStartBootcamp(self):
        BigWorld.player().startBootcampCmd()

    def __doStopBootcamp(self):
        BigWorld.player().base.requestBootcampQuit(AccountSettings.getFavorites(CURRENT_VEHICLE))

    def __onBootcampBecomePlayer(self):
        self.__inBootcampAccount = True
        Waiting.hide('login')

    def __onBootcampBecomeNonPlayer(self):
        self.__inBootcampAccount = False

    def __onBootcampStartChoice(self):
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_INTRO, None, g_bootcamp.getIntroPageData(True)), EVENT_BUS_SCOPE.LOBBY)
        return

    def __onGameplayChoice(self, gameplayType, gameplayChoice):
        BigWorld.player().base.doCmdIntStr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_GAMEPLAY_CHOICE, gameplayChoice, gameplayType)

    def runBootcamp(self):
        if self.isInBootcamp():
            if not self.needAwarding():
                self.stopBootcamp(inBattle=not self.isInBootcampAccount())
            else:
                self.__doBootcamp(isSkip=True)
        elif isLongDisconnectedFromCenter():
            DialogsInterface.showI18nInfoDialog('bootcampCenterUnavailable', lambda result: None)
        else:
            self.__doBootcamp(isSkip=False)

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def getSkipDialogConstants(self, isSkip=True):
        bootcampLiteral = 'bootcamp/'
        needAwarding = self.needAwarding()
        isReferralEnabled = self.isReferralEnabled()
        dialogType, focusedID = (ExecutionChooserDialogMeta.SKIP, DIALOG_BUTTON_ID.CLOSE) if isSkip else (ExecutionChooserDialogMeta.RETRY, DIALOG_BUTTON_ID.SUBMIT)
        dialogKey = bootcampLiteral + dialogType
        if isReferralEnabled and dialogType == ExecutionChooserDialogMeta.SKIP:
            dialogKey = bootcampLiteral + ExecutionChooserDialogMeta.SKIP_REFERRAL
        if not isSkip and needAwarding:
            dialogKey = bootcampLiteral + ExecutionChooserDialogMeta.START
        return BootcampDialogConstants(dialogType=dialogType, dialogKey=dialogKey, focusedID=focusedID, needAwarding=needAwarding)

    @process
    def __doBootcamp(self, isSkip):
        dialogConstants = self.getSkipDialogConstants(isSkip)
        result = yield DialogsInterface.showDialog(ExecutionChooserDialogMeta(dialogConstants.dialogType, dialogConstants.dialogKey, dialogConstants.focusedID, not dialogConstants.needAwarding and not isSkip))
        if result:
            if isSkip:
                self.stopBootcamp(inBattle=not self.isInBootcampAccount())
            elif self.prbDispatcher is not None:
                action = PrbAction(PREBATTLE_ACTION_NAME.BOOTCAMP)
                yield self.prbDispatcher.doSelectAction(action)
        return
