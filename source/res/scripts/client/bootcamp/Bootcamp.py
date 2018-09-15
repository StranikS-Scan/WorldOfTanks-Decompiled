# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/Bootcamp.py
import BigWorld
import base64
import cPickle
import BattleReplay
import TriggersManager
import SoundGroups
import MusicControllerWWISE as MC
from account_helpers.AccountSettings import CURRENT_VEHICLE, AccountSettings
from account_helpers.settings_core import ISettingsCore
from adisp import process, async
from debug_utils import LOG_CURRENT_EXCEPTION
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP, LOG_ERROR_BOOTCAMP
from PlayerEvents import g_playerEvents
from bootcamp_shared import BOOTCAMP_BATTLE_ACTION
from gui import makeHtmlString
from gui.app_loader import g_appLoader
from gui.prb_control.dispatcher import g_prbLoader
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.login.EULADispatcher import EULADispatcher
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.prb_control import prbEntityProperty
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.battle_control.arena_info import player_format
from helpers import dependency, aop, i18n
from .BootcampGUI import BootcampGUI
from .BootcampReplayController import BootcampReplayController
from .BootcampConstants import BOOTCAMP_BATTLE_RESULT_MESSAGE
from .BootCampEvents import g_bootcampEvents
from .BootcampContext import Chapter
from .BootcampTransition import BootcampTransition
from .BootcampPreferences import BootcampPreferences
from .BootcampSettings import getBattleSettings, getGarageDefaults
from .ReloadLobbyHelper import ReloadLobbyHelper
from .states import STATE
from .states.StateInGarage import StateInGarage
from .states.StateInitial import StateInitial
from .states.StateOutroVideo import StateOutroVideo
from .states.StateResultScreen import StateResultScreen
from .aop.common import weave
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_session import IBattleSessionProvider
from collections import namedtuple
DISABLED_TANK_LEVELS = (1,)

class _BCNameFormatter(player_format.PlayerFullNameFormatter):

    @staticmethod
    def _normalizePlayerName(name):
        msgid = '#bootcamp:{0}'.format(name)
        locname = i18n.makeString(msgid)
        if locname != msgid:
            name = locname
        return name


_BattleResults = namedtuple('_BattleResults', ('type', 'typeStr'))

class BOOTCAMP_LESSON(object):
    BATTLE = 0
    GARAGE = 1


class Bootcamp(EventSystemEntity):
    settingsCore = dependency.descriptor(ISettingsCore)
    connectionMgr = dependency.descriptor(IConnectionManager)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
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
        self.__battleResults = None
        self.__hangarSpace = None
        self.__hangarSpacePremium = None
        self.__bonuses = None
        self.__isIntroVideoPlayed = False
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
        self.__minimapSize = 0.0
        self.__p = {'manualStart': False,
         'finished': False}
        self.__weaver = aop.Weaver()
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
        from gui.battle_results.components.common import makeRegularFinishResultLabel
        from gui.battle_results.settings import PLAYER_TEAM_RESULT
        if not resultType:
            teamResult = PLAYER_TEAM_RESULT.DRAW
        elif resultType == BOOTCAMP_BATTLE_RESULT_MESSAGE.VICTORY:
            teamResult = PLAYER_TEAM_RESULT.WIN
        else:
            teamResult = PLAYER_TEAM_RESULT.DEFEAT
        self.__battleResults = _BattleResults(resultType, makeHtmlString('html_templates:bootcamp/battle_results', teamResult))

    def getBattleResults(self):
        return self.__battleResults

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
        return self.__isSniperModeUsed

    def setSniperModeUsed(self, value):
        """
        Set sniper mode used flag, used to set max zoom once
        Must be used only in StateInBattle.py
        
        :param value: sniper mode current state
        """
        self.__isSniperModeUsed = value

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
        autoStartBattle = isRelogin or BattleReplay.isPlaying()
        if not autoStartBattle:
            self.showActionWaitWindow()
            yield self.settingsCore.serverSettings.settingsCache.update()
            self.settingsCore.serverSettings.applySettings()
            self.__preferences = BootcampPreferences()
            isNewbie = False
            if ctx['isNewbie'] and not ctx['completed'] and ctx['runCount'] == 1:
                isNewbie = True
            self.__preferences.setup(isNewbie)
            self.hideActionWaitWindow()
            eula = EULADispatcher()
            yield eula.processLicense()
            eula.fini()
        self.__running = True
        self.__lessonId = lessonNum
        self.__lessonType = BOOTCAMP_LESSON.BATTLE if isBattleLesson else BOOTCAMP_LESSON.GARAGE
        if (lessonNum == 0 or not isBattleLesson) and not autoStartBattle:
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
        weave(self.__weaver)
        from BootcampGarage import g_bootcampGarage
        g_bootcampGarage.initSubscriptions()
        g_bootcampEvents.onBootcampStarted()
        if not autoStartBattle:
            if isBattleLesson:
                g_prbLoader.createBattleDispatcher()
                g_prbLoader.setEnabled(True)
                self.enqueueBattleLesson()
            else:
                self.showActionWaitWindow()
                yield self.nextFrame()
                self.__currentState = StateInGarage(self.__lessonId, self.__account, self.__checkpoint)
                ReloadLobbyHelper().reload()
                self.hideActionWaitWindow()
                self.__currentState.activate()
        else:
            from states.StateBattlePreparing import StateBattlePreparing
            self.__currentState = StateBattlePreparing(self.__lessonId, BigWorld.player())
            self.__currentState.activate()
        BigWorld.overloadBorders(True)
        if self.__chapter is None:
            self.__chapter = Chapter()
        if self.__gui is None:
            self.__gui = BootcampGUI()
        for bankName in self.BOOTCAMP_SOUND_BANKS:
            SoundGroups.g_instance.loadSoundBank(bankName)

        self.sessionProvider.getCtx().setPlayerFullNameFormatter(_BCNameFormatter())
        return

    def stop(self, reason):
        g_bootcampEvents.onBootcampFinished()
        self.__weaver.clear()
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
        self.sessionProvider.getCtx().resetPlayerFullNameFormatter()
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
        if self.__currentState.skipBootcamp:
            self.requestBootcampFinishFromBattle = True
            self.sessionProvider.exit()
        else:
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
        if actionId == BOOTCAMP_BATTLE_ACTION.PLAYER_OBSERVED_ACTION:
            if actionArgs[0] == 1:
                TriggersManager.g_manager.activateTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_OBSERVED)
            else:
                TriggersManager.g_manager.deactivateTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_OBSERVED)
        else:
            g_bootcampEvents.onBattleAction(actionId, actionArgs)
            self.__currentState.onBattleAction(actionId, actionArgs)

    def isInBattleResultState(self):
        return isinstance(self.__currentState, StateResultScreen)

    def onResultScreenFinished(self):
        self.__currentState.deactivate()
        isVictory = self.__battleResults.type == BOOTCAMP_BATTLE_RESULT_MESSAGE.VICTORY
        if self.__lessonId == 0:
            if not isVictory:
                g_prbLoader.createBattleDispatcher()
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
        MC.g_musicController.muteMusic(True)
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
        BigWorld.updateTerrainBorders((-127, -237, -37, -157))
        self.setHangarSpace(self.__hangarSpace, self.__hangarSpacePremium)

    def setDefaultHangarSpace(self):
        self.setHangarSpace(None, None)
        return

    def changeNation(self, nationIndex, removedCallback):
        self.__nation = nationIndex
        self.__nationWindowRemovedCallback = removedCallback
        Waiting.show('sinhronize')
        self.__account.base.changeBootcampLessonBonus(nationIndex)
        g_playerEvents.onClientUpdated += self.onNationChanged

    def onNationChanged(self, _, __):
        g_playerEvents.onClientUpdated -= self.onNationChanged
        Waiting.hide('sinhronize')
        if self.__nationWindowRemovedCallback is not None:
            self.__nationWindowRemovedCallback()
            self.__nationWindowRemovedCallback = None
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

    def addPointcut(self, pointcut, *args, **kwargs):
        """ Manually add a pointcut to the common Bootcamp weaver.
            This pointcut can then be removed manually by the returned index.
            Otherwise, it will be removed automatically when leaving Bootcamp for any reason.
        
        :param pointcut: pointcut class or object to add
        :param args: (optional) extra arguments for pointcut class constructor
        :param kwargs: (optional) extra arguments for pointcut class constructor, or for aop.Weaver.weave
        :return: index of the added pointcut - can be used to manually remove it later
        """
        return self.__weaver.weave(pointcut=pointcut, *args, **kwargs)

    def removePointcut(self, pointcutIndex):
        """ Manually remove a pointcut previously added with addPointcut.
        
        :param pointcutIndex: index of the pointcut to remove (ignored if None)
        """
        if pointcutIndex is not None:
            self.__weaver.clear(pointcutIndex)
        return


g_bootcamp = Bootcamp()
