# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_session.py
import weakref
from collections import namedtuple
import Event
import BattleReplay
from PlayerEvents import g_playerEvents
from adisp import async
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
    __slots__ = ('__ctx', '__sharedRepo', '__dynamicRepo', '__requestsCtrl', '__arenaDP', '__arenaListeners', '__viewComponentsBridge', '__weakref__', '__arenaVisitor', '__invitations', '__isReplayPlaying', '__battleCache')

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

    @async
    def sendRequest(self, ctx, callback, allowDelay=None):
        self.__requestsCtrl.request(ctx, callback=callback, allowDelay=allowDelay)

    def setPlayerVehicle(self, vID, vDesc):
        ctrl = self.__sharedRepo.ammo
        if ctrl is not None:
            ctrl.setGunSettings(vDesc.gun)
        ctrl = self.__sharedRepo.equipments
        if ctrl is not None:
            ctrl.notifyPlayerVehicleSet()
        ctrl = self.__sharedRepo.vehicleState
        if ctrl is not None:
            ctrl.setPlayerVehicle(vID)
        ctrl = self.__dynamicRepo.respawn
        if ctrl is not None:
            ctrl.spawnVehicle(vID)
        mapKind = self.__arenaVisitor.type.getVehicleCamouflageKind()
        g_tankActiveCamouflage[vDesc.type.compactDescr] = SeasonType.fromArenaKind(mapKind)
        return

    def switchVehicle(self, vehicleID):
        repo = self.shared
        for ctrl in (repo.ammo, repo.equipments, repo.optionalDevices):
            if ctrl is not None:
                ctrl.clear(False)

        repo.vehicleState.switchToOther(vehicleID)
        return

    def updateObservedVehicleData(self, vID, extraData):
        ctrl = self.__sharedRepo.ammo
        if ctrl is not None:
            ctrl.clear(False)
            ctrl.setGunSettings(extraData.gunSettings)
            for intCD, quantity, quantityInClip in extraData.orderedAmmo:
                ctrl.setShells(intCD, quantity, quantityInClip)

            ctrl.setCurrentShellCD(extraData.currentShellCD)
            ctrl.setNextShellCD(extraData.nextShellCD)
            ctrl.setGunReloadTime(extraData.reloadTimeLeft, extraData.reloadBaseTime)
        ctrl = self.__sharedRepo.equipments
        if ctrl is not None:
            ctrl.clear(False)
            for intCD, quantity, stage, timeRemaining, totalTime in extraData.orderedEquipment:
                ctrl.setEquipment(intCD, quantity, stage, timeRemaining, totalTime)

            ctrl.notifyPlayerVehicleSet()
        ctrl = self.__sharedRepo.optionalDevices
        if ctrl is not None:
            ctrl.clear(False)
            for deviceID, isOn in extraData.orderedOptionalDevices:
                ctrl.setOptionalDevice(deviceID, isOn)

        ctrl = self.__sharedRepo.vehicleState
        if ctrl is not None:
            ctrl.refreshVehicleStateValue(VEHICLE_VIEW_STATE.HEALTH)
            ctrl.notifyStateChanged(VEHICLE_VIEW_STATE.VEHICLE_CHANGED, vID)
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
        return

    def addViewComponent(self, componentID, component, rule=VIEW_COMPONENT_RULE.PROXY):
        if self.__viewComponentsBridge is not None:
            self.__viewComponentsBridge.addViewComponent(componentID, component, rule=rule)
        return

    def removeViewComponent(self, componentID):
        if self.__viewComponentsBridge is not None:
            self.__viewComponentsBridge.removeViewComponent(componentID)
        return

    def getExitResult(self):
        if not self.__isReplayPlaying and not self.__arenaVisitor.gui.isTrainingBattle():
            vInfo = self.__arenaDP.getVehicleInfo()
            vStats = self.__arenaDP.getVehicleStats()
            if self.__arenaVisitor.gui.isEventBattle():
                markersCtrl = controllers.event_behavior_marker_ctrl.EventBehaviorMarkersController()
                lifecycle = markersCtrl.teammateLifecycle.getParams()
                deaths = lifecycle.get(vInfo.vehicleID, {}).get('death', 0)
                maxLives = lifecycle.get('maxLivesLimit', 5)
                isDeserter = avatar_getter.isVehicleAlive() and not avatar_getter.isVehicleOverturned()
                if not isDeserter and deaths < maxLives:
                    isDeserter = True
                return BattleExitResult(isDeserter, vInfo.player)
            if self.__arenaVisitor.hasRespawns():
                isDeserter = not vStats.stopRespawn
            else:
                isDeserter = avatar_getter.isVehicleAlive() and not avatar_getter.isVehicleOverturned()
            return BattleExitResult(isDeserter, vInfo.player)
        else:
            return BattleExitResult(False, None)
            return None

    @staticmethod
    def exit():
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

    def useLoaderIntuition(self):
        ctrl = self.__sharedRepo.messages
        if ctrl is not None:
            ctrl.showVehicleMessage('LOADER_INTUITION_WAS_USED')
        ctrl = self.__sharedRepo.ammo
        if ctrl is not None:
            ctrl.useLoaderIntuition()
        return

    def movingToRespawnBase(self):
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
        ctrl = self.__sharedRepo.feedback
        if ctrl is not None:
            ctrl.startVehicleVisual(vProxy, isImmediate)
        ctrl = self.__dynamicRepo.battleField
        if ctrl is not None:
            ctrl.setVehicleVisible(vProxy.id, vProxy.health)
        return

    def stopVehicleVisual(self, vehicleID, isPlayerVehicle):
        ctrl = self.__sharedRepo.feedback
        if ctrl is not None:
            ctrl.stopVehicleVisual(vehicleID, isPlayerVehicle)
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

    def updateScenarioTimer(self, waitTime, alarmTime, visible):
        ctrl = self.__sharedRepo.vehicleState
        if ctrl is not None:
            ctrl.updateScenarioTimer(waitTime, alarmTime, visible)
        return

    def sendPlayerBattleLogNotification(self, messageKey, messageParams):
        self.shared.messages.showPlayerMessageByKey(messageKey, messageParams)

    def __pe_onBattleResultsReceived(self, isActiveVehicle, _):
        if isActiveVehicle and not BattleReplay.g_replayCtrl.isPlaying:
            arenaUniqueID = self.__arenaVisitor.getArenaUniqueID()
            arenaBonusType = self.__arenaVisitor.getArenaBonusType()
            LOG_DEBUG('Try to exit from arena', arenaUniqueID, arenaBonusType)
            if arenaUniqueID:
                self.__ctx.lastArenaUniqueID = arenaUniqueID
            if arenaBonusType:
                self.__ctx.lastArenaBonusType = arenaBonusType
            BattleSessionProvider.exit()
