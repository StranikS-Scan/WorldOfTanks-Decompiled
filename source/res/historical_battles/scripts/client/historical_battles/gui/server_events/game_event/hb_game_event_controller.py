# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/game_event/hb_game_event_controller.py
import logging
import time
from math import ceil
import typing
from functools import partial
import BigWorld
from Event import Event, EventManager
from constants import EVENT_CLIENT_DATA
from frameworks.wulf.gui_constants import WindowLayer
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader.settings import APP_NAME_SPACE
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ComponentEvent
from gui.shared.utils.performance_analyzer import PerformanceAnalyzerMixin
from gui.shared.utils.scheduled_notifications import AcyclicNotifier, Notifiable
from historical_battles_common.hb_constants_extension import PREBATTLE_TYPE, QUEUE_TYPE
from helpers import dependency, time_utils
from historical_battles.gui.impl.lobby.hb_helpers.hangar_helpers import closeEvent
from historical_battles.gui.server_events.game_event.front_progress import FrontsProgressController
from historical_battles.gui.server_events.game_event.hero_tank import HBHeroTankController
from historical_battles.gui.sounds.sound_progression_controller import HBSoundProgressionController
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles_common.hb_constants import HB_BATTLES_ENABLED, HB_GAME_PARAMS_KEY
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from wotdecorators import condition
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from gui.shared.events import FullscreenModeSelectorEvent
from historical_battles.gui.shared.event_dispatcher import showHBHangar
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from CurrentVehicle import g_currentVehicle
from historical_battles.gui.prb_control.prb_config import FUNCTIONAL_FLAG
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CURRENT_VEHICLE
from historical_battles_common.hb_constants_extension import ARENA_BONUS_TYPE
from constants import RESTRICTION_TYPE
from helpers.time_utils import ONE_SECOND, ONE_DAY, ONE_HOUR
from skeletons.gui.system_messages import ISystemMessages
from helpers.CallbackDelayer import CallbackDelayer
from historical_battles.gui.gui_constants import SCH_CLIENT_MSG_TYPE
from PlayerEvents import g_extPlayerEvents
from historical_battles.gui.shared.event_dispatcher import showHBFairplayDialog, showHBFairplayWarningDialog
from constants import FAIRPLAY_VIOLATIONS
from PlayerEvents import g_playerEvents
from historical_battles.gui.shared.hb_events import DioramaVehicleEvent
from gui.clans.clan_cache import g_clanCache
from gui.Scaleform.Waiting import Waiting
from skeletons.gui.customization import ICustomizationService
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from adisp import adisp_process
from historical_battles.gui.prb_control.prb_config import PREBATTLE_ACTION_NAME
if typing.TYPE_CHECKING:
    from HBCoinsComponent import HBCoinsComponent
    from HBFrontCouponsComponent import HBFrontCouponsComponent
_logger = logging.getLogger(__name__)

class HBGameEventController(PerformanceAnalyzerMixin, Notifiable, IGameEventController, IGlobalListener):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _appLoader = dependency.descriptor(IAppLoader)
    __hbProgression = dependency.descriptor(IHBProgressionOnTokensController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __customizationService = dependency.descriptor(ICustomizationService)
    ifStarted = condition('_started')
    HB_VIOLATIONS = (FAIRPLAY_VIOLATIONS.HB_AFK, FAIRPLAY_VIOLATIONS.HB_DESERTER)

    def __init__(self):
        super(HBGameEventController, self).__init__()
        self.__isInHBMode = False
        self.__isShowingProgressionView = False
        from historical_battles.gui.close_event_confirmator import CloseEventConfirmator
        self.__closeEventConfirmator = CloseEventConfirmator()
        self._fronts = FrontsProgressController()
        self._heroTank = HBHeroTankController()
        self._soundProgressionCtrl = HBSoundProgressionController()
        self._em = EventManager()
        self.onProgressChanged = Event(self._em)
        self.onQuestsUpdated = Event(self._em)
        self.onFrontTimeStatusUpdated = Event(self._em)
        self.onSelectedFrontChanged = Event(self._em)
        self.onSelectedFrontmanChanged = Event(self._em)
        self.onFrontmanVehicleChanged = Event(self._em)
        self.onFrontmanLockChanged = Event(self._em)
        self.onGameParamsChanged = Event(self._em)
        self.onDisableFrontsWidget = Event(self._em)
        self.onLobbyHeaderUpdate = Event(self._em)
        self.onShowBattleQueueView = Event(self._em)
        self.onCloseAllAwardsWindow = Event(self._em)
        self._started = False
        self.__progressionInited = False
        self.__banTimer = CallbackDelayer()
        self.__banExpiryTime = None
        self.__prbIsSwitching = False
        return

    @property
    def coins(self):
        return getattr(BigWorld.player(), 'HBCoinsComponent', None)

    @property
    def frontCoupons(self):
        return getattr(BigWorld.player(), 'HBFrontCouponsComponent', None)

    @property
    def frontController(self):
        return self._fronts

    @property
    def heroTank(self):
        return self._heroTank

    @property
    def soundProgressionCtrl(self):
        return self._soundProgressionCtrl

    def init(self):
        g_clientUpdateManager.addCallbacks({'eventsData.' + str(EVENT_CLIENT_DATA.QUEST): self._onQuestsUpdated})
        g_eventBus.addListener(ComponentEvent.COMPONENT_REGISTERED, self._onComponentRegistered, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(FullscreenModeSelectorEvent.NAME, self.__onFullScreenModeSelector)
        g_clientUpdateManager.addCallbacks({'stats.restrictions': self.__onRestrictionsChanged})
        if self._soundProgressionCtrl:
            self._soundProgressionCtrl.init()

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._em.clear()
        self.stop()
        self.__banTimer.clearCallbacks()
        self.__banTimer = None
        g_eventBus.removeListener(ComponentEvent.COMPONENT_REGISTERED, self._onComponentRegistered, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(FullscreenModeSelectorEvent.NAME, self.__onFullScreenModeSelector, EVENT_BUS_SCOPE.GLOBAL)
        if self.prbDispatcher and self.prbDispatcher.hasListener(self):
            self.prbDispatcher.removeListener(self)
        if self._soundProgressionCtrl:
            self._soundProgressionCtrl.fini()
            self._soundProgressionCtrl = None
        return

    def start(self):
        if self._started:
            _logger.error('HBGameEventController already started')
            return
        self.__closeEventConfirmator.start()
        for container in self._getContainers():
            container.start()

        self._started = True
        self._fronts.onItemsUpdated += self._onProgressChanged
        if self.frontCoupons:
            self.frontCoupons.onFrontCouponsUpdated += self._onProgressChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onSettingsChanged
        self._itemsCache.onSyncCompleted += self.__onItemsSyncCompleted
        g_extPlayerEvents.onExtGetCustomPunishmentWindow += self.__onExtGetCustomPunishmentWindow
        g_playerEvents.onClientUpdated += self._onClientUpdated
        self._hangarSpace.onVehicleChanged += self.__onVehicleLoaded
        self._onProgressChanged()
        self.__addFrontStartTimeNotifiers()
        self.startNotification()

    @ifStarted
    def stop(self):
        self.__closeEventConfirmator.stop()
        self.__banTimer.clearCallbacks()
        self.__banExpiryTime = None
        self.frontController.onItemsUpdated -= self._onProgressChanged
        if self.frontCoupons:
            self.frontCoupons.onFrontCouponsUpdated -= self._onProgressChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self._onSettingsChanged
        self._itemsCache.onSyncCompleted -= self.__onItemsSyncCompleted
        g_extPlayerEvents.onExtGetCustomPunishmentWindow -= self.__onExtGetCustomPunishmentWindow
        g_playerEvents.onClientUpdated -= self._onClientUpdated
        self._hangarSpace.onVehicleChanged -= self.__onVehicleLoaded
        for container in self._getContainers():
            container.stop()

        self._started = False
        self.__progressionInited = False
        self.clearNotification()
        return

    def clear(self):
        self.stop()

    def isHistoricalBattlesMode(self):
        if self.prbDispatcher is None:
            return False
        else:
            state = self.prbDispatcher.getFunctionalState()
            isInPreQueue = any((state.isInPreQueue(queueType) for queueType in QUEUE_TYPE.HB_RANGE))
            return state.isInUnit(PREBATTLE_TYPE.HISTORICAL_BATTLES) or isInPreQueue

    def getGameEventData(self):
        return self.lobbyContext.getServerSettings().hbConfig.asDict()

    def isEnabled(self):
        return self.getGameEventData().get('isEnabled', False)

    def getEnvironmentSettings(self):
        return self.getGameEventData().get('hangarEnvironmentSettings', {})

    def isLastDay(self):
        return self.getEventFinishTimeLeft() < ONE_DAY

    def getHoursLeft(self):
        return ceil(self.getEventFinishTimeLeft() / ONE_HOUR)

    def getQuestsUpdateHoursLeft(self):
        secondsLeft = ONE_DAY - time_utils.getServerRegionalTimeCurrentDay()
        return ceil(secondsLeft / ONE_HOUR)

    def _getEventTime(self, key):
        data = self.getGameEventData()
        return time_utils.makeLocalServerTime(data[key]) if data and key in data else time.time()

    def getEventStartTime(self):
        return self._getEventTime('startDate')

    def getEventFinishTime(self):
        return self._getEventTime('endDate')

    def getEventFinishTimeLeft(self):
        finishTime = self.getEventFinishTime()
        return time_utils.getTimeDeltaFromNowInLocal(finishTime) if finishTime is not None else 0

    def isBattlesEnabled(self):
        return self.getGameEventData().get('isBattlesEnabled', False)

    def onPrbEntitySwitched(self):
        self.__selectVehicle()
        if not self.isHistoricalBattlesMode():
            if self.__isInHBMode:
                windowContainer = self._appLoader.getApp(APP_NAME_SPACE.SF_LOBBY).containerManager.getContainer(WindowLayer.SUB_VIEW)
                self.__hideVehicleMarker()
                if windowContainer and not windowContainer.getAllLoadingViews():
                    storedVehInvID = AccountSettings.getFavorites(CURRENT_VEHICLE)
                    if not storedVehInvID:
                        g_currentVehicle.selectVehicle(0)
                        self._hangarSpace.removeVehicle()
                    from gui.shared.event_dispatcher import showHangar
                    showHangar()
                self.__isInHBMode = False
        else:
            self.__isInHBMode = True
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

    def isShowingProgressionView(self):
        return self.__isShowingProgressionView

    def setShowingProgressionView(self, isShow):
        self.__isShowingProgressionView = isShow

    def onPrbEntitySwitching(self):
        self.__prbIsSwitching = True

    def isHBPrbActive(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.HISTORICAL_BATTLES)

    def setSelectedFrontmanID(self, frontmanID):
        self.frontController.setSelectedFrontmanID(frontmanID)
        self.__selectVehicle()

    def updateVehicle(self):
        self.__selectVehicle()

    @property
    def isBanned(self):
        return self.banDuration > 0

    @property
    def banDuration(self):
        return max(0, time_utils.getTimeDeltaFromNow(self.__banExpiryTime)) if self.__banExpiryTime is not None else 0

    @property
    def banExpiryTime(self):
        return self.__banExpiryTime

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
                    self.__pushArenaPunishmentSysMsg(data, SCH_CLIENT_MSG_TYPE.HB_ARENA_WARNING_NOTIFICATIONS)
            elif penaltyType == 'warning':
                callback = partial(showHBFairplayWarningDialog, violationName)
                self.__pushArenaPunishmentSysMsg(data, SCH_CLIENT_MSG_TYPE.HB_ARENA_WARNING_NOTIFICATIONS)
            ctx['showWindowCallback'] = callback
            return

    def __pushArenaPunishmentSysMsg(self, data, punishmentType):
        self.__systemMessages.proto.serviceChannel.pushClientMessage(data, punishmentType)

    def __updateArenaBans(self):
        arenaBans = self._itemsCache.items.stats.restrictions.get(RESTRICTION_TYPE.ARENA_BAN, {})
        arenBonusType = ARENA_BONUS_TYPE.HISTORICAL_BATTLES
        hbBans = tuple((b for b in arenaBans.itervalues() if arenBonusType in b.get('bonusTypes', ())))
        if hbBans:
            ban = max(hbBans, key=lambda b: b.get('expiryTime', 0))
            expiryTime = ban['expiryTime']
            duration = time_utils.getTimeDeltaFromNow(expiryTime)
            if duration <= 0:
                expiryTime = None
            else:
                self.__banTimer.stopCallback(self.__updateArenaBans)
                self.__banTimer.delayCallback(duration + ONE_SECOND, self.__updateArenaBans)
        else:
            expiryTime = None
        if self.__banExpiryTime != expiryTime:
            self.__banExpiryTime = expiryTime
            self.onLobbyHeaderUpdate()
            data = {'isStarted': self.__banExpiryTime is not None,
             'reason': hbBans[0].get('reason', ''),
             'banExpiryTime': self.banExpiryTime}
            self.__pushArenaPunishmentSysMsg(data if hbBans else {}, SCH_CLIENT_MSG_TYPE.HB_ARENA_BAN_NOTIFICATIONS)
        return

    def __onItemsSyncCompleted(self, *_):
        self.__updateArenaBans()

    def __onRestrictionsChanged(self, _):
        self.__updateArenaBans()

    def __selectVehicle(self):
        if self.isHistoricalBattlesMode():
            vehicle = self.getSelectedFrontmanVehicle()
            descriptor = vehicle.descriptor if hasattr(vehicle, 'descriptor') else None
            if descriptor:
                Waiting.show('hbUpdateVehicle', isSingle=True, overlapsUI=False)
                self._hangarSpace.updateVehicleDescriptor(descriptor)
                outfit = self.__customizationService.getEmptyOutfitWithNationalEmblems(vehicleCD=vehicle.descriptor.makeCompactDescr())
                self._hangarSpace.startToUpdateVehicle(vehicle, outfit=outfit)
            else:
                _logger.warning('HBGameEventController selected vehicle has no descriptor.')
        return

    def getSelectedFrontmanVehicle(self):
        frontman = self.frontController.getSelectedFrontman()
        intCD = frontman.getSelectedVehicle().intCD
        return self._itemsCache.items.getItemByCD(intCD)

    def canSelectedVehicleStartToBattle(self):
        vehicle = self.getSelectedFrontmanVehicle()
        vehInvID = vehicle.invID if hasattr(vehicle, 'invID') else -1
        return vehInvID > 0

    def canVehicleStartToBattle(self, intCD):
        vehicle = self._itemsCache.items.getItemByCD(intCD)
        vehInvID = vehicle.invID if hasattr(vehicle, 'invID') else -1
        return vehInvID > 0

    def onLobbyInited(self, event):
        super(HBGameEventController, self).onLobbyInited(event)
        if not self.prbDispatcher.hasListener(self):
            self.prbDispatcher.addListener(self)

    def onDisconnected(self):
        self.clear()
        super(HBGameEventController, self).onDisconnected()

    def __onVehicleLoaded(self):
        if self.isHistoricalBattlesMode():
            self.__showVehicleMarker()
            self.onLobbyHeaderUpdate()

    def __showVehicleMarker(self):
        if not self.isHistoricalBattlesMode():
            return
        elif self.__prbIsSwitching:
            return
        else:
            hangarVehicle = self._hangarSpace.getVehicleEntity()
            if hangarVehicle is None:
                _logger.warning('HBGameEventController hangarVehicle is None, can not be set marker.')
                return
            elif hangarVehicle.model is None:
                return
            frontman = self.frontController.getSelectedFrontman()
            roleId = frontman.getRoleID()
            g_eventBus.handleEvent(DioramaVehicleEvent(DioramaVehicleEvent.ON_HB_TANK_LOADED, ctx={'entity': hangarVehicle,
             'name': BigWorld.player().name,
             'clan': g_clanCache.clanAbbrev if g_clanCache.isInClan else '',
             'roleId': roleId,
             'inBattle': frontman.isLocked()}), scope=EVENT_BUS_SCOPE.LOBBY)
            Waiting.hide('hbUpdateVehicle')
            return

    def __hideVehicleMarker(self):
        hangarVehicle = self._hangarSpace.getVehicleEntity()
        if Waiting.isOpened('hbUpdateVehicle'):
            Waiting.hide('hbUpdateVehicle')
        if hangarVehicle is None:
            return
        else:
            g_eventBus.handleEvent(DioramaVehicleEvent(DioramaVehicleEvent.ON_HB_TANK_DESTROY, ctx={'entity': hangarVehicle}), scope=EVENT_BUS_SCOPE.LOBBY)
            return

    def _getContainers(self):
        return (self._fronts,)

    def _onQuestsUpdated(self, diff):
        self.onQuestsUpdated()

    def _onProgressChanged(self, *args, **kwargs):
        self.onProgressChanged()

    def _onComponentRegistered(self, event):
        if event.alias == VIEW_ALIAS.MESSENGER_BAR:
            for queueType in QUEUE_TYPE.HB_RANGE:
                event.componentPy.addDisableReferralQueue(queueType)
                event.componentPy.addDisableVehicleCompareQueue(queueType)

    def _onClientUpdated(self, diff, _):
        if not self.__progressionInited:
            evPr = self.getGameEventData().get('eventProgression', {})
            self.__hbProgression.setSettings(evPr)
            self.__progressionInited = True

    def __pushHBEndedNotification(self):
        text = backport.text(R.strings.hb_lobby.system_messages.switched_off_event.body())
        SystemMessages.pushMessage(text, type=SystemMessages.SM_TYPE.ErrorSimple)

    def __pushHBStartedNotification(self):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({}, SCH_CLIENT_MSG_TYPE.HB_STARTED_NOTIFICATION)

    def __pushHBBattlesSwitchedOnNotification(self):
        text = backport.text(R.strings.hb_lobby.system_messages.switched_on_battles.body())
        SystemMessages.pushMessage(text, type=SystemMessages.SM_TYPE.Information)

    def __pushHBBattlesSwitchedOffNotification(self):
        text = backport.text(R.strings.hb_lobby.system_messages.switched_off_battles.body())
        SystemMessages.pushMessage(text, type=SystemMessages.SM_TYPE.ErrorSimple)

    def _onSettingsChanged(self, diff):
        if HB_GAME_PARAMS_KEY not in diff:
            return
        self.clearNotification()
        self.__addFrontStartTimeNotifiers()
        self.startNotification()
        self.onGameParamsChanged()
        if not self.isEnabled():
            self.__pushHBEndedNotification()
            if self.isHistoricalBattlesMode():
                closeEvent()
            return
        if self.isEnabled() and not self.isHistoricalBattlesMode() and self.isBattlesEnabled():
            self.__pushHBStartedNotification()
            return
        if self.__battlesEnabledWasChanged(diff):
            isEnabled = self.isBattlesEnabled()
            if isEnabled:
                self.__pushHBBattlesSwitchedOnNotification()
            else:
                self.__pushHBBattlesSwitchedOffNotification()
        evPr = self.getGameEventData().get('eventProgression', {})
        self.__hbProgression.setSettings(evPr)
        if self.__battlesEnabledWasChanged(diff):
            self.onLobbyHeaderUpdate()

    def __addFrontStartTimeNotifiers(self):
        for frontID, front in self.frontController.getFronts().iteritems():
            if not (front and front.isEnabled() and self.__getTimeLeftToStartFront(frontID) > 0):
                continue
            callback = partial(self.__onFrontStartTimeCallback, frontID)
            delta = partial(self.__getTimer, frontID)
            self.addNotificator(AcyclicNotifier(delta, callback))

    def __getTimer(self, frontID):
        timeLeft = self.__getTimeLeftToStartFront(frontID)
        return timeLeft + 1 if timeLeft > 0 else 0

    def __onFrontStartTimeCallback(self, frontID):
        self.onFrontTimeStatusUpdated(frontID)

    def __getTimeLeftToStartFront(self, frontID):
        front = self.frontController.getFrontByID(frontID)
        return time_utils.getTimeDeltaFromNow(front.getStartTime())

    def __battlesEnabledWasChanged(self, diff):
        return HB_BATTLES_ENABLED in diff.get(HB_GAME_PARAMS_KEY, {})

    def __onFullScreenModeSelector(self, event):
        if event:
            isShowing = event.ctx['showing']
            if not isShowing and self.__isInHBMode:
                showHBHangar()
