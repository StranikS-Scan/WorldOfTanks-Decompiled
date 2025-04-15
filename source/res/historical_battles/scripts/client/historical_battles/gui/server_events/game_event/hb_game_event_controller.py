# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/game_event/hb_game_event_controller.py
import BigWorld
import time
from math import ceil
from historical_battles.skeletons.gui.customizable_objects_manager import ICustomizableObjectsManager
from shared_utils import first
from functools import partial
import typing
import logging
from items import vehicles
from adisp import adisp_process
from skeletons.gui.game_control import IHangarSpaceSwitchController
from wotdecorators import condition
from Event import Event, EventManager
from constants import EVENT_CLIENT_DATA, RESTRICTION_TYPE, FAIRPLAY_VIOLATIONS
from frameworks.wulf.gui_constants import WindowLayer
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.system_messages import ISystemMessages
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CURRENT_VEHICLE
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbackDelayer
from historical_battles.gui.gui_constants import SCH_CLIENT_MSG_TYPE
from PlayerEvents import g_extPlayerEvents, g_playerEvents
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.app_loader.settings import APP_NAME_SPACE
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.utils.performance_analyzer import PerformanceAnalyzerMixin
from gui.shared.utils.scheduled_notifications import AcyclicNotifier, Notifiable
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.events import FullscreenModeSelectorEvent
from gui.clans.clan_cache import g_clanCache
from gui.Scaleform.Waiting import Waiting
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from historical_battles.gui.impl.lobby.hb_helpers.hangar_helpers import closeEvent
from historical_battles.gui.server_events.game_event.front_progress import FrontsProgressController
from historical_battles.gui.server_events.game_event.hero_tank import HBHeroTankController
from historical_battles.gui.sounds.sound_progression_controller import HBSoundProgressionController
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from historical_battles_common.hb_constants import HB_GAME_PARAMS_KEY
from historical_battles_common.hb_constants_extension import PREBATTLE_TYPE, QUEUE_TYPE, ARENA_BONUS_TYPE
from historical_battles.gui.prb_control.prb_config import FUNCTIONAL_FLAG
from historical_battles.gui.shared.event_dispatcher import showHBFairplayDialog, showHBFairplayWarningDialog
from historical_battles.gui.shared.hb_events import DioramaVehicleEvent
from historical_battles.gui.prb_control.prb_config import PREBATTLE_ACTION_NAME
from historical_battles.gui.close_event_confirmator import CloseEventConfirmator
from historical_battles.settings import HBConfig
from historical_battles.gui.impl.lobby.division_upgrade_rewards_view import DivisionUpgradeRewardsViewWindow
from historical_battles.gui.sounds.sound_hangar_controller import SoundHangarController
from historical_battles.hb_progression_narrative_config_reader import HBProgressionNarrativesReader
from historical_battles.skeletons.gui.hb_notifications_controller import IHBEventNotifications
from tutorial.control.context import GLOBAL_FLAG
from gui.shared.tutorial_helper import getTutorialGlobalStorage
if typing.TYPE_CHECKING:
    from HBCoinsComponent import HBCoinsComponent
    from HBFrontCouponsComponent import HBFrontCouponsComponent
    from HBAccountComponent import HBAccountComponent
    from historical_battles.hb_progression_narrative_config_reader import HBNarrativeConfig
_logger = logging.getLogger(__name__)
HB_CONFIG = 'historical_battles'
HB_NODE = 'historicalBattles'
DIVISIONS_EXP_NODE = 'divisionsEXP'

class HBGameEventController(PerformanceAnalyzerMixin, Notifiable, IGameEventController, IGlobalListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __appLoader = dependency.descriptor(IAppLoader)
    __hbProgression = dependency.descriptor(IHBProgressionOnTokensController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __customizationService = dependency.descriptor(ICustomizationService)
    __custObjMgr = dependency.descriptor(ICustomizableObjectsManager)
    __spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)
    __notificationsCtrl = dependency.descriptor(IHBEventNotifications)
    ifStarted = condition('_started')
    HB_VIOLATIONS = (FAIRPLAY_VIOLATIONS.HB_AFK, FAIRPLAY_VIOLATIONS.HB_DESERTER)

    def __init__(self):
        super(HBGameEventController, self).__init__()
        self._em = EventManager()
        self.onProgressChanged = Event(self._em)
        self.onQuestsUpdated = Event(self._em)
        self.onFrontTimeStatusUpdated = Event(self._em)
        self.onSelectedFrontChanged = Event(self._em)
        self.onSubdivisionLockChanged = Event(self._em)
        self.onGameParamsChanged = Event(self._em)
        self.onDisableFrontsWidget = Event(self._em)
        self.onDisableDivisionsWidget = Event(self._em)
        self.onLobbyHeaderUpdate = Event(self._em)
        self.onShowBattleQueueView = Event(self._em)
        self.onCloseAllAwardsWindow = Event(self._em)
        self.frontDataUpdated = Event(self._em)
        self.onDivisionsExpChanged = Event(self._em)
        self.onPrbEntityStateChanged = Event(self._em)
        self._started = False
        self.__hbConfig = HBConfig()
        self.__narrativesConfig = []
        self.__closeEventConfirmator = CloseEventConfirmator()
        self.__fronts = FrontsProgressController()
        self.__heroTank = HBHeroTankController()
        self.__soundProgressionCtrl = HBSoundProgressionController()
        self.__banTimer = CallbackDelayer()
        self.__progressionInited = False
        self.__isShowingProgressionView = False
        self.__banExpiryTime = None
        self.__prbIsSwitching = False
        self.__isInHB = False
        self.__frontsWidgetDisabled = False
        return

    def init(self):
        g_clientUpdateManager.addCallbacks({'eventsData.' + str(EVENT_CLIENT_DATA.QUEST): self.__onQuestsUpdated})
        g_eventBus.addListener(FullscreenModeSelectorEvent.NAME, self.__onFullScreenModeSelector)
        g_clientUpdateManager.addCallbacks({'stats.restrictions': self.__onRestrictionsChanged})
        if self.__soundProgressionCtrl:
            self.__soundProgressionCtrl.init()

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._em.clear()
        self.stop()
        self.__banTimer.clearCallbacks()
        self.__banTimer = None
        g_eventBus.removeListener(FullscreenModeSelectorEvent.NAME, self.__onFullScreenModeSelector, EVENT_BUS_SCOPE.GLOBAL)
        if self.prbDispatcher and self.prbDispatcher.hasListener(self):
            self.prbDispatcher.removeListener(self)
        if self.__soundProgressionCtrl:
            self.__soundProgressionCtrl.fini()
            self.__soundProgressionCtrl = None
        self.frontController.clearCache()
        return

    def start(self):
        if self._started:
            _logger.error('HBGameEventController already started')
            return
        self.__closeEventConfirmator.start()
        for container in self.__getContainers():
            container.start()

        self._started = True
        self.__fronts.onItemsUpdated += self.__onProgressChanged
        if self.frontCoupons:
            self.frontCoupons.onFrontCouponsUpdated += self.__onProgressChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged
        self.__itemsCache.onSyncCompleted += self.__onItemsSyncCompleted
        g_extPlayerEvents.onExtGetCustomPunishmentWindow += self.__onExtGetCustomPunishmentWindow
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        self.__hangarSpace.onVehicleChanged += self.__onVehicleLoaded
        self.__hangarSpace.onSpaceCreate += self.__onSpaceCreated
        self.__onProgressChanged()
        self.__addFrontStartTimeNotifiers()
        self.startNotification()
        self.__narrativesConfig = HBProgressionNarrativesReader.getNarrativesData()

    @ifStarted
    def stop(self):
        self.__closeEventConfirmator.stop()
        self.__banTimer.clearCallbacks()
        self.__banExpiryTime = None
        self.frontController.onItemsUpdated -= self.__onProgressChanged
        if self.frontCoupons:
            self.frontCoupons.onFrontCouponsUpdated -= self.__onProgressChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged
        self.__itemsCache.onSyncCompleted -= self.__onItemsSyncCompleted
        g_extPlayerEvents.onExtGetCustomPunishmentWindow -= self.__onExtGetCustomPunishmentWindow
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        self.__hangarSpace.onVehicleChanged -= self.__onVehicleLoaded
        self.__hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        for container in self.__getContainers():
            container.stop()

        self._started = False
        self.__progressionInited = False
        self.clearNotification()
        self.__narrativesConfig = None
        return

    def clear(self):
        self.stop()

    def onLobbyInited(self, event):
        super(HBGameEventController, self).onLobbyInited(event)
        if not self.prbDispatcher.hasListener(self):
            self.prbDispatcher.addListener(self)

    def onAccountBecomePlayer(self):
        super(HBGameEventController, self).onAccountBecomePlayer()
        self.__onSettingsChanged(self.__lobbyContext.getServerSettings().getSettings())

    def onDisconnected(self):
        self.__isInHB = False
        self.clear()
        super(HBGameEventController, self).onDisconnected()

    def onPrbEntitySwitching(self):
        switchedFromHB = self.isHistoricalBattlesMode()
        if switchedFromHB:
            self.__prbIsSwitching = True
            windowContainer = self.__appLoader.getApp(APP_NAME_SPACE.SF_LOBBY).containerManager.getContainer(WindowLayer.SUB_VIEW)
            self.__hideVehicleMarker()
            if windowContainer and not windowContainer.getAllLoadingViews():
                storedVehInvID = self.__getStoredVehInvID()
                if storedVehInvID:
                    g_currentVehicle.selectVehicle(storedVehInvID)
                    g_currentVehicle.refreshModel()
                else:
                    self.__hangarSpace.removeVehicle()
                    g_currentVehicle.selectNoVehicle()
                from gui.shared.event_dispatcher import showHangar
                showHangar()

    def onPrbEntitySwitched(self):
        if self.isHistoricalBattlesMode():
            self.__selectVehicle()
            if not self.__isInHB:
                self.__onHangarEntered()
            getTutorialGlobalStorage().setValue(GLOBAL_FLAG.HISTORICAL_BATTLES_ACTIVE, True)
        elif self.__prbIsSwitching:
            self.__onHangarExited()
            getTutorialGlobalStorage().setValue(GLOBAL_FLAG.HISTORICAL_BATTLES_ACTIVE, False)
        self.onPrbEntityStateChanged()
        self.__prbIsSwitching = False

    @adisp_process
    def switchPrb(self):
        if not self.isEnabled():
            return
        else:
            prbDispatcher = g_prbLoader.getDispatcher()
            if prbDispatcher is None:
                return
            entityType = prbDispatcher.getEntity().getEntityType()
            if entityType in QUEUE_TYPE.HB_RANGE:
                pass
            else:
                yield prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES))
            return

    @adisp_process
    def selectRandomMode(self):
        dispatcher = self.prbDispatcher
        if dispatcher is None:
            return
        else:
            yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
            return

    def updateFrontData(self, frontId=None, divisionID=None):
        if frontId is not None:
            self.frontController.setSelectedFrontID(frontId)
        if divisionID is not None:
            front = self.frontController.getSelectedFront()
            front.setSelectedSubdivisionID(divisionID)
        self.__selectVehicle()
        self.frontDataUpdated(frontId, divisionID)
        self.__spaceSwitchController.processPossibleSceneChange()
        return

    def updateVehicle(self):
        self.__selectVehicle()

    def isBattlesEnabled(self):
        return self.getGameEventData().get('isBattlesEnabled', False)

    def isHistoricalBattlesMode(self):
        if self.prbDispatcher is None:
            return False
        else:
            state = self.prbDispatcher.getFunctionalState()
            isInPreQueue = any((state.isInPreQueue(queueType) for queueType in QUEUE_TYPE.HB_RANGE))
            return state.isInUnit(PREBATTLE_TYPE.HISTORICAL_BATTLES) or isInPreQueue

    def isEnabled(self):
        return self.getGameEventData().get('isEnabled', False)

    def getGameEventData(self):
        return self.__hbConfig.asDict()

    def getEnvironmentSettings(self):
        return self.getGameEventData().get('hangarEnvironmentSettings', {})

    def getMainDiscount(self):
        return self.getGameEventData().get('mainDiscount', {})

    def isLastDay(self):
        return self.getEventFinishTimeLeft() < time_utils.ONE_DAY

    def isShowingProgressionView(self):
        return self.__isShowingProgressionView

    def isHBPrbActive(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.HISTORICAL_BATTLES)

    def getHoursLeft(self):
        return ceil(self.getEventFinishTimeLeft() / time_utils.ONE_HOUR)

    def getQuestsUpdateHoursLeft(self):
        secondsLeft = time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay()
        return ceil(secondsLeft / time_utils.ONE_HOUR)

    def getEventStartTime(self):
        return self.__getEventTime('startDate')

    def getEventFinishTime(self):
        return self.__getEventTime('endDate')

    def getEventFinishTimeLeft(self):
        finishTime = self.getEventFinishTime()
        return time_utils.getTimeDeltaFromNowInLocal(finishTime) if finishTime is not None else 0

    def setShowingProgressionView(self, isShow):
        self.__isShowingProgressionView = isShow

    def getSelectedSubdivisionVehicles(self):
        subdivision = self.frontController.getSelectedSubdivision()
        subdivisionTanks = subdivision.getTanksIntCDForCurrentProgressionLevel()
        return [ self.__itemsCache.items.getItemByCD(intCD) for intCD in subdivisionTanks ]

    def disableFrontsWidget(self, isDisabled):
        self.__frontsWidgetDisabled = isDisabled
        self.onDisableFrontsWidget(isDisabled)

    @property
    def frontsWidgetDisabled(self):
        return self.__frontsWidgetDisabled

    @property
    def coins(self):
        return getattr(BigWorld.player(), 'HBCoinsComponent', None)

    @property
    def account(self):
        return getattr(BigWorld.player(), 'HBAccountComponent', None)

    @property
    def frontCoupons(self):
        return getattr(BigWorld.player(), 'HBFrontCouponsComponent', None)

    @property
    def frontController(self):
        return self.__fronts

    @property
    def heroTank(self):
        return self.__heroTank

    @property
    def soundProgressionCtrl(self):
        return self.__soundProgressionCtrl

    @property
    def settings(self):
        return self.__lobbyContext.getServerSettings().getSettings().get(HB_GAME_PARAMS_KEY, {})

    @property
    def hbConfig(self):
        return self.__hbConfig

    @property
    def narrativesConfig(self):
        return self.__narrativesConfig

    @property
    def isBanned(self):
        return self.banDuration > 0

    @property
    def banDuration(self):
        return max(0, time_utils.getTimeDeltaFromNow(self.__banExpiryTime)) if self.__banExpiryTime is not None else 0

    @property
    def banExpiryTime(self):
        return self.__banExpiryTime

    def onDivisionLevelUp(self, divisionId, prevLvl, currLvl):
        subdivision = self.frontController.getSubdivisionById(divisionId)
        subdivisionTanks = [ tank.shortUserName for tank in subdivision.getTanksForCurrentProgressionLevel() ]
        divisionName = backport.text(R.strings.hb_lobby.dyn('division_{}'.format(divisionId)).name())
        divisionAbilities = subdivision.getAbilitiesData()
        unlockedAbilities = []
        equipmentsCache = vehicles.g_cache.equipments()
        for abilityId in divisionAbilities[prevLvl:currLvl]:
            abilityName = backport.text(R.strings.hb_artefacts.dyn(equipmentsCache[abilityId].name).name())
            unlockedAbilities.append(u'\xab{}\xbb'.format(abilityName))

        data = {'divisionName': divisionName,
         'divisionLevel': currLvl,
         'divisionVehicles': subdivisionTanks,
         'unlockedAbilities': unlockedAbilities}
        self.__notificationsCtrl.pushDivisionLevelUpSysMsg(data)
        window = DivisionUpgradeRewardsViewWindow(divisionId, prevLvl, currLvl)
        window.load()

    def __onExtGetCustomPunishmentWindow(self, ctx):
        messageCtx = ctx.get('messageCtx', {})
        violationName = messageCtx.get('violationName', '')
        if violationName not in self.HB_VIOLATIONS:
            return
        else:
            data = {'isStarted': self.__banExpiryTime is not None,
             'reason': violationName,
             'banExpiryTime': self.banExpiryTime}
            penaltyType = messageCtx.get('penaltyType', '')
            callback = None
            if penaltyType == 'penalty':
                if self.banDuration > 0:
                    callback = partial(showHBFairplayDialog, data)
                else:
                    callback = partial(showHBFairplayWarningDialog, violationName)
                    self.__notificationsCtrl.pushArenaPunishmentSysMsg(data, SCH_CLIENT_MSG_TYPE.HB_ARENA_WARNING_NOTIFICATIONS)
            elif penaltyType == 'warning':
                callback = partial(showHBFairplayWarningDialog, violationName)
                self.__notificationsCtrl.pushArenaPunishmentSysMsg(data, SCH_CLIENT_MSG_TYPE.HB_ARENA_WARNING_NOTIFICATIONS)
            ctx['showWindowCallback'] = callback
            return

    def __updateArenaBans(self):
        arenaBans = self.__itemsCache.items.stats.restrictions.get(RESTRICTION_TYPE.ARENA_BAN, {})
        offence = ARENA_BONUS_TYPE.HB_OFFENCE
        defence = ARENA_BONUS_TYPE.HB_DEFENCE
        hbBans = tuple((b for b in arenaBans.itervalues() if offence in b.get('bonusTypes', ()) or defence in b.get('bonusTypes', ())))
        if hbBans:
            ban = max(hbBans, key=lambda b: b.get('expiryTime', 0))
            expiryTime = ban['expiryTime']
            duration = time_utils.getTimeDeltaFromNow(expiryTime)
            if duration <= 0:
                expiryTime = None
            else:
                self.__banTimer.stopCallback(self.__updateArenaBans)
                self.__banTimer.delayCallback(duration + time_utils.ONE_SECOND, self.__updateArenaBans)
        else:
            expiryTime = None
        if self.__banExpiryTime != expiryTime:
            self.__banExpiryTime = expiryTime
            self.onLobbyHeaderUpdate()
            data = {'isStarted': self.__banExpiryTime is not None,
             'reason': hbBans[0].get('reason', ''),
             'banExpiryTime': self.banExpiryTime}
            self.__notificationsCtrl.pushArenaPunishmentSysMsg(data if hbBans else {}, SCH_CLIENT_MSG_TYPE.HB_ARENA_BAN_NOTIFICATIONS)
            if self.__banExpiryTime is None:
                showHBFairplayDialog(data)
        return

    def __onItemsSyncCompleted(self, *_):
        self.__updateArenaBans()

    def __onRestrictionsChanged(self, _):
        self.__updateArenaBans()

    def __onVehicleLoaded(self):
        if self.isHistoricalBattlesMode():
            self.__updateVehicleOutfit()
            self.__showVehicleMarker()
            self.onLobbyHeaderUpdate()
            Waiting.hide('hbUpdateVehicle')

    def __onQuestsUpdated(self, diff):
        self.onQuestsUpdated()

    def __onProgressChanged(self, *args, **kwargs):
        self.onProgressChanged()

    def __onClientUpdated(self, diff, _):
        if not self.__progressionInited:
            evPr = self.getGameEventData().get('eventProgression', {})
            self.__hbProgression.setSettings(evPr)
            self.__progressionInited = True
        hbNode = diff.get(HB_NODE)
        if hbNode and DIVISIONS_EXP_NODE in hbNode:
            divisionIds = diff[HB_NODE][DIVISIONS_EXP_NODE].keys()
            self.onDivisionsExpChanged(divisionIds)
            self.__showVehicleMarker()

    def __onSettingsChanged(self, diff):
        if HB_CONFIG in diff:
            self.__updateHBConfig(diff)
        if HB_GAME_PARAMS_KEY not in diff:
            return
        self.clearNotification()
        self.__addFrontStartTimeNotifiers()
        self.startNotification()
        self.onGameParamsChanged()
        self.__onCurrentFrontStateChanged()
        if not self.isEnabled():
            if self.isHistoricalBattlesMode():
                closeEvent()
            return
        evPr = self.getGameEventData().get('eventProgression', {})
        self.__hbProgression.setSettings(evPr)
        self.onLobbyHeaderUpdate()

    def __onFullScreenModeSelector(self, event):
        pass

    def __onFrontStartTimeCallback(self, frontID):
        self.onFrontTimeStatusUpdated(frontID)

    def __selectVehicle(self):
        if self.isHistoricalBattlesMode():
            Waiting.show('hbUpdateVehicle', isSingle=True, overlapsUI=False)
            divisionVehicles = self.getSelectedSubdivisionVehicles()
            vehicle = divisionVehicles[0]
            descriptor = vehicle.descriptor if hasattr(vehicle, 'descriptor') else None
            if descriptor:
                self.__hangarSpace.updateVehicle(vehicle)
            else:
                _logger.warning('HBGameEventController selected vehicle has no descriptor.')
        return

    def __updateVehicleOutfit(self):
        divisionVehicles = self.getSelectedSubdivisionVehicles()
        vehicle = divisionVehicles[0]
        descriptor = vehicle.descriptor if hasattr(vehicle, 'descriptor') else None
        if descriptor:
            outfit = self.__customizationService.getEmptyOutfitWithNationalEmblems(vehicleCD=vehicle.descriptor.makeCompactDescr())
            self.__hangarSpace.updateVehicle(vehicle, outfit)
        return

    def __getStoredVehInvID(self):
        storedVehInvID = AccountSettings.getFavorites(CURRENT_VEHICLE)
        if not storedVehInvID:
            criteria = REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN
            criteria |= ~REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.BATTLE_ROYALE])
            criteria |= ~REQ_CRITERIA.VEHICLE.HIDDEN_IN_HANGAR
            vehicle = first(self.__itemsCache.items.getVehicles(criteria=criteria).values())
            if vehicle:
                storedVehInvID = vehicle.invID
        return storedVehInvID

    def __showVehicleMarker(self):
        if not self.isHistoricalBattlesMode():
            return
        elif self.__prbIsSwitching:
            return
        else:
            hangarVehicle = self.__hangarSpace.getVehicleEntity()
            if hangarVehicle is None:
                _logger.warning('HBGameEventController hangarVehicle is None, can not be set marker.')
                return
            elif hangarVehicle.model is None:
                return
            currentSubdivision = self.frontController.getSelectedSubdivision()
            g_eventBus.handleEvent(DioramaVehicleEvent(DioramaVehicleEvent.ON_HB_TANK_LOADED, ctx={'entity': hangarVehicle,
             'name': BigWorld.player().name,
             'clan': g_clanCache.clanAbbrev if g_clanCache.isInClan else '',
             'inBattle': currentSubdivision.isInBattle(),
             'divisionID': currentSubdivision.getID(),
             'divisionLevel': currentSubdivision.getProgressionLevel(),
             'divisionEXP': currentSubdivision.getEXP()}), scope=EVENT_BUS_SCOPE.LOBBY)
            Waiting.hide('hbUpdateVehicle')
            return

    def __hideVehicleMarker(self):
        hangarVehicle = self.__hangarSpace.getVehicleEntity()
        if Waiting.isOpened('hbUpdateVehicle'):
            Waiting.hide('hbUpdateVehicle')
        if hangarVehicle is None:
            return
        else:
            g_eventBus.handleEvent(DioramaVehicleEvent(DioramaVehicleEvent.ON_HB_TANK_DESTROY, ctx={'entity': hangarVehicle}), scope=EVENT_BUS_SCOPE.LOBBY)
            return

    def __getEventTime(self, key):
        data = self.getGameEventData()
        return time_utils.makeLocalServerTime(data[key]) if data and key in data else time.time()

    def __getContainers(self):
        return (self.__fronts,)

    def __addFrontStartTimeNotifiers(self):
        for frontID, front in self.frontController.getFronts().iteritems():
            if not (front and front.isEnabled() and self.getTimeLeftToStartFront(frontID) > 0):
                continue
            callback = partial(self.__onFrontStartTimeCallback, frontID)
            delta = partial(self.__getTimer, frontID)
            self.addNotificator(AcyclicNotifier(delta, callback))

    def __getTimer(self, frontID):
        timeLeft = self.getTimeLeftToStartFront(frontID)
        return timeLeft + 1 if timeLeft > 0 else 0

    def getTimeLeftToStartFront(self, frontID):
        front = self.frontController.getFrontByID(frontID)
        return time_utils.getTimeDeltaFromNow(front.getStartTime())

    def __updateHBConfig(self, serverSettingsDiff):
        data = serverSettingsDiff[HB_CONFIG]
        self.__hbConfig = self.__hbConfig.replace(data)

    def __onCurrentFrontStateChanged(self):
        front = self.frontController.getSelectedFront()
        if front and not front.isAvailable():
            availableFront = self.frontController.getLatestFront()
            if availableFront:
                self.updateFrontData(frontId=availableFront.getID())
            else:
                _logger.error('There is no available front')
                closeEvent()

    def __onSpaceCreated(self):
        if self.__isInHB and not self.__custObjMgr.currentHangarName:
            BigWorld.callback(1, self.__onHangarEntered)

    def __onHangarEntered(self):
        SoundHangarController.onEnterEvent()
        SoundHangarController.onEnterHangar()
        self.__isInHB = True

    def __onHangarExited(self):
        self.__isInHB = False
        SoundHangarController.onExitHangar()
