# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/game_control/ls_controller.py
from collections import namedtuple
import CGF
import Event
import WWISE
import adisp
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CURRENT_VEHICLE
from CurrentVehicle import g_currentVehicle
from cgf_components.hangar_camera_manager import HangarCameraManager
from skeletons.gui.shared import IItemsCache
from frameworks.wulf import WindowLayer
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.game_control.season_provider import SeasonProvider
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar as showMainHangar
from gui.shared.system_factory import collectIgnoredModeForAutoSelectVehicle
from last_stand.gui.shared.event_dispatcher import closeViewsByID, showHangar
from last_stand.gui.prb_control.entities.pre_queue.entity import LastStandEntity
from last_stand.gui.prb_control.entities.squad.entity import LastStandSquadEntity
from last_stand.gui.shared.utils.performance_analyzer import PerformanceAnalyzerMixin
from last_stand.gui.shared.event_dispatcher import showPromoWindowView
from last_stand.gui.sounds.sound_constants import LS_SOUND_REMAPPING
from helpers import dependency, time_utils
from last_stand_common.last_stand_constants import QUEUE_TYPE, PREBATTLE_TYPE, FORBIDDEN_VEHICLE_TAGS
from last_stand.gui.ls_gui_constants import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, QUEUE_TYPE_TO_DIFFICULTY_LEVEL
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from last_stand.skeletons.ls_controller import ILSController
from last_stand_common.last_stand_constants import LAST_STAND_GAME_PARAMS_KEY
from shared_utils import makeTupleByDict
from skeletons.gui.game_control import IReferralProgramController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IHangarLoadingController
from skeletons.gui.game_control import ILimitedUIController
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.game_control import ILootBoxSystemController

class _LSConfig(namedtuple('_LSConfig', ('isEnabled', 'isBattlesEnabled', 'startDate', 'endDate', 'rewardsSettings', 'artefactsSettings', 'dailyBonusSettings', 'vehicles', 'shop', 'isPromoScreenEnabled', 'isIntroVideoEnabled', 'prominentBonus', 'modeSelectorShowRewards'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, isBattlesEnabled={}, startDate=0, endDate=0, rewardsSettings={}, artefactsSettings={}, dailyBonusSettings={}, vehicles={}, shop={}, isPromoScreenEnabled=False, isIntroVideoEnabled=False, prominentBonus={}, modeSelectorShowRewards={})
        defaults.update(kwargs)
        return super(_LSConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


_VehiclesConfig = namedtuple('_VehiclesConfig', ('allowedVehicles', 'allowedLevels', 'forbiddenClassTags', 'forbiddenVehicles'))

class LSController(ILSController, Notifiable, SeasonProvider, IGlobalListener, PerformanceAnalyzerMixin):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarLoadingController = dependency.descriptor(IHangarLoadingController)
    __referralCtrl = dependency.descriptor(IReferralProgramController)
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __difficultyLevelCtrl = dependency.descriptor(IDifficultyLevelController)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self):
        super(LSController, self).__init__()
        self.__serverSettings = None
        self._prevStates = (False, {})
        self.onEventDisabled = Event.Event()
        self.onSettingsUpdate = Event.Event()
        return

    def init(self):
        super(LSController, self).init()
        self._prevStates = (False, {})
        self.addNotificator(SimpleNotifier(self.__getTimer, self.__timerUpdate))
        self.__hangarLoadingController.onHangarLoadedAfterLogin += self.__onHangarLoadedAfterLogin

    def fini(self):
        self.onEventDisabled.clear()
        self.onSettingsUpdate.clear()
        self.clearNotification()
        self._prevStates = (False, {})
        self.__clear()
        self.__hangarLoadingController.onHangarLoadedAfterLogin -= self.__onHangarLoadedAfterLogin
        super(LSController, self).fini()

    def onDisconnected(self):
        super(LSController, self).onDisconnected()
        self._prevStates = (False, {})
        self.__clear()

    def onAvatarBecomePlayer(self):
        super(LSController, self).onAvatarBecomePlayer()
        self.__clear()

    def onAccountBecomePlayer(self):
        super(LSController, self).onAccountBecomePlayer()
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())

    def onLobbyStarted(self, ctx):
        super(LSController, self).onLobbyStarted(ctx)
        self.startNotification()
        g_eventBus.addListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onSelectVehicleInHangar, scope=EVENT_BUS_SCOPE.LOBBY)
        if self.isAvailable():
            WWISE.activateRemapping(LS_SOUND_REMAPPING)

    def onLobbyInited(self, event):
        self.startGlobalListening()
        if not self.isAvailable() and self.isEventPrb():
            self.selectRandomMode()

    def onPrbEntitySwitched(self):
        self.__referralCtrl.setReferralHardDisabled(self.isEventPrb())
        if not any((self.prbEntity.getModeFlags() & flag for flag in collectIgnoredModeForAutoSelectVehicle())):
            g_currentVehicle.selectVehicle(AccountSettings.getFavorites(CURRENT_VEHICLE))
        if isinstance(self.prbEntity, LastStandEntity):
            accountSelectedLevel = self.__difficultyLevelCtrl.getLastSelectedLevel()
            self.__difficultyLevelCtrl.selectLevel(accountSelectedLevel)
        if self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.STRONGHOLD:
            showMainHangar()

    @property
    def lootBoxesEvent(self):
        return self.__lootBoxes.mainEntryPoint

    def isEnabled(self):
        return self.getModeSettings().isEnabled

    def isBattlesEnabled(self):
        currentQueueType = self.prbEntity.currentQueueType if self.prbEntity is not None else QUEUE_TYPE.UNKNOWN
        return self.getModeSettings().isBattlesEnabled.get(currentQueueType, False)

    def isPromoScreenEnabled(self):
        return self.getModeSettings().isPromoScreenEnabled and self.isEnabled()

    def isIntroVideoEnabled(self):
        return self.getModeSettings().isIntroVideoEnabled and self.isEnabled()

    def isAvailable(self):
        return self.isEnabled() and self.__getTimer() is not None

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().getSettings().get(LAST_STAND_GAME_PARAMS_KEY, {})

    def getModeSettings(self):
        return makeTupleByDict(_LSConfig, self.getConfig()) if self.getConfig() else _LSConfig.defaults()

    def selectBattle(self):
        self.__selectMode(PREBATTLE_ACTION_NAME.LAST_STAND)

    def openHangar(self):
        if self.isEventPrb():
            showHangar()
        else:
            self.selectBattle()

    def isEventPrb(self):
        prbDispatcher = self.prbDispatcher
        state = prbDispatcher.getFunctionalState() if prbDispatcher is not None else None
        return state is not None and (state.isInPreQueue(QUEUE_TYPE.LAST_STAND) or state.isInPreQueue(QUEUE_TYPE.LAST_STAND_MEDIUM) or state.isInPreQueue(QUEUE_TYPE.LAST_STAND_HARD) or state.isInUnit(PREBATTLE_TYPE.LAST_STAND))

    def selectRandomMode(self):
        self.__selectMode(PREBATTLE_ACTION_NAME.RANDOM)

    @prbEntityProperty
    def prbEntity(self):
        pass

    def selectVehicle(self, invID):
        if not self.isEventPrb():
            return
        else:
            dispatcher = self.prbDispatcher
            if dispatcher is None:
                return
            entity = dispatcher.getEntity()
            if entity and isinstance(entity, (LastStandEntity, LastStandSquadEntity)):
                entity.selectModeVehicle(invID)
            return

    def getVehiclesConfig(self):
        limits = self.getModeSettings().vehicles
        return _VehiclesConfig(limits.get('allowedVehicles', []), limits.get('allowedLevels', []), limits.get('forbiddenClassTags', []), limits.get('forbiddenVehicles', []))

    def getSuitableVehicles(self):
        vehConfig = self.getVehiclesConfig()
        criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(vehConfig.allowedVehicles)
        lsVehicles = set(self.__itemsCache.items.getVehicles(criteria).values())
        criteria = REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.HAS_ANY_TAG(FORBIDDEN_VEHICLE_TAGS)
        if vehConfig.allowedLevels:
            criteria |= REQ_CRITERIA.VEHICLE.LEVELS(vehConfig.allowedLevels)
        if vehConfig.forbiddenVehicles:
            criteria |= ~REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(vehConfig.forbiddenVehicles)
        if vehConfig.forbiddenClassTags:
            criteria |= ~REQ_CRITERIA.VEHICLE.CLASSES(vehConfig.forbiddenClassTags)
        lsVehicles.update(self.__itemsCache.items.getVehicles(criteria).values())
        return lsVehicles

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__updateEventBattlesSettings
        return

    def __onHangarLoadedAfterLogin(self):
        if self.isPromoScreenEnabled():
            showPromoWindowView()
        if self.isEventPrb():
            cameraManager = CGF.getManager(self.__hangarSpace.spaceID, HangarCameraManager)
            if cameraManager:
                cameraManager.enablePlatoonMode(False)

    def __updateEventBattlesSettings(self, diff):
        if LAST_STAND_GAME_PARAMS_KEY in diff:
            self.startNotification()
            self.onSettingsUpdate()
            if not self.isAvailable():
                self.__closeLSViews()
                self.onEventDisabled()
                WWISE.deactivateRemapping(LS_SOUND_REMAPPING)
            else:
                WWISE.activateRemapping(LS_SOUND_REMAPPING)
            self.__updateStates()

    def __updateStates(self):
        wasEnabled, wasBattlesEnabled = self._prevStates
        modeSettings = self.getModeSettings()
        isEnabled, isBattlesEnabled = self._prevStates = (modeSettings.isEnabled, modeSettings.isBattlesEnabled.copy())
        if self.__getTimer() is None:
            return
        else:
            systemMessages = []
            for queueType, queueTypeEnabled in isBattlesEnabled.items():
                if wasBattlesEnabled.get(queueType, False) and not queueTypeEnabled:
                    systemMessages.append(backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.switchedOffDifficulty(), difficulty=self.__getQueueTypeLocalizedName(queueType)))

            if len(systemMessages) == len(isBattlesEnabled):
                systemMessages = [backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.switchedOff())]
            if wasEnabled != isEnabled and not isEnabled:
                systemMessages.append(backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.switchedOffFull()))
            for message in systemMessages:
                SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Error, priority=NotificationPriorityLevel.MEDIUM)

            return

    def __clear(self):
        self.stopNotification()
        self.stopGlobalListening()
        g_eventBus.removeListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onSelectVehicleInHangar, scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = None
        WWISE.deactivateRemapping(LS_SOUND_REMAPPING)
        return

    def __getTimer(self):
        endDate = self.getModeSettings().endDate
        now = time_utils.getCurrentLocalServerTimestamp()
        timeLeft = endDate - now
        return timeLeft + 1 if timeLeft > 0 else None

    def __timerUpdate(self):
        self.__closeLSViews()
        self.onEventDisabled()

    def __closeLSViews(self):
        if not self.isEventPrb():
            return
        closeViewsByID([R.views.dialogs.DefaultDialog(),
         R.views.lobby.tanksetup.dialogs.Confirm(),
         R.views.lobby.tanksetup.dialogs.ConfirmActionsWithEquipmentDialog(),
         R.views.lobby.tanksetup.dialogs.ExchangeToBuyItems()])

    def __onSelectVehicleInHangar(self, event):
        if not self.isEventPrb():
            return
        vehicleInvID = event.ctx['vehicleInvID']
        vehicle = self.__itemsCache.items.getVehicle(vehicleInvID)
        if vehicle:
            self.selectRandomMode()

    @adisp.adisp_process
    def __selectMode(self, name):
        dispatcher = self.prbDispatcher
        if dispatcher is None:
            return
        else:
            isLastStand = name == PREBATTLE_ACTION_NAME.LAST_STAND
            yield dispatcher.doSelectAction(PrbAction(name), fadeCtx={'layer': WindowLayer.OVERLAY,
             'waitForLayoutReady': R.views.last_stand.mono.lobby.hangar() if isLastStand else None})
            return

    @staticmethod
    def __getQueueTypeLocalizedName(queueType):
        difficultyLevel = QUEUE_TYPE_TO_DIFFICULTY_LEVEL[queueType].value
        return backport.text(R.strings.last_stand_lobby.difficult.dyn('level_{}'.format(difficultyLevel))())
