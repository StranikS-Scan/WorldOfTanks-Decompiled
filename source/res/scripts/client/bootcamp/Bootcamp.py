# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/Bootcamp.py
import base64
import cPickle
from collections import namedtuple
import BigWorld
import BattleReplay
import TriggersManager
import WWISE
import MusicControllerWWISE as MC
from constants import PREMIUM_ENTITLEMENTS, SPA_ATTRS, BootcampVersion
from gui.game_loading.resources.consts import Milestones
from realm import CURRENT_REALM
from account_helpers.AccountSettings import AccountSettings
from account_helpers.settings_core.settings_constants import BATTLE_EVENTS
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core import ISettingsCore
from account_helpers.counter_settings import dropCounters as dropNewSettingsCounters
from adisp import adisp_process, adisp_async
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP, LOG_ERROR_BOOTCAMP
from PlayerEvents import g_playerEvents
from bootcamp_shared import BOOTCAMP_BATTLE_ACTION
from gui import makeHtmlString
from gui.ClientHangarSpace import g_clientHangarSpaceOverride
from gui.Scaleform.daapi.view.lobby.referral_program.referral_program_helpers import isReferralProgramEnabled, isCurrentUserRecruit
from gui.prb_control.dispatcher import g_prbLoader
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.login.EULADispatcher import EULADispatcher
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.prb_control import prbEntityProperty
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.event_dispatcher import showInterludeVideoWindow
from gui.battle_control.arena_info import player_format
from helpers import dependency, aop, i18n
from items import vehicles, ITEM_TYPE_NAMES
from items.customizations import getBootcampOutfit
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IBootcampController, IDemoAccCompletionController
from skeletons.gui.shared import IItemsCache
from skeletons.tutorial import ITutorialLoader
from vehicle_outfit.outfit import Outfit
from .BootcampGUI import BootcampGUI
from .BootcampReplayController import BootcampReplayController
from .BootcampConstants import BOOTCAMP_BATTLE_RESULT_MESSAGE
from .BootCampEvents import g_bootcampEvents
from .BootcampSettings import getBattleSettings
from .BootcampGarageLessons import GarageLessons
from .ReloadLobbyHelper import ReloadLobbyHelper
from .states import STATE
from .states.StateInGarage import StateInGarage
from .states.StateInitial import StateInitial
from .states.StateResultScreen import StateResultScreen
from .aop.common import weave
from . import GAME_SETTINGS_NEWBIE, GAME_SETTINGS_COMMON
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


class BOOTCAMP_SOUND(object):
    NEW_UI_ELEMENT_SOUND = 'bc_new_ui_element_button'


class BOOTCAMP_UI_COMPONENTS(object):
    START_BATTLE_BUTTON = 'StartBattleButton'
    WELCOME_START_BATTLE_BUTTON = 'WelcomeStartBattleButton'


class Bootcamp(EventSystemEntity):
    settingsCore = dependency.descriptor(ISettingsCore)
    connectionMgr = dependency.descriptor(IConnectionManager)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    itemsCache = dependency.descriptor(IItemsCache)
    appLoader = dependency.descriptor(IAppLoader)
    bootcampController = dependency.descriptor(IBootcampController)
    demoAccController = dependency.descriptor(IDemoAccCompletionController)
    tutorialLoader = dependency.descriptor(ITutorialLoader)

    def __init__(self):
        super(Bootcamp, self).__init__()
        self.__currentState = StateInitial()
        self.__running = False
        self.__account = None
        self.__avatar = None
        self.__lessonId = 0
        self.__isRecruit = False
        self.__isBattleLesson = False
        self.__context = {}
        self.__gui = None
        self.__arenaUniqueID = None
        self.__lobbyReloader = ReloadLobbyHelper()
        self.__battleResults = None
        self.__hangarSpace = None
        self.__hangarSpacePremium = None
        self.__bonuses = None
        self.__isIntroVideoPlayed = False
        self.__requestBootcampFinishFromBattle = False
        self.__isSniperModeUsed = False
        self.__version = BootcampVersion.DEFAULT
        self.__showingWaitingActionWindow = False
        self.__nation = 0
        self.__nationsData = {}
        self.__nationsOrder = {'realm': {},
         'country': {}}
        self.__customizationData = {}
        self.__checkpoint = ''
        self.__replayController = None
        self.__minimapSize = 0.0
        self.__garageLessons = GarageLessons()
        self.__p = {'manualStart': False,
         'finished': False}
        self.__weaver = aop.Weaver()
        return

    @adisp_async
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
        self.__lobbyReloader.cancel()
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

    def getCheckpoint(self):
        return self.__checkpoint

    def getVersion(self):
        return self.__version

    def isLastLesson(self, lesson):
        return self.getContextIntParameter('lastLessonNum') == lesson

    def saveCheckpoint(self, checkpoint):
        self.__checkpoint = checkpoint
        if self.__account is not None:
            self.__account.base.saveBootcampCheckpoint(self.__checkpoint, self.__lessonId)
        return

    def setBattleResults(self, arenaUniqueID, resultType, resultReason):
        self.__arenaUniqueID = arenaUniqueID
        from gui.battle_results.br_constants import PlayerTeamResult
        if not resultType:
            teamResult = PlayerTeamResult.DRAW
        elif resultType == BOOTCAMP_BATTLE_RESULT_MESSAGE.VICTORY:
            teamResult = PlayerTeamResult.WIN
        else:
            teamResult = PlayerTeamResult.DEFEAT
        self.__battleResults = _BattleResults(resultType, makeHtmlString('html_templates:bootcamp/battle_results', teamResult))

    def getBattleResults(self):
        return self.__battleResults

    def getBattleResultsExtra(self, lessonId):
        return self.__garageLessons.getBattleResult(lessonId)

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
        self.__isSniperModeUsed = value

    @adisp_process
    def start(self, lessonNum, isBattleLesson):
        LOG_DEBUG_DEV_BOOTCAMP('Starting bootcamp', lessonNum, isBattleLesson)
        if BattleReplay.g_replayCtrl.isPlaying:
            self.__replayController = BootcampReplayController()
            self.__replayController.init()
        g_bootcampEvents.onInterludeVideoStarted += self.onInterludeVideoStarted
        g_bootcampEvents.onBattleLessonFinished += self.onBattleLessonFinished
        g_bootcampEvents.onGarageLessonFinished += self.onGarageLessonFinished
        g_bootcampEvents.onBattleLoaded += self.onBattleLoaded
        g_bootcampEvents.onResultScreenFinished += self.onResultScreenFinished
        g_bootcampEvents.onRequestBootcampFinish += self.onRequestBootcampFinish
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
            isNewbie = False
            if ctx['isNewbieSettings'] and not ctx['completed']:
                isNewbie = True
            self.__setupPreferences(isNewbie)
            self.hideActionWaitWindow()
            eula = EULADispatcher()
            yield eula.processLicense()
            eula.fini()
        self.__running = True
        self.__lessonId = lessonNum
        self.__lessonType = BOOTCAMP_LESSON.BATTLE if isBattleLesson else BOOTCAMP_LESSON.GARAGE
        if (lessonNum == 0 or not isBattleLesson) and not autoStartBattle:
            self.showActionWaitWindow()
            yield self.itemsCache.update(CACHE_SYNC_REASON.SHOW_GUI)
            self.__isRecruit = isCurrentUserRecruit()
            self.hideActionWaitWindow()
        if self.__currentState is not None:
            self.__currentState.deactivate()
        self.__hangarSpace = ctx['hangarSpace']
        self.__hangarSpacePremium = ctx['hangarSpacePremium']
        self.__bonuses = ctx['bonuses']
        self.__version = ctx['version']
        showRewards = ctx['needAwarding']
        lastBattleLesson = self.getContextIntParameter('lastLessonNum') - 1
        if 0 <= lastBattleLesson < len(self.__bonuses['battle']):
            self.__bonuses['battle'][lastBattleLesson]['showRewards'] = showRewards
        self.__nation = ctx['nation']
        self.__nationsData = ctx['nationsData']
        self.__nationsOrder = ctx.get('nations_order')
        self.__p['completed'] = ctx['completed']
        self.__p['needAwarding'] = ctx['needAwarding']
        self.__customizationData = ctx.get('customization', {})
        weave(self.__weaver)
        if AccountSettings.isCleanPC():
            dropNewSettingsCounters()
        g_bootcampEvents.onBootcampStarted()
        if not autoStartBattle:
            if isBattleLesson and not self.demoAccController.isInDemoAccRegistration:
                g_prbLoader.createBattleDispatcher()
                g_prbLoader.setEnabled(True)
                self.enqueueBattleLesson()
            else:
                self.showActionWaitWindow()
                yield self.nextFrame()
                self.__currentState = StateInGarage()
                self.__lobbyReloader.reload()
                self.hideActionWaitWindow()
                self.__currentState.activate()
        else:
            from states.StateBattlePreparing import StateBattlePreparing
            self.__currentState = StateBattlePreparing(self.__lessonId, BigWorld.player())
            self.__currentState.activate()
        BigWorld.overloadBorders(True)
        if self.__gui is None:
            self.__gui = BootcampGUI()
        WWISE.activateRemapping('bootcamp')
        self.sessionProvider.getCtx().setPlayerFullNameFormatter(_BCNameFormatter())
        return

    def isNewbie(self):
        ctx = self.getContext()
        return True if ctx['isNewbieSettings'] and not ctx['completed'] else False

    def stop(self, reason):
        g_bootcampEvents.onBootcampFinished()
        self.__weaver.clear()
        BigWorld.overloadBorders(False)
        if self.__gui is not None:
            self.__gui.clear()
            self.__gui = None
        g_bootcampEvents.onInterludeVideoStarted -= self.onInterludeVideoStarted
        g_bootcampEvents.onBattleLessonFinished -= self.onBattleLessonFinished
        g_bootcampEvents.onGarageLessonFinished -= self.onGarageLessonFinished
        g_bootcampEvents.onBattleLoaded -= self.onBattleLoaded
        g_bootcampEvents.onResultScreenFinished -= self.onResultScreenFinished
        g_bootcampEvents.onRequestBootcampFinish -= self.onRequestBootcampFinish
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__onAvatarBecomeNonPlayer
        g_playerEvents.onArenaCreated -= self.__onArenaCreated
        self.connectionMgr.onDisconnected -= self.__cm_onDisconnected
        if self.__running:
            self.__running = False
        if self.__currentState:
            self.__currentState.deactivate()
        self.__currentState = StateInitial()
        self.__account = None
        self.__context = {}
        self.__isIntroVideoPlayed = False
        if self.__replayController is not None:
            self.__replayController.fini()
            self.__replayController = None
        MC.g_musicController.stopAmbient(True)
        WWISE.deactivateRemapping('bootcamp')
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

    def getGUI(self):
        return self.__gui

    def getBootcampOutfit(self, vehDescr):
        return Outfit(vehicleCD=vehDescr.makeCompactDescr(), component=getBootcampOutfit(vehDescr, self.__customizationData)) if vehDescr.name in self.__customizationData and self.isRunning() else None

    @property
    def replayCtrl(self):
        return self.__replayController

    @prbEntityProperty
    def prbEntity(self):
        pass

    def showActionWaitWindow(self):
        if not self.__showingWaitingActionWindow:
            self.__showingWaitingActionWindow = True
            g_playerEvents.onLoadingMilestoneReached(Milestones.SYNCHRONIZE)
            Waiting.show('synchronize')

    def hideActionWaitWindow(self):
        if self.__showingWaitingActionWindow:
            self.__showingWaitingActionWindow = False
            Waiting.hide('synchronize')

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
            self.__currentState = StateInBattle(lessonId, self.__avatar)
            self.__currentState.activate()

    def onBattleLessonFinished(self, lessonId, lessonResults):
        self.__lessonId = lessonId
        self.__currentState.deactivate()
        MC.g_musicController.stop()
        if self.requestBootcampFinishFromBattle:
            if self.demoAccController.isDemoAccount:
                self.demoAccController.isInDemoAccRegistration = True
                self.__currentState = StateInGarage()
                self.__currentState.activate()
            else:
                self.onRequestBootcampFinish()
        else:
            self.__currentState = StateResultScreen(lessonResults)
            self.__currentState.activate()

    def onInterludeVideoStarted(self, index):
        messageVO = self.getInterludeVideoPageData(index)
        player = BigWorld.player()
        if not player.spaFlags.getFlag(SPA_ATTRS.BOOTCAMP_VIDEO_DISABLED) and messageVO:
            showInterludeVideoWindow(messageVO=messageVO)

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

    def isInBattleResultState(self):
        return isinstance(self.__currentState, StateResultScreen)

    def onResultScreenFinished(self):
        self.__currentState.deactivate()
        isVictory = self.__battleResults.type == BOOTCAMP_BATTLE_RESULT_MESSAGE.VICTORY
        if self.__lessonId == 0:
            if not isVictory:
                g_prbLoader.createBattleDispatcher()
                g_prbLoader.setEnabled(True)
                self.appLoader.showLobby()
                self.__currentState = StateInitial()
                self.enqueueBattleLesson()
            else:
                self.__currentState = StateInGarage()
        else:
            self.__currentState = StateInGarage()
        self.__currentState.activate()

    def enqueueBattleLesson(self):
        if self.prbEntity is not None:
            self.prbEntity.doAction()
        return

    def onGarageLessonFinished(self, lessonId):
        LOG_DEBUG_DEV_BOOTCAMP('onGarageLessonFinished', lessonId)
        self.__account.base.completeBootcampLesson()
        lastLesson = self.getContextIntParameter('lastLessonNum')
        if self.__lessonId == lastLesson:
            LOG_DEBUG_DEV_BOOTCAMP('Finished last lesson', lessonId)
        else:
            self.enqueueBattleLesson()
        functional = self.tutorialLoader.tutorial.getChapterFunctionalContext()
        functional.stopVSEPlans()

    def onRequestBootcampFinish(self):
        LOG_DEBUG_DEV_BOOTCAMP('onRequestBootcampFinish')
        self.__account.base.requestBootcampQuit()

    def finishBootcamp(self):
        LOG_DEBUG_DEV_BOOTCAMP('finishBootcamp', self.__currentState.id())
        self.finishFromGarageLesson()
        self.setContext({})
        self.setAccount(None)
        return

    def finishFromGarageLesson(self):
        self.__running = False
        self.setDefaultHangarSpace()
        self.stop(0)
        self.__lobbyReloader.reload()

    def getBattleSettings(self):
        settings = getBattleSettings(self.__lessonId)
        return (settings.visiblePanels, settings.hiddenPanels)

    def getBattleRibbonsSettings(self):
        return getBattleSettings(self.__lessonId).ribbons

    def getBattleLoadingPages(self):
        return getBattleSettings(self.__lessonId).lessonPages

    def getInterludeVideoPageData(self, index):
        messageVO = {}
        if self.__lessonId:
            extraData = self.getBattleResultsExtra(self.__lessonId - 1)
            if extraData['videos']:
                video = extraData['videos'][index]
                messageVO['messages'] = [video['messages']]
                messageVO['voiceovers'] = [ voiceover for voiceover in video['voiceovers'] ]
                messageVO['exitEvent'] = g_bootcampEvents.onInterludeVideoFinished
        return messageVO

    def getInterludeVideoButtons(self):
        if self.__lessonId:
            extraData = self.getBattleResultsExtra(self.__lessonId - 1)
            if extraData['videos']:
                return [ {'image': video['messages']['icon']} for video in extraData['videos'] ]
        return []

    def getIntroPageData(self, isChoice=False, isInProgress=False):
        if isChoice:
            self.__lessonId = 1 if isInProgress else 0
        parameters = self.getParameters()
        autoStart = parameters.get('introAutoStart', False)
        if BattleReplay.isPlaying():
            autoStart = True
        introPageData = {'autoStart': autoStart,
         'lessonNumber': self.__lessonId,
         'tutorialPages': self.getBattleLoadingPages(),
         'showSkipOption': True,
         'isReferralEnabled': self.isReferralEnabled(),
         'isChoice': isChoice}
        return introPageData

    def getIntroVideoData(self):
        if self.__currentState:
            introVideoPageData = self.getIntroPageData()
            introVideoPageData.update(self.__currentState.getIntroVideoData())
            return introVideoPageData
        return {}

    def getUI(self):
        return self.__gui

    def setHangarSpace(self, hangarSpace, hangarSpacePremium):
        g_clientHangarSpaceOverride.setPath(hangarSpacePremium, isPremium=True, isReload=False)
        g_clientHangarSpaceOverride.setPath(hangarSpace, isPremium=False, isReload=False)

    def setBootcampHangarSpace(self):
        BigWorld.updateTerrainBorders((-127, -237, -37, -157))
        self.setHangarSpace(self.__hangarSpace, self.__hangarSpacePremium)

    def setDefaultHangarSpace(self):
        self.setHangarSpace(None, None)
        return

    def previewNation(self, nationIndex):
        if nationIndex in self.__nationsData:
            nationData = self.__nationsData[nationIndex]
            vehicleFirstID = nationData['vehicle_first']
            vehicle = self.itemsCache.items.getVehicles()[vehicleFirstID]
            self.installModules(nationData, 'vehicle_first', vehicle.descriptor)
            outfit = self.getBootcampOutfit(vehicle.descriptor)
            g_clientHangarSpaceOverride.hangarSpace.startToUpdateVehicle(vehicle, outfit=outfit)
        else:
            LOG_ERROR_BOOTCAMP('Wrong nation index: {}'.format(nationIndex))

    @staticmethod
    def installModules(nationData, sectionName, vehicleDescr):
        if 'equip' in nationData and sectionName in nationData['equip']:
            equipIds = nationData['equip'][sectionName].split(':')
            for equipId in equipIds:
                intEquipId = int(equipId)
                if vehicleDescr.mayInstallComponent(intEquipId):
                    itemTypeIdx, _, compID = vehicles.parseIntCompactDescr(intEquipId)
                    if ITEM_TYPE_NAMES[itemTypeIdx] == 'vehicleTurret':
                        vehicleDescr.installTurret(intEquipId, 0)
                    else:
                        if ITEM_TYPE_NAMES[itemTypeIdx] == 'vehicleGun':
                            turretDescr, _ = vehicleDescr.turrets[0]
                            if not [ True for gun in turretDescr.guns if gun.id[1] == compID ]:
                                LOG_ERROR_BOOTCAMP('Can not install gun {} for turret {}'.format(intEquipId, turretDescr.compactDescr))
                                continue
                        vehicleDescr.installComponent(intEquipId)
                LOG_ERROR_BOOTCAMP('Can not install module', intEquipId)

    def changeNation(self, nationIndex):
        self.__nation = nationIndex
        Waiting.show('synchronize')
        self.__account.base.changeBootcampLessonBonus(nationIndex)
        g_playerEvents.onClientUpdated += self.onNationChanged

    def onNationChanged(self, _, __):
        g_playerEvents.onClientUpdated -= self.onNationChanged
        Waiting.hide('synchronize')

    def getBonuses(self):
        return self.__bonuses

    def getPremiumType(self):
        if self.__bonuses is None:
            return
        else:
            lastBattleField = 'last_battle_short' if self.__version == BootcampVersion.SHORT else 'last_battle'
            bonuses = self.__bonuses[lastBattleField]['bonus']
            for premiumType in PREMIUM_ENTITLEMENTS.ALL_TYPES:
                if premiumType in bonuses:
                    return premiumType

            return

    @property
    def nation(self):
        return self.__nation

    def getNationsOrder(self, *fields):
        userCountry = BigWorld.player().spaFlags.getFlag(SPA_ATTRS.USER_COUNTRY)
        realm = CURRENT_REALM if CURRENT_REALM in self.__nationsOrder else 'DEFAULT'
        realmConfig = self.__nationsOrder.get(realm, {})
        if userCountry in realmConfig:
            nationOrder = realmConfig.get(userCountry, {})
        else:
            nationOrder = realmConfig.get('DEFAULT', {})
        return [ nationOrder.get(field, []) for field in fields ]

    def getNationData(self, nation=None):
        return self.__nationsData.get(self.__nation if nation is None else nation, {})

    def isReferralEnabled(self):
        return isReferralProgramEnabled() and self.__isRecruit

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

    def isEnableCriticalDamageIcon(self):
        return self.getLessonNum() >= self.getContextIntParameter('enableDamageIconLesson')

    def checkBigConsumablesIconsLesson(self):
        return self.__lessonId == self.getContextIntParameter('researchSecondVehicleLesson')

    def getBattleStatsLessonWin(self):
        return self.__context.get('battleStatsWin', [])

    def getBattleStatsLessonDefeat(self):
        return self.__context.get('battleStatsDefeat', [])

    def setBootcampParams(self, params):
        self.__p.update(params)

    def getParameters(self):
        return self.__p

    def addPointcut(self, pointcut, *args, **kwargs):
        return self.__weaver.weave(pointcut=pointcut, *args, **kwargs)

    def removePointcut(self, pointcutIndex):
        if pointcutIndex is not None:
            self.__weaver.clear(pointcutIndex)
        return

    def __setupPreferences(self, isNewbie):
        if isNewbie:
            self.settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.BATTLE_EVENTS, {setting:True for _, setting in BATTLE_EVENTS.getIterator()})
            settingsTemplate = GAME_SETTINGS_NEWBIE
        else:
            settingsTemplate = GAME_SETTINGS_COMMON
        settings = {}
        for k, v in settingsTemplate.iteritems():
            i = k.find(':')
            if i > -1:
                settings.setdefault(k[:i], {})[k[i + 1:]] = v
            settings[k] = v

        self.settingsCore.applySettings(settings)
        self.settingsCore.confirmChanges(self.settingsCore.applyStorages(restartApproved=False))
        self.settingsCore.clearStorages()


g_bootcamp = Bootcamp()
