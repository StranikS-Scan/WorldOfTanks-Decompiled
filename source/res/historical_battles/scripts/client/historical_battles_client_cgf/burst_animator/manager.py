# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles_client_cgf/burst_animator/manager.py
import BigWorld
import CGF
import GenericComponents
from functools import partial
from PlayerEvents import g_playerEvents
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from component import BurstAnimatorComponent
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.battle_session import IBattleSessionProvider
from historical_battles_common_cgf.rules.manager_register import registerHistoricalBattlesManager

@registerHistoricalBattlesManager(domain=CGF.DomainOption.DomainClient)
class BurstAnimatorComponentManager(CGF.ComponentManager):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BurstAnimatorComponentManager, self).__init__()
        self.__vehicleToAnimator = {}
        g_playerEvents.onShowShooterTracer += self.__onOtherPlayerShot
        if self.__sessionProvider.shared.ammo:
            self.__sessionProvider.shared.ammo.onGunReloadTimeSet += self.onPlayerShot

    def deactivate(self):
        if self.__sessionProvider.shared.ammo:
            self.__sessionProvider.shared.ammo.onGunReloadTimeSet -= self.onPlayerShot
        g_playerEvents.onShowShooterTracer -= self.__onOtherPlayerShot
        self.__vehicleToAnimator = {}

    @onAddedQuery(CGF.GameObject, BurstAnimatorComponent, GenericComponents.AnimatorComponent)
    def handleComponentAdded(self, go, burstAnimator, animatorComponent):
        vehicle = self.__getVehicleFromGO(go)
        self.__vehicleToAnimator[vehicle.id] = animatorComponent
        if BigWorld.player().playerVehicleID == vehicle.id:
            if animatorComponent is not None:
                animatorComponent.stop()
                ammoCtrl = self.__sessionProvider.shared.ammo
                reloadState = ammoCtrl.getGunReloadingState()
                BigWorld.callback(reloadState.getTimeLeft(), partial(self.__reload, BigWorld.player().playerVehicleID))
        else:
            self.__reload(vehicle.id)
        return

    @onRemovedQuery(CGF.GameObject, BurstAnimatorComponent, GenericComponents.AnimatorComponent)
    def handleComponentRemoved(self, go, burstAnimator, animatorComponent):
        vehicle = self.__getVehicleFromGO(go)
        if vehicle is not None:
            self.__vehicleToAnimator.pop(vehicle.id)
        return

    def onPlayerShot(self, currShellCD, state, skipAutoLoader):
        if not state.getActualValue() != -1:
            self.__sessionProvider.shared.ammo.onGunReloadTimeSet += self.__onGunReloadTimeSet
            animator = self.__vehicleToAnimator.get(BigWorld.player().playerVehicleID, None)
            if animator is not None:
                animator.startLayer(0)
        return

    def __onGunReloadTimeSet(self, currShellCD, state, skipAutoLoader):
        self.__sessionProvider.shared.ammo.onGunReloadTimeSet -= self.__onGunReloadTimeSet
        ammoCtrl = self.__sessionProvider.shared.ammo
        reloadState = ammoCtrl.getGunReloadingState()
        if reloadState.getTimeLeft() > 0:
            BigWorld.callback(reloadState.getTimeLeft(), partial(self.__reload, BigWorld.player().playerVehicleID))

    def __reload(self, id):
        animator = self.__vehicleToAnimator.get(id, None)
        if animator is not None:
            ammoCtrl = self.__sessionProvider.shared.ammo
            if ammoCtrl.getFirstAvailableShell() is None:
                animator.stop()
                return
            animator = self.__vehicleToAnimator.get(id, None)
            if animator is not None:
                animator.startLayer(0)
                nextTick(partial(self.__pause, id))()
        return

    def __pause(self, id):
        animator = self.__vehicleToAnimator.get(id, None)
        if animator is not None and animator.isPlaying():
            animator.setCursorPosition(0.0, 0)
            animator.pause()
        return

    def __onOtherPlayerShot(self, shooterEntity, gunIndex):
        if BigWorld.player().playerVehicleID == shooterEntity.id:
            return
        else:
            animator = self.__vehicleToAnimator.get(shooterEntity.id, None)
            if animator is not None and not animator.isPlaying():
                animator.startLayer(0)
                BigWorld.callback(9, partial(self.__reload, shooterEntity.id))
            return

    def __getVehicleFromGO(self, obj):
        from Vehicle import Vehicle
        hierarchyManager = CGF.HierarchyManager(self.spaceID)
        if not hierarchyManager:
            return None
        else:
            vehicleGO = hierarchyManager.getTopMostParent(obj)
            vehicle = vehicleGO.findComponentByType(Vehicle)
            return vehicle
