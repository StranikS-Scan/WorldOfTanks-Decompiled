# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BunkerLogicComponent.py
import BigWorld
from cgf_components_common.bunkers import BunkerLogicComponent as BunkerLogicComponentCGF
from constants import IS_CGF_DUMP
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if not IS_CGF_DUMP:
    from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, ENTITY_IN_FOCUS_TYPE

class BunkerLogicComponent(BigWorld.DynamicScriptComponent, BunkerLogicComponentCGF):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def bunkerDestroyed(self):
        self._onBunkerDestroyed()

    def startLogic(self):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl is not None:
            feedbackCtrl.onVehicleFeedbackReceived += self._onVehicleFeedbackReceived
        return

    def stopLogic(self):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl is not None:
            feedbackCtrl.onVehicleFeedbackReceived -= self._onVehicleFeedbackReceived
        return

    def _onVehicleFeedbackReceived(self, eventID, entityID, entityInFocusData):
        if eventID != FEEDBACK_EVENT_ID.ENTITY_IN_FOCUS:
            return
        else:
            destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
            if destructibleComponent is None:
                return
            if entityInFocusData.entityTypeInFocus == ENTITY_IN_FOCUS_TYPE.DESTRUCTIBLE_ENTITY:
                _, targetID = destructibleComponent.getDestructibleEntityAndDestructibleIDByEntityID(entityID)
                self.highlightBunker(self.destructibleEntityId == targetID and entityInFocusData.isInFocus)
            elif entityInFocusData.entityTypeInFocus == ENTITY_IN_FOCUS_TYPE.VEHICLE:
                self.highlightBunker(entityID in self.vehicleIDs and entityID in BigWorld.entities.keys() and BigWorld.entities[entityID].isAlive() and entityInFocusData.isInFocus)
            return

    def highlightBunker(self, isInFocus):
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        destructibleEntity = destructibleComponent.getDestructibleEntity(self.destructibleEntityId)
        if destructibleEntity is None or not destructibleEntity.isAlive():
            return
        else:
            if isInFocus:
                destructibleEntity.drawEdge()
            else:
                destructibleEntity.removeEdge()
            vehicles = [ v for v in BigWorld.player().vehicles if v.id in self.vehicleIDs ]
            for vehicle in vehicles:
                if isInFocus:
                    vehicle.drawEdge()
                vehicle.removeEdge()

            return

    def _onBunkerDestroyed(self):
        self._activateGameObject(self.destroyedChild)
        self._activateGameObject(self.transitionChild)

    def _activateGameObject(self, gameObject):
        if gameObject is not None and gameObject.isValid():
            gameObject.activate()
        return
