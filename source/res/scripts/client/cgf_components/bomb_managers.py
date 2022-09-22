# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/bomb_managers.py
import BigWorld
import CGF
import GenericComponents
import Vehicle
from BombPickUp import BombPickUpComponent
from Generator import GeneratorActivationComponent
from EntityStressTimer import StressTimer
from cgf_components import PlayerVehicleTag, BossTag
from cgf_components.bomb_components import BombAbsorptionAreaComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID, VEHICLE_VIEW_STATE
from items.vehicles import getEquipmentByName
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

def _getEqipment(compDescr, guiSessionProvider):
    equipments = guiSessionProvider.shared.equipments
    if equipments is None:
        return
    else:
        return None if not equipments.hasEquipment(compDescr) else equipments.getEquipment(compDescr)


class BombPickUpManager(CGF.ComponentManager):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @property
    def feedbackCtrl(self):
        return self.guiSessionProvider.shared.feedback

    @onAddedQuery(Vehicle.Vehicle, BombPickUpComponent, CGF.GameObject)
    def onPlayerAdded(self, vehicle, pickUp, go):
        pickUp.update += self.updateUI
        self.updateUI(vehicle, pickUp, go)

    @onRemovedQuery(Vehicle.Vehicle, BombPickUpComponent)
    def onPlayerRemoved(self, _, pickUp):
        pickUp.update -= self.updateUI

    def updateUI(self, vehicle, pickUp, go):
        if go.findComponentByType(PlayerVehicleTag) is not None:
            ctx = (pickUp.leftTime, pickUp.endTime, pickUp.totalTime)
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_BOMB_CAPTURE, ctx)
        if self.feedbackCtrl:
            self.feedbackCtrl.onVehicleFeedbackReceived(_EVENT_ID.WT_BOMB_CAPTURE, vehicle.id, pickUp.leftTime)
        return


class BombDeployManager(CGF.ComponentManager):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    activations = CGF.QueryConfig(Vehicle.Vehicle, GeneratorActivationComponent, CGF.GameObject)

    @property
    def feedbackCtrl(self):
        return self.guiSessionProvider.shared.feedback

    @onAddedQuery(Vehicle.Vehicle, GeneratorActivationComponent)
    def onAdded(self, _, activation):
        self.playerUI(activation)

    @onRemovedQuery(Vehicle.Vehicle, GeneratorActivationComponent)
    def onRemoved(self, vehicle, activation):
        self.playerUI(activation)
        if self.feedbackCtrl:
            self.feedbackCtrl.onVehicleFeedbackReceived(_EVENT_ID.WT_BOMB_DEPLOY, vehicle.id, 0)

    def playerUI(self, addedActivation):
        genProgress = addedActivation.generatorGO.findComponentByType(GenericComponents.GeneratorProgressComponent)
        for veh, activation, go in self.activations:
            if addedActivation.generatorGO.id == activation.generatorGO.id:
                if go.findComponentByType(PlayerVehicleTag):
                    ctx = (genProgress.timeLeft, BigWorld.serverTime() + genProgress.timeLeft, genProgress.timeLeft)
                    self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_BOMB_DEPLOY, ctx)
                else:
                    carry = veh.appearance.gameObject.findComponentByType(GenericComponents.CarryingLootComponent)
                    if carry and self.feedbackCtrl:
                        self.feedbackCtrl.onVehicleFeedbackReceived(_EVENT_ID.WT_BOMB_DEPLOY, veh.id, genProgress.timeLeft)

        if not any((go.findComponentByType(PlayerVehicleTag) for _, __, go in self.activations)):
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_BOMB_DEPLOY, (0.0, 0.0, 0.0))

    @onAddedQuery(Vehicle.Vehicle, PlayerVehicleTag, CGF.GameObject)
    def onAddedPlayerVehicle(self, _, __, go):
        activation = go.findComponentByType(GeneratorActivationComponent)
        if activation:
            self.playerUI(activation)


class BombCarryManager(CGF.ComponentManager):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    tracking = set()

    @onAddedQuery(GenericComponents.CarryingLootComponent, PlayerVehicleTag)
    def onPlayerAdded(self, bombCarrying, _):
        lootGO = bombCarrying.lootGO
        if lootGO.isValid():
            timer = lootGO.findComponentByType(StressTimer)
            self.tracking.add(lootGO.id)
            if timer is not None:
                self.updateUI(timer, lootGO)
        return

    @onRemovedQuery(GenericComponents.CarryingLootComponent, PlayerVehicleTag)
    def onPlayerRemoved(self, bombCarrying, _):
        lootGO = bombCarrying.lootGO
        if lootGO.isValid():
            timer = bombCarrying.lootGO.findComponentByType(StressTimer)
            if timer is not None:
                self.updateUI(StressTimer(timer.timerGUID), lootGO)
            self.tracking.discard(bombCarrying.lootGO.id)
        return

    @onAddedQuery(StressTimer, CGF.GameObject)
    def onAdded(self, timer, go):
        timer.update += self.updateUI
        self.updateUI(timer, go)

    @onRemovedQuery(StressTimer)
    def onRemoved(self, timer):
        timer.update -= self.updateUI

    def updateUI(self, timer, go):
        if go.id in self.tracking:
            ctx = (timer.leftTime,
             timer.endTime,
             timer.totalTime,
             timer.isPaused,
             timer.timerGUID)
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_BOMB_CARRY, ctx)

    def deactivate(self):
        self.tracking.clear()


class BombAbsorptionAreaManager(CGF.ComponentManager):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    EQ_NAME = 'builtinAbsorb_wt'
    tracking = set()

    def getStressTimerGO(self, go):
        hierarchy = CGF.HierarchyManager(go.spaceID)
        parent = hierarchy.getTopMostParent(go)
        return parent

    @onAddedQuery(BombAbsorptionAreaComponent)
    def onAdded(self, bomb):
        if bomb.trigger is not None:
            trigger = bomb.trigger()
            trigger.addEnterReaction(self.onEnter)
            trigger.addExitReaction(self.onExit)
            trigger.addFilter(self.filter, False)
        return

    def onEnter(self, _, where):
        go = self.getStressTimerGO(where)
        self.tracking.add(go.id)
        stress = go.findComponentByType(StressTimer)
        if stress is not None:
            self.updateUI(stress, go)
        equipment = _getEqipment(getEquipmentByName(self.EQ_NAME).compactDescr, self.guiSessionProvider)
        if equipment:
            equipment.activate(avatar=BigWorld.player())
        return

    def onExit(self, _, where):
        go = self.getStressTimerGO(where)
        self.tracking.remove(go.id)
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_BOMB_ABSORB, (0.0, 0.0, 0.0))
        equipment = _getEqipment(getEquipmentByName(self.EQ_NAME).compactDescr, self.guiSessionProvider)
        if equipment:
            equipment.deactivate(avatar=BigWorld.player())

    def filter(self, who, _):
        return who.findComponentByType(BossTag) is not None and who.findComponentByType(PlayerVehicleTag) is not None

    def updateUI(self, stress, go):
        if go.id in self.tracking:
            ctx = (stress.leftTime, stress.endTime, stress.totalTime)
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_BOMB_ABSORB, ctx)

    @onAddedQuery(StressTimer, CGF.GameObject)
    def onAddedStressTimer(self, timer, go):
        timer.update += self.updateUI
        self.updateUI(timer, go)

    @onRemovedQuery(StressTimer)
    def onRemovedStressTimer(self, timer):
        timer.update -= self.updateUI


class BombCapturedManager(CGF.ComponentManager):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    EQ_NAME = 'builtinOverload_wt'

    @onAddedQuery(GenericComponents.CarryingLootComponent, PlayerVehicleTag)
    def onAdded(self, _, __):
        equipment = _getEqipment(getEquipmentByName(self.EQ_NAME).compactDescr, self.guiSessionProvider)
        if equipment:
            equipment.activate(avatar=BigWorld.player())

    @onRemovedQuery(GenericComponents.CarryingLootComponent, PlayerVehicleTag)
    def onRemoved(self, _, __):
        equipment = _getEqipment(getEquipmentByName(self.EQ_NAME).compactDescr, self.guiSessionProvider)
        if equipment:
            equipment.deactivate(avatar=BigWorld.player())
