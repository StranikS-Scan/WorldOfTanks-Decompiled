# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_session.py
import weakref
from collections import namedtuple
import BigWorld
import Event
import BattleReplay
from PlayerEvents import g_playerEvents
from adisp import adisp_async
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from debug_utils import LOG_DEBUG
from gui import g_tankActiveCamouflage
from gui.battle_control import arena_visitor
from gui.battle_control import avatar_getter
from gui.battle_control import controllers
from gui.battle_control.arena_info import invitations
from gui.battle_control.arena_info.arena_dp import ArenaDataProvider
from gui.battle_control.arena_info.listeners import ListenersCollection
from gui.battle_control.battle_cache import BattleClientCache
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.battle_constants import VIEW_COMPONENT_RULE
from gui.battle_control.battle_ctx import BattleContext
from gui.battle_control.requests import AvatarRequestsController
from gui.battle_control.view_components import createComponentsBridge
from items.components.c11n_constants import SeasonType
from skeletons.gui.battle_session import IBattleSessionProvider
BattleExitResult = namedtuple('BattleExitResult', 'isDeserter playerInfo')

class BattleSessionProvider(IBattleSessionProvider):
    __slots__ = ('__ctx', '__sharedRepo', '__dynamicRepo', '__requestsCtrl', '__arenaDP', '__arenaListeners', '__viewComponentsBridge', '__weakref__', '__arenaVisitor', '__invitations', '__isReplayPlaying', '__battleCache', 'onUpdateObservedVehicleData')

    def __init__(self):
        super(BattleSessionProvider, self).__init__()
        self.__ctx = BattleContext()
        self.__sharedRepo = controllers.SharedControllersLocator()
        self.__dynamicRepo = controllers.DynamicControllersLocator()
        self.__requestsCtrl = None
        self.__arenaDP = None
        self.__arenaVisitor = arena_visitor.createSkeleton()
        self.__arenaListeners = None
        self.__viewComponentsBridge = None
        self.__invitations = None
        self.__isReplayPlaying = False
        self.__battleCache = BattleClientCache()
        self.onBattleSessionStart = Event.Event()
        self.onBattleSessionStop = Event.Event()
        self.onUpdateObservedVehicleData = Event.Event()
        return

    @property
    def shared(self):
        return self.__sharedRepo

    @property
    def dynamic(self):
        return self.__dynamicRepo

    @property
    def arenaVisitor(self):
        return self.__arenaVisitor

    @property
    def invitations(self):
        return self.__invitations

    @property
    def battleCache(self):
        return self.__battleCache

    @property
    def isReplayPlaying(self):
        return self.__isReplayPlaying

    def getCtx(self):
        return self.__ctx

    @adisp_async
    def sendRequest(self, ctx, callback, allowDelay=None):
        self.__requestsCtrl.request(ctx, callback=callback, allowDelay=allowDelay)

    def setPlayerVehicle(self, vID, vDesc):
        ctrl = self.shared.prebattleSetups
        isSetupsSelectionStarted = ctrl.isSelectionStarted() if ctrl is not None else False
        ctrl = self.__sharedRepo.ammo
        if ctrl is not None:
            if not isSetupsSelectionStarted:
                ctrl.clearAmmo()
                ctrl.setGunSettings(vDesc.gun)
        ctrl = self.__sharedRepo.equipments
        if ctrl is not None:
            ctrl.notifyPlayerVehicleSet(vID)
        ctrl = self.__sharedRepo.vehicleState
        if ctrl is not None:
            ctrl.setPlayerVehicle(vID)
        ctrl = self.shared.prebattleSetups
        if ctrl is not None:
            ctrl.setPlayerVehicle(vID, vDesc)
        ctrl = self.__dynamicRepo.respawn
        if ctrl is not None:
            ctrl.spawnVehicle(vID)
        mapKind = self.__arenaVisitor.type.getVehicleCamouflageKind()
        g_tankActiveCamouflage[vDesc.type.compactDescr] = SeasonType.fromArenaKind(mapKind)
        return

    def switchVehicle(self, vehicleID):
        repo = self.shared
        if repo.vehicleState is not None and repo.vehicleState.getControllingVehicleID() != vehicleID:
            for ctrl in (repo.ammo, repo.equipments, repo.optionalDevices):
                if ctrl is not None:
                    ctrl.clear(False)

        repo.vehicleState.switchToOther(vehicleID)
        return

    def updateObservedVehicleData(self, vehicle):
        ammoCtrl = self.__sharedRepo.ammo
        if ammoCtrl is not None:
            ammoCtrl.clear(False)
            ammoCtrl.setGunSettings(vehicle.typeDescriptor.gun)
        ctrl = self.__sharedRepo.equipments
        if ctrl is not None:
            ctrl.clear(False)
        ctrl.notifyPlayerVehicleSet(vehicle.id)
        ctrl = self.__sharedRepo.optionalDevices
        if ctrl is not None:
            ctrl.clear(False)
        vehicle.ownVehicle.initialUpdate(force=True)
        self.updateVehicleEffects(vehicle)
        self.onUpdateObservedVehicleData(vehicle.id, None)
        return

    def updateVehicleEffects(self, vehicle):
        if vehicle is not None:
            vehicle.onDebuffEffectApplied(vehicle.debuff > 0)
            if vehicle.stunInfo > 0.0:
                vehicle.updateStunInfo()
            if vehicle.inspired:
                vehicle.set_inspired()
            if vehicle.healing:
                vehicle.set_healing()
        return

    def getArenaDP(self):
        return self.__arenaDP

    def addArenaCtrl(self, controller):
        return self.__arenaListeners.addController(controller) if self.__arenaListeners is not None else False

    def removeArenaCtrl(self, controller):
        if self.__arenaListeners is not None:
            self.__arenaListeners.removeController(controller)
        return

    def registerViewComponentsCtrl(self, controller):
        if self.__viewComponentsBridge is not None:
            self.__viewComponentsBridge.registerController(controller)
            return True
        else:
            return False

    def registerViewComponents(self, *data):
        if self.__viewComponentsBridge is not None:
            self.__viewComponentsBridge.registerViewComponents(*data)
            return True
        else:
            return False

    def addViewComponent(self, componentID, component, rule=VIEW_COMPONENT_RULE.PROXY):
        if self.__viewComponentsBridge is not None:
            self.__viewComponentsBridge.addViewComponent(componentID, component, rule=rule)
        return

    def removeViewComponent(self, componentID):
        if self.__viewComponentsBridge is not None:
            self.__viewComponentsBridge.removeViewComponent(componentID)
        return

    def getExitResult(self):
        if self.__isReplayPlaying or self.__arenaVisitor.gui.isTrainingBattle() or self.__arenaVisitor.gui.isMapsTraining() or self.__arenaVisitor.gui.isComp7Training():
            return BattleExitResult(False, None)
        else:
            vInfo = self.__arenaDP.getVehicleInfo()
            vStats = self.__arenaDP.getVehicleStats()
            if self.__arenaVisitor.hasRespawns():
                isDeserter = not vStats.stopRespawn
            else:
                player = BigWorld.player()
                hasLiftOver = ARENA_BONUS_TYPE_CAPS.checkAny(player.arenaBonusType, ARENA_BONUS_TYPE_CAPS.LIFT_OVER) if player else False
                isDeserter = avatar_getter.isVehicleAlive() and (not avatar_getter.isVehicleOverturned() or hasLiftOver)
            return BattleExitResult(isDeserter, vInfo.player)

    def exit(self):
        if self.__arenaVisitor.gui.isMapsTraining():
            self.__onMapsTrainingExit()
        avatar_getter.leaveArena()

    def start(self, setup):
        self.__isReplayPlaying = setup.isReplayPlaying
        self.__arenaVisitor = arena_visitor.createByAvatar(avatar=setup.avatar)
        setup.sessionProvider = weakref.proxy(self)
        self.__arenaDP = ArenaDataProvider(setup)
        self.__ctx.start(self.__arenaDP)
        self.__battleCache.load()
        self.__arenaListeners = ListenersCollection()
        self.__arenaListeners.start(setup)
        self.__viewComponentsBridge = createComponentsBridge()
        setup.sessionProvider = weakref.proxy(self)
        self.__sharedRepo = controllers.createShared(setup)
        self.__dynamicRepo = controllers.createDynamic(setup)
        self.__requestsCtrl = AvatarRequestsController()
        self.__invitations = invitations.createInvitationsHandler(setup)
        setup.clear()
        g_playerEvents.onBattleResultsReceived += self.__pe_onBattleResultsReceived
        self.onBattleSessionStart()

    def stop(self):
        self.onBattleSessionStop()
        g_playerEvents.onBattleResultsReceived -= self.__pe_onBattleResultsReceived
        if self.__viewComponentsBridge is not None:
            self.__viewComponentsBridge.clear()
            self.__viewComponentsBridge = None
        if self.__invitations is not None:
            self.__invitations.clear()
            self.__invitations = None
        if self.__requestsCtrl is not None:
            self.__requestsCtrl.fini()
            self.__requestsCtrl = None
        if self.__arenaListeners is not None:
            self.__arenaListeners.stop()
            self.__arenaListeners = None
        if self.__arenaDP is not None:
            self.__arenaDP.clear()
            self.__arenaDP = None
        self.__sharedRepo.destroy()
        self.__dynamicRepo.destroy()
        self.__arenaVisitor.clear()
        self.__arenaVisitor = arena_visitor.createSkeleton()
        self.__battleCache.clear()
        self.__ctx.stop()
        self.__isReplayPlaying = False
        return

    def switchToPostmortem(self, noRespawnPossible=True, respawnAvailable=False):
        ctrl = self.__sharedRepo.ammo
        if ctrl is not None:
            ctrl.clear(False)
        ctrl = self.__sharedRepo.equipments
        if ctrl is not None:
            ctrl.clear(False)
        ctrl = self.__sharedRepo.optionalDevices
        if ctrl is not None:
            ctrl.clear(False)
        ctrl = self.__sharedRepo.vehicleState
        if ctrl is not None:
            ctrl.switchToPostmortem(noRespawnPossible, respawnAvailable)
        return

    def updateVehicleQuickShellChanger(self, isActive):
        ammoCtrl = self.__sharedRepo.ammo
        if ammoCtrl is not None:
            ammoCtrl.updateVehicleQuickShellChanger(isActive)
        return

    def movingToRespawnBase(self, vehicle=None):
        ctrl = self.__sharedRepo.ammo
        if ctrl is not None:
            ctrl.clear(False)
            if vehicle:
                ctrl.setGunSettings(vehicle.typeDescriptor.gun)
        ctrl = self.__sharedRepo.equipments
        if ctrl is not None:
            ctrl.clear(False)
            if vehicle:
                ctrl.notifyPlayerVehicleSet(vehicle.id)
        ctrl = self.__sharedRepo.optionalDevices
        if ctrl is not None:
            ctrl.clear(False)
        ctrl = self.__sharedRepo.vehicleState
        if ctrl is not None:
            ctrl.movingToRespawn()
        ctrl = self.__dynamicRepo.respawn
        if ctrl is not None:
            ctrl.movingToRespawn()
        return

    def invalidateVehicleState(self, state, value, vehicleID=0):
        ctrl = self.__sharedRepo.vehicleState
        if ctrl is not None:
            ctrl.invalidate(state, value, vehicleID)
        if state == VEHICLE_VIEW_STATE.DESTROYED:
            ctrl = self.__sharedRepo.ammo
            if ctrl is not None:
                ctrl.clear(leave=False)
            ctrl = self.__sharedRepo.equipments
            if ctrl is not None:
                ctrl.clear(leave=False)
            ctrl = self.__sharedRepo.optionalDevices
            if ctrl is not None:
                ctrl.clear(leave=False)
        return

    def setVehicleHealth(self, isPlayerVehicle, vehicleID, newHealth, attackerID, attackReasonID):
        if not isPlayerVehicle:
            ctrl = self.__sharedRepo.feedback
            if ctrl is not None:
                ctrl.setVehicleNewHealth(vehicleID, newHealth, attackerID, attackReasonID)
        ctrl = self.__dynamicRepo.battleField
        if ctrl is not None:
            ctrl.setVehicleHealth(vehicleID, newHealth)
        return

    def repairPointAction(self, repairPointIndex, action, nextActionTime):
        ctrl = self.__dynamicRepo.repair
        if ctrl is not None:
            ctrl.action(repairPointIndex, action, nextActionTime)
        return

    def updateAvatarPrivateStats(self, stats):
        ctrl = self.__sharedRepo.privateStats
        if ctrl is not None:
            ctrl.update(stats)
        return

    def addHitDirection(self, hitDirYaw, attackerID, damage, isBlocked, critFlags, isHighExplosive, damagedID, attackReasonID):
        hitDirectionCtrl = self.__sharedRepo.hitDirection
        if hitDirectionCtrl is not None:
            hitDirectionCtrl.addHit(hitDirYaw, attackerID, damage, isBlocked, critFlags, isHighExplosive, damagedID, attackReasonID)
        return

    def startVehicleVisual(self, vProxy, isImmediate=False):
        vehicleID = vProxy.id
        ctrl = self.__sharedRepo.optionalDevices
        if ctrl is not None:
            ctrl.startVehicleVisual(vProxy, isImmediate)
        ctrl = self.__sharedRepo.feedback
        if ctrl is not None:
            ctrl.startVehicleVisual(vProxy, isImmediate)
        ctrl = self.__dynamicRepo.battleField
        if ctrl is not None:
            vehSwitchCtrl = self.__dynamicRepo.comp7PrebattleSetup
            vHealth = vehSwitchCtrl.getVehicleHealth(vProxy) if vehSwitchCtrl is not None else vProxy.health
            ctrl.setVehicleVisible(vehicleID, vHealth)
        ctrl = self.__sharedRepo.vehicleState
        if ctrl is not None and BigWorld.player().observedVehicleID == vehicleID:
            ctrl.refreshObserverVehicleVisual()
        return

    def stopVehicleVisual(self, vehicleID, isPlayerVehicle):
        ctrl = self.__sharedRepo.feedback
        if ctrl is not None:
            ctrl.stopVehicleVisual(vehicleID, isPlayerVehicle)
        ctrl = self.__dynamicRepo.battleField
        if ctrl is not None:
            ctrl.stopVehicleVisual(vehicleID)
        return

    def handleShortcutChatCommand(self, key):
        ctrl = self.__sharedRepo.chatCommands
        if ctrl is None:
            return
        else:
            if self.__arenaVisitor.gui.isInEpicRange():
                mapCtrl = self.dynamic.maps
                if not mapCtrl or mapCtrl.overviewMapScreenVisible:
                    return
            ctrl.handleShortcutChatCommand(key)
            return

    def handleContexChatCommand(self, key):
        ctrl = self.__sharedRepo.chatCommands
        if ctrl is None:
            return
        else:
            ctrl.handleContexChatCommand(key)
            return

    def __pe_onBattleResultsReceived(self, isActiveVehicle, _):
        if isActiveVehicle and not BattleReplay.g_replayCtrl.isPlaying:
            arenaUniqueID = self.__arenaVisitor.getArenaUniqueID()
            arenaBonusType = self.__arenaVisitor.getArenaBonusType()
            LOG_DEBUG('Try to exit from arena', arenaUniqueID, arenaBonusType)
            if arenaUniqueID:
                self.__ctx.lastArenaUniqueID = arenaUniqueID
            if arenaBonusType:
                self.__ctx.lastArenaBonusType = arenaBonusType
            self.exit()

    def __onMapsTrainingExit(self):
        if not BattleReplay.isPlaying() and self.__ctx.lastArenaUniqueID is None:
            self.__ctx.lastArenaUniqueID = self.__arenaVisitor.getArenaUniqueID()
            self.__ctx.lastArenaBonusType = self.__arenaVisitor.getArenaBonusType()
        return
