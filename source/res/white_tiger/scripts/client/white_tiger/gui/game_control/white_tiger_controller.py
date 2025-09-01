# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/game_control/white_tiger_controller.py
from collections import namedtuple
from typing import Dict
import WWISE
import adisp
import Event
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CURRENT_VEHICLE
from frameworks.wulf import WindowLayer
from gui.impl.gen import R
from gui.game_control.season_provider import SeasonProvider
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.system_factory import collectIgnoredModeForAutoSelectVehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import dependency, time_utils, server_settings
from shared_utils import makeTupleByDict
from white_tiger.gui.prb_control.entities.pre_queue.entity import WhiteTigerEntity
from white_tiger.gui.prb_control.entities.squad.entity import WhiteTigerSquadEntity
from white_tiger.gui.white_tiger_account_settings import isWelcomeScreenSeen, setWelcomeScreenSeen
from white_tiger.gui.shared.event_dispatcher import showWelcomeScreen
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from adisp import adisp_process
from gui.prb_control.entities.base.ctx import PrbAction
from white_tiger.gui.white_tiger_gui_constants import PREBATTLE_ACTION_NAME, SOUND_REMAPPING_LABEL
from white_tiger_common.wt_constants import WHITE_TIGER_GAME_PARAMS_KEY, WT_VEHICLE_TAGS, QUEUE_TYPE, PREBATTLE_TYPE, ARENA_BONUS_TYPE
from perfomance_analyzer_controller import PerformanceAnalyzer, WTPerformance
from white_tiger.gui.game_control.settings.white_tiger_settings_controller import WhiteTigerSettingsController
from white_tiger.gui.sounds.sound_constants import WhiteTigerHangarSound

class _WhiteTigerConfig(namedtuple('_WhiteTigerConfig', ('isEnabled', 'peripheryIDs', 'primeTimes', 'seasons', 'cycleTimes', 'specialVehicles', 'lootBoxDailyPurchaseLimit', 'lootBoxCounterEntitlementID', 'specialTankmen', 'autoOpenTime', 'eventShowcaseVehicle'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, peripheryIDs={}, primeTimes={}, seasons={}, cycleTimes={}, specialVehicles=[], lootBoxDailyPurchaseLimit=0, lootBoxCounterEntitlementID='', specialTankmen={}, autoOpenTime='', eventShowcaseVehicle='')
        defaults.update(kwargs)
        return super(_WhiteTigerConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class WhiteTigerSoundBanksRemapper(object):

    def __init__(self):
        self.__activeSoundRemapping = set()

    def clear(self):
        for label in list(self.__activeSoundRemapping):
            self.__deactivateSoundRemappingLabel(label)

    def setActiveWhiteTigerSoundbanksByLabel(self, isActive, label):
        if isActive:
            self.__activateSoundRemappingLabel(label)
        else:
            self.__deactivateSoundRemappingLabel(label)

    def __activateSoundRemappingLabel(self, label):
        if label and label not in self.__activeSoundRemapping:
            WWISE.activateRemapping(label)
            self.__activeSoundRemapping.add(label)

    def __deactivateSoundRemappingLabel(self, label):
        if label and label in self.__activeSoundRemapping:
            WWISE.deactivateRemapping(label)
            self.__activeSoundRemapping.remove(label)


class WhiteTigerController(IWhiteTigerController, IGlobalListener, SeasonProvider, PerformanceAnalyzer, Notifiable):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WhiteTigerController, self).__init__()
        self.onPrimeTimeStatusUpdated = Event.Event()
        self.onEventPrbChanged = Event.Event()
        self.onEventEnded = Event.Event()
        self.__wtSettingsCtrl = WhiteTigerSettingsController()
        self.__wtSoundBanksRemapper = WhiteTigerSoundBanksRemapper()
        self.__wtEventHangarSound = WhiteTigerHangarSound()
        self.__isWTModeEnabled = False
        self.__performanceRisk = None
        return

    def onLobbyInited(self, event):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.startGlobalListening()
        if self.isAvailable():
            self.__wtSoundBanksRemapper.setActiveWhiteTigerSoundbanksByLabel(True, SOUND_REMAPPING_LABEL)
        if isinstance(self.prbEntity, (WhiteTigerEntity, WhiteTigerSquadEntity)):
            self.__enableWTMode()
        self.__wtSettingsCtrl.onLobbyInited(event)
        self.startNotification()
        g_eventBus.addListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onSelectVehicleInHangar, scope=EVENT_BUS_SCOPE.LOBBY)

    def init(self):
        self.__wtSettingsCtrl.init()
        self.addNotificator(SimpleNotifier(self.getTimer, self.__timerUpdate))
        self.addNotificator(SimpleNotifier(self.getTimeLeft, self.__onEventEnded))

    def fini(self):
        self.clearNotification()
        self.__wtSettingsCtrl.fini()
        self.__wtSettingsCtrl = None
        self.__unsubscribe()
        self.__clear()
        self.__wtSoundBanksRemapper.clear()
        return

    def getDisabledSettings(self):
        return self.__wtSettingsCtrl.disabledSettings

    def isInWhiteTigerMode(self):
        isEventPrbActive = self.isEventPrbActive()
        arenaBonusType = self.__sessionProvider.arenaVisitor.getArenaBonusType()
        return isEventPrbActive or arenaBonusType == ARENA_BONUS_TYPE.WHITE_TIGER

    def isAvailable(self):
        return self.isEnabled() and not self.isFrozen() and self.getCurrentSeason() is not None

    def isEnabled(self):
        return self.getModeSettings().isEnabled

    def isInAnnouncement(self):
        now = time_utils.getCurrentLocalServerTimestamp()
        return now < self.getStartDate()

    def getTimeLeft(self):
        if not self.isEnabled() or self.getCurrentSeason() is None:
            return 0
        else:
            now = time_utils.getCurrentLocalServerTimestamp()
            return self.getEndDate() - now

    def isBattlesPossible(self):
        _, _, isPrimeNow = self.getPrimeTimeStatus()
        return self.isEnabled() and self.getCurrentSeason() is not None and isPrimeNow

    def isPromoScreenEnabled(self):
        return False

    def isEventPrbActive(self):
        dispatcher = self.prbDispatcher
        state = dispatcher.getFunctionalState() if dispatcher is not None else None
        return state is not None and (state.isInPreQueue(QUEUE_TYPE.WHITE_TIGER) or state.isInUnit(PREBATTLE_TYPE.WHITE_TIGER))

    @prbEntityProperty
    def prbEntity(self):
        pass

    def onDisconnected(self):
        super(WhiteTigerController, self).onDisconnected()
        self.__disableWTMode()
        self.__wtSettingsCtrl.onDisconnected()
        self.__unsubscribe()
        self.__clear()

    def onAvatarBecomePlayer(self):
        super(WhiteTigerController, self).onAvatarBecomePlayer()
        self.__wtSettingsCtrl.onAvatarBecomePlayer()
        self.__unsubscribe()
        self.__clear()

    def onAccountBecomePlayer(self):
        self.__wtSettingsCtrl.onAccountBecomePlayer()

    @adisp_process
    def selectBattle(self, callback=None):
        prebattleType = PREBATTLE_ACTION_NAME.WHITE_TIGER
        dispatcher = self.prbDispatcher
        if dispatcher is None:
            return
        else:
            result = yield dispatcher.doSelectAction(PrbAction(prebattleType), fadeCtx={'layer': WindowLayer.OVERLAY,
             'waitForLayoutReady': R.views.white_tiger.mono.lobby.main()})
            if callback and result:
                callback()
            return

    def isSelectedVehicleWTVehicle(self):
        currentVehicle = g_currentVehicle.item
        vehicles = self.getWTVehicles()
        return currentVehicle and g_currentVehicle.item.intCD in vehicles

    def _showWelcomeIfNeeded(self):
        hasSeason = self.getCurrentSeason() is not None
        mustShow = not (isWelcomeScreenSeen() and hasSeason)
        if mustShow:
            showWelcomeScreen()
            if hasSeason:
                setWelcomeScreenSeen()
        return

    def isFrozen(self):
        for primeTime in self.getPrimeTimes().values():
            if primeTime.hasAnyPeriods():
                return False

        return True

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().getSettings().get(WHITE_TIGER_GAME_PARAMS_KEY, {})

    def getWTVehicles(self):
        return self.getConfig().get('vehicles', [])

    def getEndDate(self):
        season = self.getCurrentSeason()
        if season is not None:
            return season.getEndDate()
        else:
            season = self.getNextSeason()
            return season.getEndDate() if season else 0

    def getStartDate(self):
        season = self.getCurrentSeason()
        if season is not None:
            return season.getStartDate()
        else:
            season = self.getNextSeason()
            return season.getStartDate() if season else 0

    def getSquadConfig(self):
        config = self.getConfig()
        return config['matchmaker']['squadConfig']

    def getModeSettings(self):
        return makeTupleByDict(_WhiteTigerConfig, self.getConfig()) if self.getConfig() else _WhiteTigerConfig.defaults()

    def getAlertBlock(self):
        if not self.hasSuitableVehicles():
            visible = True
            buttonCallback = None
        elif self.isInPreannounceState():
            visible = True
            buttonCallback = None
        else:
            visible = not self.isInPrimeTime() and self.isEnabled()
            buttonCallback = None
        alertData = self._getAlertBlockData() if visible else None
        return (alertData is not None, alertData, self._ALERT_DATA_CLASS.packCallbacks(buttonCallback))

    def onPrbEntitySwitched(self):
        if not any((self.prbEntity.getModeFlags() & flag for flag in collectIgnoredModeForAutoSelectVehicle())):
            g_currentVehicle.selectVehicle(AccountSettings.getFavorites(CURRENT_VEHICLE))
        if isinstance(self.prbEntity, (WhiteTigerEntity, WhiteTigerSquadEntity)):
            self.__enableWTMode()
        else:
            self.__disableWTMode()
        self.onEventPrbChanged(self.isEventPrbActive())

    def selectRandomMode(self):
        self.__selectMode(PREBATTLE_ACTION_NAME.RANDOM)

    def selectVehicle(self, invID=0):
        if not self.__isWTModeEnabled:
            return
        if isinstance(self.prbEntity, (WhiteTigerEntity, WhiteTigerSquadEntity)):
            self.prbEntity.selectModeVehicle(invID)

    @property
    def performanceRisk(self):
        if self.__performanceRisk is None:
            perfRisk = self.analyzeClientSystem()
            self.__performanceRisk = WTPerformance.getPerformanceRiskMap(perfRisk)
        return self.__performanceRisk

    def __getOwnedWhiteTigerVehicles(self):
        criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_ANY_TAG(WT_VEHICLE_TAGS.EVENT_VEHS)
        return dict([ (vehicle.invID, vehicle) for vehicle in self.__itemsCache.items.getVehicles(criteria=criteria).values() ])

    def __enableWTMode(self):
        if self.__isWTModeEnabled:
            return
        self.__wtSoundBanksRemapper.setActiveWhiteTigerSoundbanksByLabel(True, SOUND_REMAPPING_LABEL)
        self._showWelcomeIfNeeded()
        self.__wtEventHangarSound.isActive(True)
        self.__isWTModeEnabled = True

    def __disableWTMode(self):
        if not self.__isWTModeEnabled:
            return
        self.__wtEventHangarSound.isActive(False)
        self.__isWTModeEnabled = False

    def __unsubscribe(self):
        self.stopGlobalListening()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged

    @adisp.adisp_process
    def __selectMode(self, name):
        dispatcher = self.prbDispatcher
        if dispatcher is None:
            return
        else:
            isWhiteTigerMode = name == PREBATTLE_ACTION_NAME.WHITE_TIGER
            yield dispatcher.doSelectAction(PrbAction(name), fadeCtx={'layer': WindowLayer.OVERLAY,
             'waitForLayoutReady': R.views.white_tiger.mono.lobby.hangar() if isWhiteTigerMode else None})
            return

    def __clear(self):
        self.stopGlobalListening()
        self.__wtEventHangarSound.clear()
        self.__isWTModeEnabled = False
        g_eventBus.removeListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onSelectVehicleInHangar, scope=EVENT_BUS_SCOPE.LOBBY)

    def __onSelectVehicleInHangar(self, event):
        if not self.isInWhiteTigerMode():
            return
        vehicleInvID = event.ctx['vehicleInvID']
        vehicle = self.__itemsCache.items.getVehicle(vehicleInvID)
        if vehicle:
            self.selectRandomMode()

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onPrimeTimeStatusUpdated(status)
        if self.isInWhiteTigerMode() and (status == PrimeTimeStatus.FROZEN or not self.isEnabled()):
            self.selectRandomMode()

    def __onEventEnded(self):
        self.stopNotification()
        self.onEventEnded()
        self.selectRandomMode()

    @server_settings.serverSettingsChangeListener(WHITE_TIGER_GAME_PARAMS_KEY)
    def __onServerSettingsChanged(self, diff):
        self.startNotification()
        self.__timerUpdate()
        self.__wtSoundBanksRemapper.setActiveWhiteTigerSoundbanksByLabel(self.isAvailable(), SOUND_REMAPPING_LABEL)
