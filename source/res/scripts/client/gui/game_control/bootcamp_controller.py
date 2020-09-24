# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/bootcamp_controller.py
from collections import namedtuple
import AccountCommands
import BigWorld
from async import async, await
from adisp import process
from account_helpers.AccountSettings import CURRENT_VEHICLE, AccountSettings
from account_helpers import isLongDisconnectedFromCenter
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.bootcamp.disabled_settings import BCDisabledSettings
from gui.Scaleform.daapi.view.dialogs.bootcamp_dialogs_meta import ExecutionChooserDialogMeta
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID, BCConfirmDialogMeta
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.Bootcamp import g_bootcamp, LESSON_COUNT
from PlayerEvents import g_playerEvents
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui import DialogsInterface, makeHtmlString
from debug_utils import LOG_ERROR
from gui.shared.event_dispatcher import showResSimpleDialog
BootcampDialogConstants = namedtuple('BootcampDialogConstants', 'dialogType dialogKey focusedID needAwarding premiumType')
_YELLOW = 'yellow'
_GRAY = 'gray'
_REWARD = '\n{}'

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

    @property
    def replayCtrl(self):
        return g_bootcamp.replayCtrl

    @property
    def nationData(self):
        return g_bootcamp.getNationData()

    @property
    def nation(self):
        return g_bootcamp.nation

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

    def getAwardVehicles(self):
        return [self.nationData['vehicle_first'], self.nationData['vehicle_second']] if self.nationData else []

    def isEnableDamageIcon(self):
        return g_bootcamp.isEnableDamageIcon()

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

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def getSkipDialogConstants(self, isSkip=True):
        bootcampLiteral = 'bootcamp/'
        needAwarding = self.needAwarding()
        isReferralEnabled = self.isReferralEnabled()
        if isSkip:
            dialogType, focusedID = ExecutionChooserDialogMeta.SKIP, DIALOG_BUTTON_ID.CLOSE
        else:
            dialogType, focusedID = ExecutionChooserDialogMeta.RETRY, DIALOG_BUTTON_ID.SUBMIT
        dialogKey = bootcampLiteral + dialogType
        if isReferralEnabled and dialogType == ExecutionChooserDialogMeta.SKIP:
            dialogKey = bootcampLiteral + ExecutionChooserDialogMeta.SKIP_REFERRAL
        if not isSkip and needAwarding:
            dialogKey = bootcampLiteral + ExecutionChooserDialogMeta.START
        return BootcampDialogConstants(dialogType=dialogType, dialogKey=dialogKey, focusedID=focusedID, needAwarding=needAwarding, premiumType=g_bootcamp.getPremiumType(LESSON_COUNT))

    @async
    def __doBootcamp(self, isSkip):
        g_eventBus.handleEvent(events.DestroyViewEvent(VIEW_ALIAS.LOBBY_MENU))
        if isSkip:
            self.__skipBootcamp()
        else:
            needAwarding = self.needAwarding()
            startAcc = R.strings.bootcamp.message.start if needAwarding else R.strings.bootcamp.message.restart
            iconAcc = R.images.gui.maps.icons.bootcamp.dialog
            icon = iconAcc.bc_enter_small() if needAwarding else iconAcc.bc_enter_1_small()
            if needAwarding:
                messageSkipAcc = R.strings.bootcamp.message.skip.message
                premiumStr = self.__format(messageSkipAcc.premium(), _YELLOW)
                goldStr = self.__format(messageSkipAcc.gold(), _YELLOW)
                crewStr = self.__format(messageSkipAcc.crew(), _YELLOW)
                message = self.__format(startAcc.message(), _GRAY, premium=premiumStr, gold=goldStr, crew=crewStr)
            else:
                rewardStr = _REWARD.format(self.__format(startAcc.reward(), _YELLOW))
                message = self.__format(startAcc.message(), _GRAY, reward=rewardStr)
            result = yield await(showResSimpleDialog(startAcc, icon, message))
            if result:
                self.__goBootcamp()

    @process
    def __skipBootcamp(self):
        skipAcc = R.strings.bootcamp.message.skip
        iconAcc = R.images.gui.maps.icons.bootcamp.dialog
        if self.needAwarding():
            icon = backport.image(iconAcc.bc_leave())
            messageAcc = skipAcc.message
            premiumStr = self.__format(messageAcc.premium(), _YELLOW)
            goldStr = self.__format(messageAcc.gold(), _YELLOW)
            crewStr = self.__format(messageAcc.crew(), _YELLOW)
            if self.isReferralEnabled():
                message = self.__format(skipAcc.referral.message(), _GRAY, premium=premiumStr, gold=goldStr, crew=crewStr)
            else:
                message = self.__format(messageAcc(), _GRAY, premium=premiumStr, gold=goldStr, crew=crewStr)
        else:
            icon = backport.image(iconAcc.bc_leave_noreward())
            message = self.__format(skipAcc.completed.message(), _GRAY)
        result = yield DialogsInterface.showBCConfirmationDialog(BCConfirmDialogMeta({'label': backport.text(skipAcc.label()),
         'labelExecute': backport.text(skipAcc.labelExecute()),
         'icon': icon,
         'message': message,
         'isTraining': True}))
        if result:
            self.stopBootcamp(inBattle=not self.isInBootcampAccount())

    def __goBootcamp(self):
        action = PrbAction(PREBATTLE_ACTION_NAME.BOOTCAMP)
        event = events.PrbActionEvent(action, events.PrbActionEvent.SELECT)
        g_eventBus.handleEvent(event, EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __format(text, style, **kwargs):
        return makeHtmlString('html_templates:bootcamp/message', style, ctx={'text': backport.text(text, **kwargs)})
