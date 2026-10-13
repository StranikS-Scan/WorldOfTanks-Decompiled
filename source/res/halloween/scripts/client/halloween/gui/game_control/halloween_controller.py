# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/game_control/halloween_controller.py
from __future__ import absolute_import
from collections import namedtuple
import CGF
import typing
from account_helpers.AccountSettings import CURRENT_VEHICLE
import Event
import adisp
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from cgf_components.hangar_camera_manager import HangarCameraSystem
from constants import EVENT_CLIENT_DATA
from frameworks.wulf import WindowLayer
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.game_control.season_provider import SeasonProvider
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar as showMainHangar
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.system_factory import collectIgnoredModeForAutoSelectVehicle
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from halloween.gui.halloween_gui_constants import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, QUEUE_TYPE_TO_DIFFICULTY_LEVEL
from halloween.gui.prb_control.entities.pre_queue.entity import HalloweenEntity
from halloween.gui.prb_control.entities.squad.entity import HalloweenSquadEntity
from halloween.gui.shared.event_dispatcher import closeViewsByID, showHangar
from halloween.gui.shared.event_dispatcher import showPromoWindowView
from halloween.gui.shared.utils.performance_analyzer import PerformanceAnalyzerMixin
from halloween.skeletons.difficulty_level_controller import IDifficultyLevelController
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.uilogging.loggers import HWMetricsLogger
from halloween.uilogging.logging_constants import HWLogKeys
from halloween_common.configs.halloween_gsw import GSWSchema
from halloween_common.halloween_constants import HALLOWEEN_GAME_PARAMS_KEY
from halloween_common.halloween_constants import HALLOWEEN_QUESTS_PREFFIX, QUEUE_TYPE, PREBATTLE_TYPE
from helpers import dependency, time_utils
from shared_utils import makeTupleByDict
from skeletons.gui.game_control import IHangarLoadingController
from skeletons.gui.game_control import IReferralProgramController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    from gui.shared.events import GUICommonEvent
    from halloween_common.configs.halloween_gsw import GSWModel

class _HalloweenConfig(namedtuple('_HalloweenConfig', ('isEnabled', 'isBattlesEnabled', 'startDate', 'endDate', 'artefactsSettings', 'vehicles', 'rent', 'shop', 'isPromoScreenEnabled', 'isIntroVideoEnabled', 'isOutroVideoEnabled', 'isInfoPageEnabled', 'isInfoMetaEnabled', 'modeSelectorShowRewards', 'twitch_con', 'prominentBonus', 'battleQueue'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, isBattlesEnabled={}, startDate=0, endDate=0, artefactsSettings={}, rent={}, vehicles=[], shop={}, isPromoScreenEnabled=False, isIntroVideoEnabled=False, isOutroVideoEnabled=False, isInfoPageEnabled=False, isInfoMetaEnabled=False, modeSelectorShowRewards={}, twitch_con={}, prominentBonus={}, battleQueue={})
        defaults.update(kwargs)
        return super(_HalloweenConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.items() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class HalloweenController(IHalloweenController, Notifiable, SeasonProvider, IGlobalListener, PerformanceAnalyzerMixin):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarLoadingController = dependency.descriptor(IHangarLoadingController)
    __referralCtrl = dependency.descriptor(IReferralProgramController)
    __difficultyLevelCtrl = dependency.descriptor(IDifficultyLevelController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(HalloweenController, self).__init__()
        self.__serverSettings = None
        self._prevStates = (False, {})
        self._hwQuestsCache = {}
        self.onEventDisabled = Event.Event()
        self.onSettingsUpdate = Event.Event()
        self.__uiLogger = HWMetricsLogger(HWLogKeys.RANDOM_LOBBY)
        return

    def init(self):
        super(HalloweenController, self).init()
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
        super(HalloweenController, self).fini()

    def onDisconnected(self):
        super(HalloweenController, self).onDisconnected()
        self._prevStates = (False, {})
        self.__clear()

    def onAvatarBecomePlayer(self):
        super(HalloweenController, self).onAvatarBecomePlayer()
        self.__clear()

    def onAccountBecomePlayer(self):
        super(HalloweenController, self).onAccountBecomePlayer()
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())

    def onLobbyInited(self, event):
        super(HalloweenController, self).onLobbyInited(event)
        self.startNotification()
        g_clientUpdateManager.addCallbacks({'eventsData.' + str(EVENT_CLIENT_DATA.QUEST): self.__initHWQuestsCache})
        g_eventBus.addListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onSelectVehicleInHangar, scope=EVENT_BUS_SCOPE.LOBBY)
        self.startGlobalListening()
        if not self.isAvailable() and self.isEventPrb():
            self.selectRandomMode()

    def onLobbyStarted(self, ctx):
        super(HalloweenController, self).onLobbyStarted(ctx)
        self.__initHWQuestsCache()

    def onPrbEntitySwitched(self):
        self.__referralCtrl.setReferralHardDisabled(self.isEventPrb())
        if not any((self.prbEntity.getModeFlags() & flag for flag in collectIgnoredModeForAutoSelectVehicle())):
            g_currentVehicle.selectVehicle(AccountSettings.getFavorites(CURRENT_VEHICLE))
        if isinstance(self.prbEntity, HalloweenEntity):
            accountSelectedLevel = self.__difficultyLevelCtrl.getLastSelectedLevel()
            self.__difficultyLevelCtrl.selectLevel(accountSelectedLevel)
        if self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.STRONGHOLD:
            showMainHangar()

    def isEnabled(self):
        return self.getModeSettings().isEnabled

    def isBattlesEnabled(self):
        currentQueueType = self.prbEntity.currentQueueType if self.prbEntity is not None else QUEUE_TYPE.UNKNOWN
        return self.getModeSettings().isBattlesEnabled.get(currentQueueType, False)

    def isPromoScreenEnabled(self):
        return self.getModeSettings().isPromoScreenEnabled and self.isEnabled()

    def isIntroVideoEnabled(self):
        return self.getModeSettings().isIntroVideoEnabled and self.isEnabled()

    def isOutroVideoEnabled(self):
        return self.getModeSettings().isOutroVideoEnabled and self.isEnabled()

    def isInfoPageEnabled(self):
        return self.getModeSettings().isInfoPageEnabled and self.isEnabled()

    def isInfoMetaEnabled(self):
        return self.getModeSettings().isInfoMetaEnabled and self.isEnabled()

    def isAvailable(self):
        return self.isEnabled() and self.__getTimer() is not None

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().getSettings().get(HALLOWEEN_GAME_PARAMS_KEY, {})

    @staticmethod
    def getGSWConfig():
        return GSWSchema.getModel()

    def getModeSettings(self):
        return makeTupleByDict(_HalloweenConfig, self.getConfig()) if self.getConfig() else _HalloweenConfig.defaults()

    def getHWQuestsCache(self):
        return self._hwQuestsCache

    def selectBattle(self, *args, **kwargs):
        source = kwargs.get('source')
        if source:
            self.__uiLogger.onClick(HWLogKeys.HW_ENTRY_POINT, source)
        self.__selectMode(PREBATTLE_ACTION_NAME.HALLOWEEN)

    def openHangar(self):
        if self.isEventPrb():
            showHangar()
        else:
            self.selectBattle()

    def isEventPrb(self):
        prbDispatcher = self.prbDispatcher
        state = prbDispatcher.getFunctionalState() if prbDispatcher is not None else None
        return state is not None and (state.isInPreQueue(QUEUE_TYPE.HALLOWEEN) or state.isInPreQueue(QUEUE_TYPE.HALLOWEEN_MEDIUM) or state.isInPreQueue(QUEUE_TYPE.HALLOWEEN_HARD) or state.isInUnit(PREBATTLE_TYPE.HALLOWEEN))

    def selectRandomMode(self):
        self.__selectMode(PREBATTLE_ACTION_NAME.RANDOM)

    @prbEntityProperty
    def prbEntity(self):
        pass

    @property
    def remainingEventSeconds(self):
        return self.__getTimer()

    def selectVehicle(self, invID):
        if not self.isEventPrb():
            return
        else:
            dispatcher = self.prbDispatcher
            if dispatcher is None:
                return
            entity = dispatcher.getEntity()
            if entity and isinstance(entity, (HalloweenEntity, HalloweenSquadEntity)):
                entity.selectModeVehicle(invID)
            return

    def hasAccessToVehicle(self, vehTypeCD):
        rentVehicles = self.getModeSettings().rent.get('vehicles', {})
        return True if vehTypeCD not in rentVehicles else any((self.__eventsCache.questsProgress.getTokenCount(accessToken) > 0 for accessToken in rentVehicles[vehTypeCD].values()))

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
            cameraManager = CGF.getSystem(self.__hangarSpace.spaceID, HangarCameraSystem)
            if cameraManager:
                cameraManager.enablePlatoonMode(False)

    def __updateEventBattlesSettings(self, diff):
        if HALLOWEEN_GAME_PARAMS_KEY in diff:
            self.startNotification()
            self.onSettingsUpdate()
            if not self.isAvailable():
                self.__closeHalloweenViews()
                self.onEventDisabled()
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
                    systemMessages.append(backport.text(R.strings.halloween_system_messages.serviceChannelMessages.switchedOffDifficulty(), difficulty=self.__getQueueTypeLocalizedName(queueType)))

            if len(isBattlesEnabled) == len(systemMessages) > 0:
                systemMessages = [backport.text(R.strings.halloween_system_messages.serviceChannelMessages.switchedOff())]
            if wasEnabled != isEnabled and not isEnabled:
                systemMessages.append(backport.text(R.strings.halloween_system_messages.serviceChannelMessages.switchedOffFull()))
            for message in systemMessages:
                SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Error, priority=NotificationPriorityLevel.MEDIUM)

            return

    def __clear(self):
        self.stopNotification()
        self.stopGlobalListening()
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_eventBus.removeListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onSelectVehicleInHangar, scope=EVENT_BUS_SCOPE.LOBBY)
        self._hwQuestsCache.clear()
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = None
        return

    def __initHWQuestsCache(self, *args, **kwargs):
        self._hwQuestsCache = self.__eventsCache.getAllQuests(filterFunc=lambda q: q.getID().startswith(HALLOWEEN_QUESTS_PREFFIX))

    def __getTimer(self):
        endDate = self.getModeSettings().endDate
        now = time_utils.getCurrentLocalServerTimestamp()
        timeLeft = endDate - now
        return timeLeft + 1 if timeLeft > 0 else None

    def __timerUpdate(self):
        self.__closeHalloweenViews()
        self.onEventDisabled()

    def __closeHalloweenViews(self):
        if not self.isEventPrb():
            return
        closeViewsByID([R.views.dialogs.DefaultDialog(),
         R.views.common.dialog_view.simple_dialog_content.SimpleDialogContent(),
         R.views.lobby.tanksetup.dialogs.Confirm(),
         R.views.lobby.tanksetup.dialogs.ConfirmActionsWithEquipmentDialog(),
         R.views.lobby.tanksetup.dialogs.ExchangeToBuyItems(),
         R.views.halloween.mono.lobby.dialogs.abilities_incomplete_confirm()])

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
            isHalloweenMode = name == PREBATTLE_ACTION_NAME.HALLOWEEN
            yield dispatcher.doSelectAction(PrbAction(name), fadeCtx={'layer': WindowLayer.OVERLAY,
             'waitForLayoutReady': R.views.halloween.mono.lobby.hangar() if isHalloweenMode else None})
            return

    @staticmethod
    def __getQueueTypeLocalizedName(queueType):
        difficultyLevel = QUEUE_TYPE_TO_DIFFICULTY_LEVEL[queueType].value
        return backport.text(R.strings.halloween_lobby.difficult.dyn('level_{}'.format(difficultyLevel))())
