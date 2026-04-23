# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/w2gt/w2gt_ctrl.py
import enum
import logging
import typing
import ArenaType
import BigWorld
from Event import Event, EventManager
from client_request_lib.exceptions import ResponseCodes
from constants import ARENA_PERIOD, ROLE_TYPE_TO_LABEL, ROLE_TYPE
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IW2GTBattleController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.w2gt.w2gt_data_mgr import W2GTDataMgr, W2gtProgress
from gui.battle_control.controllers.w2gt.w2gt_plugin import W2GTPlugin
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers import dependency
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_messages import ClientActionMessage, ACTION_MESSAGE_TYPE
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IW2GTGameController
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
    from typing import Optional, Dict
    from gui.game_control.w2gt_controller import _W2gtResponseData
_logger = logging.getLogger(__name__)
_NOT_MODIFIED_CODE = 304
_DEFAULT_VEHICLE_ROLE = {VEHICLE_CLASS_NAME.LIGHT_TANK: ROLE_TYPE_TO_LABEL[ROLE_TYPE.LT_UNIVERSAL],
 VEHICLE_CLASS_NAME.MEDIUM_TANK: ROLE_TYPE_TO_LABEL[ROLE_TYPE.MT_UNIVERSAL],
 VEHICLE_CLASS_NAME.HEAVY_TANK: ROLE_TYPE_TO_LABEL[ROLE_TYPE.HT_UNIVERSAL],
 VEHICLE_CLASS_NAME.SPG: ROLE_TYPE_TO_LABEL[ROLE_TYPE.SPG],
 VEHICLE_CLASS_NAME.AT_SPG: ROLE_TYPE_TO_LABEL[ROLE_TYPE.ATSPG_UNIVERSAL]}

class _RequestState(enum.IntEnum):
    NONE = 1
    IN_PROGRESS = 2
    RECEIVED = 3


class W2GTBattleController(IW2GTBattleController):
    __w2gtGameCtrl = dependency.descriptor(IW2GTGameController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__period = None
        self.__periodStartTime = None
        self.__playerVehicleID = 0
        self.__ownVehicle = None
        self.__plugin = None
        self.__receivedData = None
        self.__arenaUniqueID = None
        self.__progress = None
        self.__spaceLoaded = False
        self.__requestState = _RequestState.NONE
        self.__isPlayerAlive = True
        self.__isActive = False
        self.__postponedClientMessages = None
        self.__em = EventManager()
        self.onStageChanged = Event(self.__em)
        return

    @property
    def isActive(self):
        return self.__isActive

    def startControl(self, *args):
        self.__postponedClientMessages = []
        self.__period = ARENA_PERIOD.IDLE
        self.__periodStartTime = BigWorld.serverTime()
        self.__progress = W2gtProgress()
        self.__settingsCore.serverSettings.settingsCache.onSyncCompleted += self.__onServerSettingsSyncCompleted

    def stopControl(self):
        self.__clear()

    def getControllerID(self):
        return BATTLE_CTRL_ID.W2GT_CTRL

    def isArenaSuitable(self, arena):
        if arena is not None and arena.arenaType is not None:
            gameplayType = ArenaType.getGameplayName(arena.arenaType.gameplayID)
            return gameplayType == 'ctf'
        else:
            return False

    def spaceLoadCompleted(self):
        self.__spaceLoaded = True
        self.__tryInitializeData()

    def invalidateArenaInfo(self):
        self.__tryInitializeData()

    def invalidateVehiclesInfo(self, arenaDP):
        self.__tryInitializeData()

    def invalidateVehicleStatus(self, flags, vInfo, arenaDP):
        if vInfo.isObserver():
            return
        vehicleID = vInfo.vehicleID
        if vehicleID == self.__playerVehicleID and not vInfo.isAlive():
            self.__isPlayerAlive = False
            if self.__plugin:
                self.__plugin.setDestroyed()

    def setPeriodInfo(self, period, endTime, length, additionalInfo):
        self.__period = period
        self.__periodStartTime = endTime - length
        if self.__plugin:
            self.__plugin.updatePeriod(period)

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        self.__period = period
        self.__periodStartTime = endTime - length
        if self.__plugin:
            self.__plugin.updatePeriod(period)
        if period == ARENA_PERIOD.PREBATTLE:
            self.__sendClientMessages()

    @wg_async
    def __tryInitializeData(self):
        if self.__isActive:
            return
        elif BigWorld.player().isObserver():
            _logger.debug("Can't initialize W2GT request. Player is Observer")
            return
        elif self.__period > ARENA_PERIOD.BATTLE:
            _logger.debug("Can't make request for W2GT. Time to make it is over")
            return
        elif not self.__settingsCore.serverSettings.settingsCache.isSynced():
            _logger.debug('Server settings is not ready yet')
            return
        elif not self.__w2gtGameCtrl.isEnabled:
            _logger.debug('W2GT is disabled in server settings')
            return
        else:
            if self.__ownVehicle is None:
                playerVehicleID = avatar_getter.getPlayerVehicleID()
                ownVehicle = BigWorld.entity(playerVehicleID)
                if ownVehicle is None or not ownVehicle.isPlayerVehicle:
                    _logger.debug("Can't collect data for W2GT request. Player vehicle hasn't not ready yet")
                    return
                self.__playerVehicleID = playerVehicleID
                self.__ownVehicle = ownVehicle
            arena = avatar_getter.getArena()
            if self.__arenaUniqueID is None:
                if not self.isArenaSuitable(arena):
                    _logger.debug('Arena is not supported for W2GT')
                    return
                self.__arenaUniqueID = arena.arenaUniqueID
            savedProgress = self.__w2gtGameCtrl.getProgress(self.__arenaUniqueID, self.__playerVehicleID)
            self.__progress = W2gtProgress(**savedProgress)
            if self.__period == ARENA_PERIOD.BATTLE and not self.__progress.isCapable:
                return
            if self.__requestState == _RequestState.NONE:
                self.__requestState = _RequestState.IN_PROGRESS
                team = avatar_getter.getPlayerTeam()
                vehTypeDescriptor = self.__ownVehicle.typeDescriptor
                vehRole = self.__getVehicleRole(vehTypeDescriptor)
                vehLevel = vehTypeDescriptor.level
                data = yield wg_await(self.__w2gtGameCtrl.getTips(arena.arenaType.geometryName, arena.arenaType.gameplayID, vehRole, vehLevel, team))
                self.__receivedData = data
                self.__requestState = _RequestState.RECEIVED
            else:
                _logger.debug('Request for W2GT data is in progress or already has done')
            if self.__period > ARENA_PERIOD.BATTLE:
                _logger.debug('Time getting data response is over for W2GT')
                return
            self.__tryRun()
            return

    def __tryRun(self):
        isActive = self.__receivedData is not None and self.__spaceLoaded and self.__plugin is None and self.__ownVehicle is not None
        if not self.__isActive and isActive and self.__isPlayerAlive:
            self.__isActive = isActive
            if not self.__receivedData.success:
                _logger.debug('Invalid data response for W2GT')
                if self.__receivedData.responseCode in (ResponseCodes.NO_ERRORS, _NOT_MODIFIED_CODE):
                    msgAccessor = R.strings.ingame_gui.battleMessenger.w2gt.warning.noData
                else:
                    msgAccessor = R.strings.ingame_gui.battleMessenger.w2gt.warning.gettingDataError
                message = ClientActionMessage(msg=backport.text(msgAccessor()), type_=ACTION_MESSAGE_TYPE.WARNING)
                if self.__period >= ARENA_PERIOD.PREBATTLE:
                    g_messengerEvents.onCustomMessage(message)
                else:
                    self.__postponedClientMessages.append(message)
                return
            dataMgr = W2GTDataMgr()
            dataMgr.init(self.__receivedData, self.__progress, self.__w2gtGameCtrl.w2gtConfig)
            if not dataMgr.zones:
                _logger.warning("Invalid data for W2GT. Zones weren't found")
                return
            self.__plugin = W2GTPlugin()
            self.__plugin.onStagePluginChanged += self.__onPluginStageChanged
            self.__plugin.initialize(dataMgr, self.__period, self.__periodStartTime)
        return

    def __sendClientMessages(self):
        messages = self.__postponedClientMessages[:]
        for message in messages:
            g_messengerEvents.onCustomMessage(message)
            self.__postponedClientMessages.remove(message)

    def __onPluginStageChanged(self, stageID, ctx):
        self.__progress = self.__progress.replace(stageID=stageID, startTime=BigWorld.serverTime(), ctx=ctx)
        self.__w2gtGameCtrl.saveProgress(self.__arenaUniqueID, self.__playerVehicleID, self.__progress)
        self.onStageChanged(stageID)

    def __onServerSettingsSyncCompleted(self):
        self.__tryInitializeData()

    def __getVehicleRole(self, vehTypeDescriptor):
        role = ROLE_TYPE_TO_LABEL.get(vehTypeDescriptor.role)
        return _DEFAULT_VEHICLE_ROLE.get(vehTypeDescriptor.type.classTag, '') if not role or role == ROLE_TYPE_TO_LABEL[ROLE_TYPE.NOT_DEFINED] else role

    def __clear(self):
        self.__em.clear()
        self.__settingsCore.serverSettings.settingsCache.onSyncCompleted -= self.__onServerSettingsSyncCompleted
        self.__requestState = _RequestState.NONE
        self.__receivedData = None
        self.__arenaUniqueID = None
        self.__progress = None
        self.__isActive = False
        self.__postponedClientMessages = None
        if self.__plugin:
            self.__plugin.onStagePluginChanged -= self.__onPluginStageChanged
            self.__plugin.clear()
            self.__plugin = None
        self.__spaceLoaded = False
        self.__period = ARENA_PERIOD.IDLE
        self.__playerVehicleID = 0
        self.__ownVehicle = None
        self.__isPlayerAlive = True
        return
