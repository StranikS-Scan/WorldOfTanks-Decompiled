# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/Bootcamp.py
import BigWorld
from copy import deepcopy
import constants
import base64
import cPickle
import BattleReplay
import TriggersManager
import SoundGroups
import MusicControllerWWISE as MC
from account_helpers.AccountSettings import CURRENT_VEHICLE, AccountSettings
from account_helpers.settings_core import ISettingsCore
from account_helpers import isPremiumAccount
from adisp import process, async
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from PlayerEvents import g_playerEvents
from BootCampEvents import g_bootcampEvents
from BootcampContext import Chapter
from BootcampTransition import BootcampTransition
from BootcampPreferences import BootcampPreferences
from BootcampSettings import getBattleSettings, getGarageDefaults
from ReloadLobbyHelper import ReloadLobbyHelper
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.login.EULADispatcher import EULADispatcher
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.prb_control import prbEntityProperty
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from states import STATE
from states.StateInGarage import StateInGarage
from states.StateInitial import StateInitial
from states.StateOutroVideo import StateOutroVideo
from states.StateResultScreen import StateResultScreen
from skeletons.connection_mgr import IConnectionManager
from BootcampGUI import BootcampGUI
from BootcampReplayController import BootcampReplayController
from constants import BOOTCAMP_BATTLE_RESULT_MESSAGE
from gui.app_loader import g_appLoader
from gui import makeHtmlString
DISABLED_TANK_LEVELS = (1,)

class BOOTCAMP_LESSON(object):
    BATTLE = 0
    GARAGE = 1


class Bootcamp(EventSystemEntity):
    settingsCore = dependency.descriptor(ISettingsCore)
    connectionMgr = dependency.descriptor(IConnectionManager)
    BOOTCAMP_SOUND_BANKS = ('ambient.bnk', 'bootcamp.pck', 'bootcamp_gui.bnk', 'bootcamp_hangar.bnk', 'bootcamp_voiceover.bnk', 'bootcamp_result_screen.bnk')

    def __init__(self):
        super(Bootcamp, self).__init__()
        self.__currentState = StateInitial()
        self.__running = False
        self.__account = None
        self.__avatar = None
        self.__lessonId = 0
        self.__isBattleLesson = False
        self.__context = {}
        self.__chapter = None
        self.__gui = None
        self.__arenaUniqueID = None
        self.__resultType = 0
        self.__resultReason = 0
        self.__resultTypeStr = ''
        self.__resultReasonStr = ''
        self.__resultReusableInfo = None
        self.__hangarSpace = None
        self.__hangarSpacePremium = None
        self.__bonuses = None
        self.__isIntroVideoPlayed = False
        self.__currentLobbySettingsVisibility = None
        self.__requestBootcampFinishFromBattle = False
        self.transitionFlash = None
        self.__isSniperModeUsed = False
        self.__showingWaitingActionWindow = False
        self.__nation = 0
        self.__nationsData = {}
        self.__checkpoint = ''
        self.__nationWindowRemovedCallback = None
        self.__preferences = None
        self.__replayController = None
        self.__p = {'manualStart': False,
         'finished': False}
        return

    @async
    def nextFrame(self, callback):
        BigWorld.callback(0.0, lambda : callback(True))

    def replayCallbackSubscribe(self):
        BattleReplay.g_replayCtrl.setDataCallback('bootcamp_setContext', self.replaySetContext)

    def serializeContext(self):
        return base64.b64encode(cPickle.dumps(self.__context, -1))

    def deserializeContext(self, contextBin):
        return cPickle.loads(base64.b64decode(contextBin))

    def onAvatarInit(self):
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.serializeCallbackData('bootcamp_setContext', (self.serializeContext(),))

    @property
    def requestBootcampFinishFromBattle(self):
        return self.__requestBootcampFinishFromBattle

    @requestBootcampFinishFromBattle.setter
    def requestBootcampFinishFromBattle(self, value):
        self.__requestBootcampFinishFromBattle = value

    def replaySetContext(self, contextBin):
        self.setContext(self.deserializeContext(contextBin))

    def setContext(self, context):
        self.__context = context
        self.__checkpoint = ''
        if context is None:
            return
        else:
            if 'checkpoint' in self.__context:
                self.__checkpoint = self.__context['checkpoint']
            return

    def __cm_onDisconnected(self):
        self.stop(0)

    def setAccount(self, account):
        self.__account = account

    @property
    def account(self):
        return self.__account

    def getContext(self):
        return self.__context

    def getContextIntParameter(self, parameter, default=0):
        return self.__context.get(parameter, default)

    def getLessonNum(self):
        return self.__lessonId

    def getLessonType(self):
        return self.__lessonType

    def setBattleResults(self, arenaUniqueID, resultType, resultReason):
        self.__arenaUniqueID = arenaUniqueID
        self.__resultType = resultType
        self.__resultReason = resultReason
        from gui.battle_results.components.common import makeRegularFinishResultLabel
        from gui.battle_results.settings import PLAYER_TEAM_RESULT
        if not resultType:
            teamResult = PLAYER_TEAM_RESULT.DRAW
        elif resultType == BOOTCAMP_BATTLE_RESULT_MESSAGE.VICTORY:
            teamResult = PLAYER_TEAM_RESULT.WIN
        else:
            teamResult = PLAYER_TEAM_RESULT.DEFEAT
        self.__resultTypeStr = makeHtmlString('html_templates:bootcamp/battle_results', teamResult)
        self.__resultReasonStr = makeRegularFinishResultLabel(resultReason, teamResult)
        self.__resultReusableInfo = None
        return

    def setBattleResultsReusableInfo(self, reusableInfo):
        if reusableInfo.arenaUniqueID == self.__arenaUniqueID:
            self.__resultReusableInfo = reusableInfo

    def getBattleResults(self):
        return (self.__resultType,
         self.__resultReason,
         self.__resultTypeStr,
         self.__resultReasonStr,
         self.__resultReusableInfo)

    def getBattleResultsExtra(self, lessonId):
        from BootcampGarage import g_bootcampGarage
        battleResults = g_bootcampGarage.getBattleResultsExtra(lessonId)
        return battleResults

    def isManualStart(self):
        return self.__p['manualStart']

    def isIntroVideoPlayed(self):
        return self.__isIntroVideoPlayed

    def setIntroVideoPlayed(self):
        self.__isIntroVideoPlayed = True

    def resetSniperModeUsed(self):
        self.__isSniperModeUsed = False

    def isSniperModeUsed(self):
        result = self.__isSniperModeUsed
        self.__isSniperModeUsed = True
        return result

    @process
    def start(self, lessonNum, isBattleLesson):
        LOG_DEBUG_DEV_BOOTCAMP('Starting bootcamp', lessonNum, isBattleLesson)
        from gui.shared.personality import ServicesLocator
        if BattleReplay.g_replayCtrl.isPlaying:
            self.__replayController = BootcampReplayController()
            self.__replayController.init()
        g_bootcampEvents.onBattleLessonFinished += self.onBattleLessonFinished
        g_bootcampEvents.onGarageLessonFinished += self.onGarageLessonFinished
        g_bootcampEvents.onBattleLoaded += self.onBattleLoaded
        g_bootcampEvents.onResultScreenFinished += self.onResultScreenFinished
        g_bootcampEvents.onRequestBootcampFinish += self.onRequestBootcampFinish
        g_bootcampEvents.onOutroVideoStop += self.onOutroVideoStop
        g_bootcampEvents.onBootcampBecomeNonPlayer += self.onBootcampBecomeNonPlayer
        g_playerEvents.onAvatarBecomeNonPlayer += self.__onAvatarBecomeNonPlayer
        g_playerEvents.onArenaCreated += self.__onArenaCreated
        self.connectionMgr.onDisconnected += self.__cm_onDisconnected
        self.__requestBootcampFinishFromBattle = False
        ctx = self.getContext()
        isRelogin = ctx['relogin']
        LOG_DEBUG_DEV_BOOTCAMP('IsRelogin', isRelogin)
        if not BattleReplay.isPlaying():
            if not isRelogin:
                self.showActionWaitWindow()
                yield self.settingsCore.serverSettings.settingsCache.update()
                self.settingsCore.serverSettings.applySettings()
                if ctx['isNewbie'] and not ctx['completed'] and ctx['runCount'] == 1:
                    self.__preferences = BootcampPreferences()
                    self.__preferences.setup()
                self.hideActionWaitWindow()
                eula = EULADispatcher()
                yield eula.processLicense()
                eula.fini()
        self.__running = True
        self.__lessonId = lessonNum
        self.__lessonType = BOOTCAMP_LESSON.BATTLE if isBattleLesson else BOOTCAMP_LESSON.GARAGE
        if (lessonNum == 0 or not isBattleLesson) and not isRelogin:
            self.showActionWaitWindow()
            yield ServicesLocator.itemsCache.update(CACHE_SYNC_REASON.SHOW_GUI)
            self.hideActionWaitWindow()
        if self.__currentState is not None:
            self.__currentState.deactivate()
        self.__hangarSpace = ctx['hangarSpace']
        self.__hangarSpacePremium = ctx['hangarSpacePremium']
        self.__bonuses = ctx['bonuses']
        showRewards = ctx['needAwarding']
        previousLesson = self.getContextIntParameter('lastLessonNum') - 1
        if previousLesson >= 0 and previousLesson < len(self.__bonuses['battle']):
            self.__bonuses['battle'][previousLesson]['showRewards'] = showRewards
        self.__nation = ctx['nation']
        self.__nationsData = ctx['nationsData']
        self.__p['completed'] = ctx['completed']
        self.__p['needAwarding'] = ctx['needAwarding']
        from states.StateBattlePreparing import StateBattlePreparing
        if not BattleReplay.isPlaying():
            if isBattleLesson:
                self.enqueueBattleLesson()
            else:
                self.showActionWaitWindow()
                yield self.nextFrame()
                self.__currentState = StateInGarage(self.__lessonId, self.__account, self.__checkpoint)
                ReloadLobbyHelper().reload()
                self.hideActionWaitWindow()
                self.__currentState.activate()
        else:
            self.__currentState = StateBattlePreparing(self.__lessonId, BigWorld.player())
            self.__currentState.activate()
        BigWorld.overloadBorders(True)
        if self.__chapter is None:
            self.__chapter = Chapter()
        if self.__gui is None:
            self.__gui = BootcampGUI()
        for bankName in self.BOOTCAMP_SOUND_BANKS:
            SoundGroups.g_instance.loadSoundBank(bankName)

        g_bootcampEvents.onBootcampStarted()
        from BootcampGarage import g_bootcampGarage
        g_bootcampGarage.initSubscriptions()
        return

    def stop(self, reason):
        g_bootcampEvents.onBootcampFinished()
        BigWorld.overloadBorders(False)
        if self.__gui is not None:
            self.__gui.clear()
            self.__gui = None
        if self.__chapter is not None:
            self.__chapter.clear()
            self.__chapter = None
        g_bootcampEvents.onBattleLessonFinished -= self.onBattleLessonFinished
        g_bootcampEvents.onGarageLessonFinished -= self.onGarageLessonFinished
        g_bootcampEvents.onBattleLoaded -= self.onBattleLoaded
        g_bootcampEvents.onResultScreenFinished -= self.onResultScreenFinished
        g_bootcampEvents.onRequestBootcampFinish -= self.onRequestBootcampFinish
        g_bootcampEvents.onOutroVideoStop -= self.onOutroVideoStop
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__onAvatarBecomeNonPlayer
        g_playerEvents.onArenaCreated -= self.__onArenaCreated
        self.connectionMgr.onDisconnected -= self.__cm_onDisconnected
        if self.__running:
            self.__running = False
        if self.__currentState:
            self.__currentState.deactivate()
        self.__currentState = StateInitial()
        if self.__preferences:
            self.__preferences.destroy()
            self.__preferences = None
        self.__account = None
        self.__context = {}
        self.__isIntroVideoPlayed = False
        if self.__replayController is not None:
            self.__replayController.fini()
            self.__replayController = None
        MC.g_musicController.stopAmbient()
        for bankName in self.BOOTCAMP_SOUND_BANKS:
            SoundGroups.g_instance.unLoadSoundBank(bankName)

        from BootcampGarage import g_bootcampGarage
        g_bootcampGarage.destroySubscriptions()
        return

    def isRunning(self):
        return self.__running

    def isFinished(self):
        return self.__p['completed']

    def handleKeyEvent(self, event):
        if self.isRunning() and self.__currentState is not None:
            self.__currentState.handleKeyEvent(event)
        return

    @property
    def replayCtrl(self):
        return self.__replayController

    @prbEntityProperty
    def prbEntity(self):
        pass

    def showActionWaitWindow(self):
        if not self.__showingWaitingActionWindow:
            self.__showingWaitingActionWindow = True
            Waiting.show('sinhronize')

    def hideActionWaitWindow(self):
        if self.__showingWaitingActionWindow:
            self.__showingWaitingActionWindow = False
            Waiting.hide('sinhronize')

    def onBootcampBecomeNonPlayer(self):
        self.hideActionWaitWindow()

    def onBattleLoaded(self, lessonId):
        from states.StateInBattle import StateInBattle
        LOG_DEBUG_DEV_BOOTCAMP('onBattleLoaded called')
        self.__currentState.deactivate()
        self.__avatar = BigWorld.player()
        self.__currentState = StateInBattle(lessonId, self.__avatar, self.__chapter, self.__gui)
        self.__currentState.activate()

    def onBattleLessonFinished(self, lessonId, lessonResults):
        self.__lessonId = lessonId
        self.__currentState.deactivate()
        if self.requestBootcampFinishFromBattle:
            self.onRequestBootcampFinish()
            return
        self.__currentState = StateResultScreen(lessonResults)
        self.__currentState.activate()

    def __onAvatarBecomeNonPlayer(self):
        if self.__currentState is not None:
            self.__currentState.onAvatarBecomeNonPlayer()
        return

    def __onArenaCreated(self):
        from states.StateBattlePreparing import StateBattlePreparing
        if self.__currentState:
            self.__currentState.deactivate()
        self.__currentState = StateBattlePreparing(self.__lessonId, self.__account)
        self.__currentState.activate()

    def onBattleAction(self, actionId, actionArgs):
        if actionId == constants.BOOTCAMP_BATTLE_ACTION.PLAYER_OBSERVED_ACTION:
            if actionArgs[0] == 1:
                TriggersManager.g_manager.activateTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_OBSERVED)
            else:
                TriggersManager.g_manager.deactivateTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_OBSERVED)
        else:
            g_bootcampEvents.onBattleAction(actionId, actionArgs)
            self.__currentState.onBattleAction(actionId, actionArgs)

    def isInBattleResultState(self):
        return isinstance(self.__currentState, StateResultScreen)

    def onResultScreenFinished(self, reward):
        self.__currentState.deactivate()
        isVictory = self.__resultType == constants.BOOTCAMP_BATTLE_RESULT_MESSAGE.VICTORY
        if self.__lessonId == 0:
            if not isVictory:
                from gui.prb_control.dispatcher import g_prbLoader
                g_prbLoader.setEnabled(True)
                g_appLoader.showLobby()
                self.__currentState = StateInitial()
                self.enqueueBattleLesson()
            else:
                self.__currentState = StateInGarage(self.__lessonId, self.__account, self.__checkpoint)
        else:
            self.__currentState = StateInGarage(self.__lessonId, self.__account, self.__checkpoint)
        self.__currentState.activate()

    def enqueueBattleLesson(self):
        if self.prbEntity is not None:
            self.prbEntity.doAction()
        return

    def showFinalVideo(self):
        LOG_DEBUG_DEV_BOOTCAMP('showFinalVideo')
        self.__currentState.deactivate()
        self.__currentState = StateOutroVideo()
        self.__currentState.activate()

    def onGarageLessonFinished(self, lessonId):
        LOG_DEBUG_DEV_BOOTCAMP('onGarageLessonFinished', lessonId)
        self.__account.base.completeBootcampLesson(0)
        lastLesson = self.getContextIntParameter('lastLessonNum')
        if self.__lessonId == lastLesson:
            LOG_DEBUG_DEV_BOOTCAMP('Finished last lesson', lessonId)
        else:
            self.enqueueBattleLesson()

    def onRequestBootcampFinish(self):
        LOG_DEBUG_DEV_BOOTCAMP('onRequestBootcampFinish')
        self.__account.base.requestBootcampQuit(AccountSettings.getFavorites(CURRENT_VEHICLE))

    def finishBootcamp(self):
        LOG_DEBUG_DEV_BOOTCAMP('finishBootcamp', self.__currentState.id())
        self.finishFromGarageLesson()
        self.setContext({})
        self.setAccount(None)
        return

    def finishFromGarageLesson(self):
        self.__running = False
        BootcampTransition.start()
        self.setDefaultHangarSpace()
        self.stop(0)
        ReloadLobbyHelper().reload()

    def onOutroVideoStop(self):
        if not self.requestBootcampFinishFromBattle:
            from BootcampGarage import g_bootcampGarage
            g_bootcampGarage.init(self.__lessonId, self.__account)
            g_bootcampGarage.showBootcampGraduateMessage()

    def hookOnEnterWorld(self):
        return False if self.__currentState is None or self.__currentState.id() != STATE.BATTLE_PREPARING else self.__currentState.hookOnEnterWorld()

    def hookVehicleOnEnterWorld(self):
        return False if self.__currentState is None or self.__currentState.id() != STATE.BATTLE_PREPARING else self.__currentState.hookVehicleOnEnterWorld()

    def onEnterWorld(self, avatar):
        self.__currentState.onEnterWorld(avatar)

    def vehicleOnEnterWorld(self, avatar, vehicle):
        self.__avatar = avatar
        self.__currentState.vehicleOnEnterWorld(avatar, vehicle)

    def getDefaultLobbySettings(self):
        return deepcopy(getGarageDefaults()['panels'])

    def getLobbySettings(self):
        if not self.__currentLobbySettingsVisibility:
            self.__currentLobbySettingsVisibility = self.getDefaultLobbySettings()
        return self.__currentLobbySettingsVisibility

    def setLobbySettings(self, value):
        self.__currentLobbySettingsVisibility = value

    def updateLobbyLobbySettingsVisibility(self, element, value):
        if element in self.__currentLobbySettingsVisibility:
            self.__currentLobbySettingsVisibility[element] = value

    def getBattleSettings(self):
        settings = getBattleSettings(self.__lessonId)
        return (settings.visiblePanels, settings.hiddenPanels)

    def getBattleRibbonsSettings(self):
        return getBattleSettings(self.__lessonId).ribbons

    def getBattleLoadingPages(self):
        return getBattleSettings(self.__lessonId).lessonPages

    def getIntroVideoData(self):
        return self.__currentState.getIntroVideoData() if self.__currentState else {}

    def getUI(self):
        return self.__gui

    def setHangarSpace(self, hangarSpace, hangarSpacePremium):
        from gui.ClientHangarSpace import g_clientHangarSpaceOverride
        g_clientHangarSpaceOverride.setPath(hangarSpacePremium, True, False)
        g_clientHangarSpaceOverride.setPath(hangarSpace, False, False)

    def setBootcampHangarSpace(self):
        BigWorld.wgUpdateTerrainBorders((-127, -237, -37, -157))
        self.setHangarSpace(self.__hangarSpace, self.__hangarSpacePremium)

    def setDefaultHangarSpace(self):
        self.setHangarSpace(None, None)
        return

    def changeNation(self, tankId, removedCallback):
        self.__nation = tankId
        self.__nationWindowRemovedCallback = removedCallback
        from gui.Scaleform.Waiting import Waiting
        Waiting.show('sinhronize')
        self.__account.base.changeBootcampLessonBonus(tankId)
        g_playerEvents.onClientUpdated += self.onNationChanged

    def onNationChanged(self, diff, updateOnlyLobbyCtx):
        g_playerEvents.onClientUpdated -= self.onNationChanged
        from gui.Scaleform.Waiting import Waiting
        Waiting.hide('sinhronize')
        if self.__nationWindowRemovedCallback is not None:
            self.__nationWindowRemovedCallback()
            self.__nationWindowRemovedCallback = None
        return

    def disableContextMenuItems(self, options, info=None):
        for option in options:
            if option['id'] == 'equip' and self.isResearchFreeLesson():
                continue
            initData = option.get('initData', None)
            if initData is not None:
                isEnabled = initData.get('enabled', False)
                if isEnabled:
                    initData['enabled'] = False
            option['initData'] = {}
            option['initData']['enabled'] = False

        return

    def getBonuses(self):
        return self.__bonuses

    @property
    def nation(self):
        return self.__nation

    def getNationData(self):
        return self.__nationsData[self.__nation]

    def isMarkerLittlePiercingEnabled(self):
        return self.__context.get('little_pierced', False)

    def getPredefinedPiercingPower(self):
        return self.__context.get('piercingPower', None)

    def isLittlePiercingDisabledModules(self, armor):
        return armor in (10, 15, 20)

    def checkLittlePiercingVehicle(self, entity):
        return entity.typeDescriptor.name == self.__context['little_pierced_vehicle']

    def isInGarageState(self):
        return self.__currentState.id() == STATE.IN_GARAGE

    def isResearchFreeLesson(self):
        return self.getLessonNum() >= self.getContextIntParameter('researchFreeLesson')

    def checkBigConsumablesIconsLesson(self):
        return self.__lessonId == self.getContextIntParameter('researchSecondVehicleLesson')

    def getBattleStatsLesson(self):
        return self.__context.get('battleStats', [])

    def setBootcampParams(self, params):
        self.__p.update(params)

    def getParameters(self):
        return self.__p


g_bootcamp = Bootcamp()
