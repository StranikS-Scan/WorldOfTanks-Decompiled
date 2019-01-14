# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/destructible_entity_component.py
from client_arena_component_system import ClientArenaComponent
import Event

class DestructibleEntitiesComponent(ClientArenaComponent):
    destructibleEntities = property(lambda self: self.__destructibleEntities)

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__destructibleEntities = {}
        self.onDestructibleEntityAdded = Event.Event(self._eventManager)
        self.onDestructibleEntityRemoved = Event.Event(self._eventManager)
        self.onDestructibleEntityHealthChanged = Event.Event(self._eventManager)
        self.onDestructibleEntityIsActiveChanged = Event.Event(self._eventManager)
        self.onDestructibleEntityStateChanged = Event.Event(self._eventManager)
        self.onDestructibleEntityFeedbackReceived = Event.Event(self._eventManager)

    def destroy(self):
        ClientArenaComponent.destroy(self)
        self.__destructibleEntities = {}

    def addDestructibleEntity(self, destEntity):
        self.__destructibleEntities[destEntity.destructibleEntityID] = destEntity
        self.onDestructibleEntityAdded(destEntity)

    def updateDestructibleEntityHealth(self, destEntity, newHealth, attackerID, attackReason, hitFlags):
        self.onDestructibleEntityHealthChanged(destEntity.destructibleEntityID, newHealth, destEntity.maxHealth, attackerID, attackReason, hitFlags)

    def updateDestructibleEntityActiveState(self, destEntity):
        self.onDestructibleEntityIsActiveChanged(destEntity.destructibleEntityID, destEntity.isActive)

    def updateDestructibleEntityDestructionState(self, destEntity):
        self.onDestructibleEntityStateChanged(destEntity.destructibleEntityID)

    def updateDestructibleEntityFeedback(self, destEntity, eventID, isImmediate=False):
        self.onDestructibleEntityFeedbackReceived(eventID, destEntity.destructibleEntityID, isImmediate)

    def removeDestructibleEntity(self, destEntity):
        if destEntity.destructibleEntityID in self.__destructibleEntities:
            self.onDestructibleEntityRemoved(destEntity.destructibleEntityID)
            del self.__destructibleEntities[destEntity.destructibleEntityID]

    def getNumDestructibleEntities(self):
        return len(self.__destructibleEntities)

    def getNumDestroyedEntities(self):
        count = 0
        for _, destEntity in self.__destructibleEntities.iteritems():
            if destEntity.health <= 0:
                count += 1

        return count

    def getTotalRemainingHealthPercentage(self):
        totalMaxHealth = 0.0
        totalRemainingHealth = 0.0
        for _, object_ in self.__destructibleEntities.iteritems():
            totalMaxHealth += object_.maxHealth
            totalRemainingHealth += object_.health

        remainingHealthPercentage = totalRemainingHealth / (totalMaxHealth / 100)
        return remainingHealthPercentage

    def getDestroyedEntityIds(self):
        destroyed = []
        for entityId, destEntity in self.__destructibleEntities.iteritems():
            if destEntity.health <= 0:
                destroyed.append(entityId)

        return destroyed

    def getDestructibleEntity(self, destId):
        return self.__destructibleEntities.get(destId, None)

    def getNearestDestructibleEntityID(self, position):

        def getDistance(entity):
            return entity.position.flatDistTo(position)

        aliveHQs = [ hq for hq in self.__destructibleEntities.itervalues() if hq.health > 0 ]
        if not aliveHQs:
            return (None, None)
        else:
            closestHQ = min(aliveHQs, key=getDistance)
            return (closestHQ.destructibleEntityID, getDistance(closestHQ)) if closestHQ else (None, None)
