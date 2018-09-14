# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_session.py
import weakref
from collections import namedtuple
from PlayerEvents import g_playerEvents
from adisp import async
from debug_utils import LOG_DEBUG
from gui import g_tankActiveCamouflage
from gui.battle_control.arena_info import invitations
from gui.battle_control.arena_info.arena_dp import ArenaDataProvider
from gui.battle_control.arena_info.listeners import ListenersCollection
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.battle_constants import VIEW_COMPONENT_RULE
from gui.battle_control.battle_ctx import BattleContext
from gui.battle_control import arena_visitor
from gui.battle_control import controllers
from gui.battle_control.requests import AvatarRequestsController
from gui.battle_control.view_components import createComponentsBridge
BattleExitResult = namedtuple('BattleExitResult', 'isDeserter playerInfo')

class BattleSessionProvider(object):
    """This class is backend of GUI for one battle session."""
    __slots__ = ('__ctx', '__sharedRepo', '__dynamicRepo', '__requestsCtrl', '__arenaDP', '__arenaListeners', '__viewComponentsBridge', '__weakref__', '__arenaVisitor', '__invitations', '__isReplayPlaying')

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
        return

    @property
    def shared(self):
        """ Returns reference to repository of shared controllers
        that are created for all game sessions.
        :return: instance of SharedControllersLocator.
        """
        return self.__sharedRepo

    @property
    def dynamic(self):
        """ Returns reference to repository of controllers
        that are created for some game sessions.
        :return: instance of DynamicControllersLocator.
        """
        return self.__dynamicRepo

    @property
    def arenaVisitor(self):
        """ Returns reference to visitor that has safe access to properties of arena.
        :return: instance of _ClientArenaVisitor.
        """
        return self.__arenaVisitor

    @property
    def invitations(self):
        """ Returns reference to invitations handler.
        :return: instance of _SquadInvitationsHandler.
        """
        return self.__invitations

    def getCtx(self):
        """
        Gets instance of ammo controller.
        :return: instance of AmmoController.
        """
        return self.__ctx

    @async
    def sendRequest(self, ctx, callback, allowDelay=None):
        """
        Sends request to the server.
        :param ctx: avatar request context object,
            @see gui.battle_control.request.context.
        :param callback: function that is invoked when response is received.
        :param allowDelay: bool.
        """
        self.__requestsCtrl.request(ctx, callback=callback, allowDelay=allowDelay)

    def setPlayerVehicle(self, vID, vDesc):
        ctrl = self.__sharedRepo.ammo
        if ctrl is not None:
            ctrl.setGunSettings(vDesc.gun)
        ctrl = self.__sharedRepo.vehicleState
        if ctrl is not None:
            ctrl.setPlayerVehicle(vID)
        ctrl = self.__sharedRepo.feedback
        if ctrl is not None:
            ctrl.setPlayerVehicle(vID)
        ctrl = self.__dynamicRepo.respawn
        if ctrl is not None:
            ctrl.spawnVehicle(vID)
        g_tankActiveCamouflage[vDesc.type.compactDescr] = self.__arenaVisitor.type.getVehicleCamouflageKind()
        return

    def getArenaDP(self):
        """Gets instance of arena data provider.
        :return: instance of ArenaDataProvider.
        """
        return self.__arenaDP

    def addArenaCtrl(self, controller):
        """Adds arena controller. For additional information see
            gui.arena_info.IArenaController.
        :param controller: object that implements IArenaController.
        :return: True if controller is added to arena listeners, otherwise - False.
        """
        if self.__arenaListeners is not None:
            return self.__arenaListeners.addController(controller)
        else:
            return False
            return

    def removeArenaCtrl(self, controller):
        """Removes arena controller.
        :param controller: object extends IArenaController.
        """
        if self.__arenaListeners is not None:
            self.__arenaListeners.removeController(controller)
        return

    def registerViewComponentsCtrl(self, controller):
        """Registers controller in the bridge of view components.
        :param controller: object that implements IViewComponentsController.
        :return: True if controller is added to arena listeners, otherwise - False.
        """
        if self.__viewComponentsBridge is not None:
            self.__viewComponentsBridge.registerController(controller)
            return True
        else:
            return False
            return

    def registerViewComponents(self, *data):
        """Sets view component data to find that components in routines
            addViewComponent, removeViewComponent.
        :param data: tuple((BATTLE_CTRL.*, (componentID, ...)), ...)
        """
        if self.__viewComponentsBridge is not None:
            self.__viewComponentsBridge.registerViewComponents(*data)
        return

    def addViewComponent(self, componentID, component, rule=VIEW_COMPONENT_RULE.PROXY):
        """View component has been created.
        :param componentID: string containing unique component ID.
        :param component: instance of component.
        :param rule: one of VIEW_COMPONENT_RULE.*.
        """
        if self.__viewComponentsBridge is not None:
            self.__viewComponentsBridge.addViewComponent(componentID, component, rule=rule)
        return

    def removeViewComponent(self, componentID):
        """View component has been removed.
        :param componentID: string containing unique component ID.
        """
        if self.__viewComponentsBridge is not None:
            self.__viewComponentsBridge.removeViewComponent(componentID)
        return

    def getExitResult(self):
        """ Gets result if player exits battle that are helped to notify player about penalty (if they have).
        :return: instance of BattleExitResult(isDeserter, player).
        """
        if not self.__isReplayPlaying and not self.__arenaVisitor.gui.isTrainingBattle():
            vInfo = self.__arenaDP.getVehicleInfo()
            vStats = self.__arenaDP.getVehicleStats()
            if self.__arenaVisitor.gui.isEventBattle():
                isDeserter = False
            elif self.__arenaVisitor.hasRespawns():
                isDeserter = not vStats.stopRespawn
            else:
                isDeserter = avatar_getter.isVehicleAlive() and not avatar_getter.isVehicleOverturned()
            return BattleExitResult(isDeserter, vInfo.player)
        else:
            return BattleExitResult(False, None)
            return None

    @staticmethod
    def exit():
        """Exits from current battle session."""
        avatar_getter.leaveArena()

    def start(self, setup):
        """
        Battle session is started.
        :param setup: instance of BattleSessionSetup.
        :return:
        """
        assert isinstance(setup, controllers.BattleSessionSetup)
        self.__isReplayPlaying = setup.isReplayPlaying
        self.__arenaVisitor = arena_visitor.createByAvatar(avatar=setup.avatar)
        setup.sessionProvider = weakref.proxy(self)
        self.__arenaDP = ArenaDataProvider(setup)
        self.__ctx.start(self.__arenaDP)
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

    def stop(self):
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
        self.__ctx.stop()
        return

    def switchToPostmortem(self):
        """Player's vehicle is destroyed, switchers GUI to postmortem mode."""
        ctrl = self.__sharedRepo.ammo
        if ctrl is not None:
            ctrl.clear()
        ctrl = self.__sharedRepo.equipments
        if ctrl is not None:
            ctrl.clear()
        ctrl = self.__sharedRepo.optionalDevices
        if ctrl is not None:
            ctrl.clear()
        ctrl = self.__sharedRepo.feedback
        if ctrl is not None:
            ctrl.setPlayerVehicle(0L)
        ctrl = self.__sharedRepo.vehicleState
        if ctrl is not None:
            ctrl.switchToPostmortem()
        return

    def useLoaderIntuition(self):
        """Loader intuition was used."""
        ctrl = self.__sharedRepo.messages
        if ctrl is not None:
            ctrl.showVehicleMessage('LOADER_INTUITION_WAS_USED')
        ctrl = self.__sharedRepo.ammo
        if ctrl is not None:
            ctrl.useLoaderIntuition()
        return

    def movingToRespawnBase(self):
        """Player's avatar is moving to the respawn."""
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
        """State of player's vehicle (health, fire, state of device, etc.) is
        changed, notifies GUI about it.
        :param state: one of VEHICLE_VIEW_STATE.*.
        :param value: value of state.
        :param vehicleID: vehicle ID or zero.
        """
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

    def addHitDirection(self, hitDirYaw, isDamage):
        ctrl = self.__sharedRepo.hitDirection
        if ctrl is not None:
            ctrl.addHit(hitDirYaw, isDamage)
        return

    def startVehicleVisual(self, vProxy, isImmediate=False):
        ctrl = self.__sharedRepo.feedback
        if ctrl is not None:
            ctrl.startVehicleVisual(vProxy, isImmediate)
        ctrl = self.__dynamicRepo.debug
        if ctrl is not None:
            ctrl.startVehicleVisual(vProxy.id)
        return

    def stopVehicleVisual(self, vehicleID, isPlayerVehicle):
        ctrl = self.__sharedRepo.feedback
        if ctrl is not None:
            ctrl.stopVehicleVisual(vehicleID, isPlayerVehicle)
        ctrl = self.__dynamicRepo.debug
        if ctrl is not None:
            ctrl.stopVehicleVisual(vehicleID)
        return

    def handleShortcutChatCommand(self, key):
        ctrl = self.__sharedRepo.chatCommands
        if ctrl is not None:
            ctrl.handleShortcutChatCommand(key)
        return

    def __pe_onBattleResultsReceived(self, isActiveVehicle, _):
        """It's listener of event _PlayerEvents.onBattleResultsReceived.
        :param isActiveVehicle: bool.
        """
        if isActiveVehicle:
            arenaUniqueID = self.__arenaVisitor.getArenaUniqueID()
            LOG_DEBUG('Try to exit from arena', arenaUniqueID)
            if arenaUniqueID:
                self.__ctx.lastArenaUniqueID = arenaUniqueID
            avatar_getter.leaveArena()
