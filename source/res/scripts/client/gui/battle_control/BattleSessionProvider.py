# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/BattleSessionProvider.py
from collections import namedtuple
import weakref
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG
from adisp import async
from gui.battle_control import consumables, vehicle_state_ctrl
from gui.battle_control.avatar_stats_controller import AvatarStatsController
from gui.battle_control.BattleContext import BattleContext
from gui.battle_control.RespawnsController import RespawnsController
from gui.battle_control.NotificationsController import NotificationsController
from gui.battle_control.arena_info import getClientArena
from gui.battle_control.avatar_getter import leaveArena
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.battle_feedback import createFeedbackAdaptor
from gui.battle_control.battle_msgs_ctrl import createBattleMessagesCtrl
from gui.battle_control.battle_period_ctrl import createPeriodCtrl
from gui.battle_control.battle_team_bases_ctrl import createTeamsBasesCtrl
from gui.battle_control.ChatCommandsController import ChatCommandsController
from gui.battle_control.ArenaLoadController import ArenaLoadController
from gui.battle_control.DRRScaleController import DRRScaleController
from gui.battle_control.RepairController import RepairController
from gui.battle_control.arena_info.ArenaDataProvider import ArenaDataProvider
from gui.battle_control.arena_info.listeners import ListenersCollection
from gui.battle_control.dyn_squad_functional import DynSquadFunctional
from gui.battle_control.gas_attack_controller import GasAttackController
from gui.battle_control.hit_direction_ctrl import HitDirectionController
from gui.battle_control.requests import AvatarRequestsController
from gui.battle_control.first_of_april_controller import FirstOfAprilController
BattleSessionProviderStartCtx = namedtuple('BattleSessionProviderStartCtx', ('avatar', 'replayCtrl', 'gasAttackMgr'))
BattleSessionProviderStartCtx.__new__.__defaults__ = (None, None, None)

class BattleSessionProvider(object):
    __slots__ = ('__ammoCtrl', '__equipmentsCtrl', '__optDevicesCtrl', '__vehicleStateCtrl', '__chatCommands', '__drrScaleCtrl', '__feedback', '__ctx', '__arenaDP', '__arenaListeners', '__arenaLoadCtrl', '__respawnsCtrl', '__notificationsCtrl', '__isBattleUILoaded', '__arenaTeamsBasesCtrl', '__periodCtrl', '__messagesCtrl', '__repairCtrl', '__hitDirectionCtrl', '__requestsCtrl', '__avatarStatsCtrl', '__dynSquadFunctional', '__weakref__', '__gasAttackCtrl', '__firstOfAprilCtrl')

    def __init__(self):
        super(BattleSessionProvider, self).__init__()
        self.__ctx = BattleContext()
        self.__ammoCtrl = None
        self.__equipmentsCtrl = None
        self.__optDevicesCtrl = None
        self.__vehicleStateCtrl = None
        self.__chatCommands = None
        self.__drrScaleCtrl = None
        self.__feedback = None
        self.__messagesCtrl = None
        self.__hitDirectionCtrl = None
        self.__requestsCtrl = None
        self.__arenaDP = None
        self.__arenaLoadCtrl = None
        self.__arenaTeamsBasesCtrl = None
        self.__periodCtrl = None
        self.__respawnsCtrl = None
        self.__notificationsCtrl = None
        self.__repairCtrl = None
        self.__dynSquadFunctional = None
        self.__avatarStatsCtrl = None
        self.__arenaListeners = None
        self.__firstOfAprilCtrl = None
        self.__isBattleUILoaded = False
        self.__gasAttackCtrl = None
        return

    def isBattleUILoaded(self):
        return self.__isBattleUILoaded

    def getCtx(self):
        return self.__ctx

    def getAmmoCtrl(self):
        return self.__ammoCtrl

    def getEquipmentsCtrl(self):
        return self.__equipmentsCtrl

    def getOptDevicesCtrl(self):
        return self.__optDevicesCtrl

    def getVehicleStateCtrl(self):
        return self.__vehicleStateCtrl

    def getChatCommands(self):
        return self.__chatCommands

    def getDrrScaleCtrl(self):
        return self.__drrScaleCtrl

    def getRespawnsCtrl(self):
        return self.__respawnsCtrl

    def getNotificationsCtrl(self):
        return self.__notificationsCtrl

    def getRepairCtrl(self):
        return self.__repairCtrl

    def getFeedback(self):
        return self.__feedback

    def getBattleMessagesCtrl(self):
        return self.__messagesCtrl

    def getHitDirectionCtrl(self):
        return self.__hitDirectionCtrl

    def getAvatarStatsCtrl(self):
        return self.__avatarStatsCtrl

    def getArenaTeamsBasesCtrl(self):
        return self.__arenaTeamsBasesCtrl

    def getPeriodCtrl(self):
        return self.__periodCtrl

    def getGasAttackCtrl(self):
        return self.__gasAttackCtrl

    def getFirstOfAprilCtrl(self):
        return self.__firstOfAprilCtrl

    @async
    def sendRequest(self, ctx, callback, allowDelay=None):
        self.__requestsCtrl.request(ctx, callback=callback, allowDelay=allowDelay)

    def setPlayerVehicle(self, vID, vDesc):
        self.__ammoCtrl.setGunSettings(vDesc.gun)
        self.__vehicleStateCtrl.setPlayerVehicle(vID)
        self.__feedback.setPlayerVehicle(vID)
        self.__respawnsCtrl.spawnVehicle(vID)

    def setAimOffset(self, offset):
        if self.__hitDirectionCtrl is not None:
            self.__hitDirectionCtrl.setOffset(offset)
        return

    def setAimPositionUpdated(self, mode, x, y):
        if self.__feedback is not None:
            self.__feedback.setAimPositionUpdated(mode, x, y)
        return

    def getArenaDP(self):
        return self.__arenaDP

    def addArenaCtrl(self, controller):
        if self.__arenaListeners:
            self.__arenaListeners.addController(weakref.proxy(self.__ctx), controller)

    def removeArenaCtrl(self, controller):
        if self.__arenaListeners:
            self.__arenaListeners.removeController(controller)

    def start(self, startCtx=None):
        isReplayRecording = startCtx.replayCtrl.isRecording
        isReplayPlaying = startCtx.replayCtrl.isPlaying
        self.__arenaDP = ArenaDataProvider(avatar=startCtx.avatar)
        self.__ctx.start(self.__arenaDP)
        self.__ammoCtrl = consumables.createAmmoCtrl(isReplayPlaying, isReplayRecording)
        self.__equipmentsCtrl = consumables.createEquipmentCtrl(isReplayPlaying)
        self.__optDevicesCtrl = consumables.createOptDevicesCtrl()
        self.__vehicleStateCtrl = vehicle_state_ctrl.createCtrl(isReplayRecording)
        isMultiTeam = self.__arenaDP.isMultipleTeams()
        self.__arenaLoadCtrl = ArenaLoadController(isMultiTeam)
        self.__arenaTeamsBasesCtrl = createTeamsBasesCtrl(isReplayPlaying)
        self.__periodCtrl = createPeriodCtrl(isReplayPlaying, isReplayRecording)
        self.__drrScaleCtrl = DRRScaleController()
        self.__respawnsCtrl = RespawnsController(startCtx)
        self.__repairCtrl = RepairController()
        self.__dynSquadFunctional = DynSquadFunctional(isReplayPlaying)
        self.__notificationsCtrl = NotificationsController(self.__arenaDP)
        self.__gasAttackCtrl = GasAttackController(startCtx)
        self.__firstOfAprilCtrl = FirstOfAprilController()
        ctx = weakref.proxy(self.__ctx)
        self.__arenaListeners = ListenersCollection()
        self.__arenaListeners.addController(ctx, self.__arenaLoadCtrl)
        self.__arenaListeners.addController(ctx, self.__arenaTeamsBasesCtrl)
        self.__arenaListeners.addController(ctx, self.__periodCtrl)
        self.__arenaListeners.addController(ctx, self.__respawnsCtrl)
        self.__arenaListeners.addController(ctx, self.__firstOfAprilCtrl)
        self.__arenaListeners.start(startCtx.avatar.arena, arenaDP=self.__arenaDP)
        self.__feedback = createFeedbackAdaptor(isReplayPlaying)
        self.__feedback.start(self.__arenaDP)
        self.__messagesCtrl = createBattleMessagesCtrl(isReplayPlaying)
        self.__messagesCtrl.start(ctx)
        self.__hitDirectionCtrl = HitDirectionController()
        self.__hitDirectionCtrl.start()
        g_playerEvents.onBattleResultsReceived += self.__pe_onBattleResultsReceived
        self.__chatCommands = ChatCommandsController()
        self.__chatCommands.start(self.__arenaDP, self.__feedback)
        self.__requestsCtrl = AvatarRequestsController()
        self.__avatarStatsCtrl = AvatarStatsController()

    def stop(self):
        g_playerEvents.onBattleResultsReceived -= self.__pe_onBattleResultsReceived
        if self.__requestsCtrl:
            self.__requestsCtrl.fini()
            self.__requestsCtrl = None
        if self.__ammoCtrl:
            self.__ammoCtrl.clear()
            self.__ammoCtrl = None
        if self.__equipmentsCtrl:
            self.__equipmentsCtrl.clear()
            self.__equipmentsCtrl = None
        if self.__optDevicesCtrl:
            self.__optDevicesCtrl.clear()
            self.__optDevicesCtrl = None
        if self.__vehicleStateCtrl:
            self.__vehicleStateCtrl.clear()
            self.__vehicleStateCtrl = None
        if self.__arenaListeners is not None:
            self.__arenaListeners.stop()
            self.__arenaListeners = None
        if self.__feedback is not None:
            self.__feedback.stop()
            self.__feedback = None
        if self.__messagesCtrl is not None:
            self.__messagesCtrl.stop()
            self.__messagesCtrl = None
        if self.__hitDirectionCtrl is not None:
            self.__hitDirectionCtrl.stop()
            self.__hitDirectionCtrl = None
        if self.__arenaDP is not None:
            self.__arenaDP.clear()
            self.__arenaDP = None
        if self.__chatCommands is not None:
            self.__chatCommands.stop()
            self.__chatCommands = None
        self.__drrScaleCtrl = None
        self.__arenaLoadCtrl = None
        self.__arenaTeamsBasesCtrl = None
        self.__periodCtrl = None
        self.__respawnsCtrl = None
        self.__notificationsCtrl = None
        self.__repairCtrl = None
        self.__gasAttackCtrl = None
        self.__firstOfAprilCtrl = None
        self.__dynSquadFunctional = None
        if self.__avatarStatsCtrl is not None:
            self.__avatarStatsCtrl.stop()
            self.__avatarStatsCtrl = None
        self.__ctx.stop()
        return

    def setBattleUI(self, battleUI):
        assert not self.__isBattleUILoaded, 'Battle UI already is set'
        self.__isBattleUILoaded = True
        self.__arenaTeamsBasesCtrl.setUI(battleUI.getTeamBasesPanel())
        self.__periodCtrl.setUI(battleUI.getBattleTimer(), battleUI.getPreBattleTimer(), battleUI.getPlayersPanelsSwitcher())
        self.__hitDirectionCtrl.setUI(battleUI.getIndicators())
        self.__drrScaleCtrl.start(battleUI)
        self.__dynSquadFunctional.setUI(battleUI, self)

    def clearBattleUI(self):
        self.__isBattleUILoaded = False
        self.__arenaTeamsBasesCtrl.clearUI()
        self.__periodCtrl.clearUI()
        self.__hitDirectionCtrl.clearUI()
        self.__drrScaleCtrl.stop()
        self.__dynSquadFunctional.clearUI(self)

    def switchToPostmortem(self):
        self.__ammoCtrl.clear()
        self.__equipmentsCtrl.clear()
        self.__optDevicesCtrl.clear()
        self.__gasAttackCtrl.clear()
        self.__feedback.setPlayerVehicle(0)
        self.__vehicleStateCtrl.switchToPostmortem()

    def useLoaderIntuition(self):
        self.__messagesCtrl.showVehicleMessage('LOADER_INTUITION_WAS_USED')
        self.__ammoCtrl.useLoaderIntuition()

    def movingToRespawnBase(self):
        self.__ammoCtrl.clear(False)
        self.__equipmentsCtrl.clear(False)
        self.__optDevicesCtrl.clear(False)
        self.__vehicleStateCtrl.movingToRespawn()
        self.__respawnsCtrl.movingToRespawn()

    def invalidateVehicleState(self, state, value, vehicleID=0):
        self.__vehicleStateCtrl.invalidate(state, value, vehicleID)
        if state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__ammoCtrl.clear(False)
            self.__equipmentsCtrl.clear(False)

    def repairPointAction(self, repairPointIndex, action, nextActionTime):
        self.__repairCtrl.action(repairPointIndex, action, nextActionTime)

    def updateAvatarPrivateStats(self, stats):
        self.__avatarStatsCtrl.update(stats)

    def addHitDirection(self, hitDirYaw, isDamage):
        self.__hitDirectionCtrl.addHit(hitDirYaw, isDamage)

    def __pe_onBattleResultsReceived(self, isActiveVehicle, _):
        if isActiveVehicle:
            arena = getClientArena()
            LOG_DEBUG('Try to exit from arena', arena)
            if arena:
                self.__ctx.lastArenaUniqueID = arena.arenaUniqueID
            leaveArena()
