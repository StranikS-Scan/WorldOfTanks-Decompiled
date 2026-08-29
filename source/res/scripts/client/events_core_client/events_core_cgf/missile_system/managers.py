# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_core_client/events_core_cgf/missile_system/managers.py
import BigWorld
import CGF
import GUI
import Keys
from gui import InputHandler
from constants import IS_EDITOR, SERVER_TICK_LENGTH
from cgf_script.managers_registrator import onAddedQuery, onProcessQuery, onRemovedQuery
from events_core_common.events_core_cgf.missile_system.helpers import MISSILE_COMPONENTS, registerMissileManager
from events_core_client.events_core_cgf.missile_system.components import ClientMissileComponent, MissileReplicationDoneComponent, MissileInputComponent, FPVModeComponent, ArcadeModeComponent
if not IS_EDITOR:
    from AvatarInputHandler import cameras
    from MissileComponent import MissileComponent
else:

    class MissileComponent(object):
        pass


@registerMissileManager(CGF.DomainOption.DomainClient)
class MissileSystemClientManager(CGF.ComponentManager):

    @onAddedQuery(*MISSILE_COMPONENTS)
    def onAdded(self, go, missile, transform):
        if missile.replicableAvatarId != -1:
            self.__onReplicationDone(missile, missile.replicableAvatarId)
        else:
            missile.onAvatarIdReplicated += self.__onReplicationDone

    @onRemovedQuery(*MISSILE_COMPONENTS)
    def onRemoved(self, go, missile, transform):
        missile.onAvatarIdReplicated -= self.__onReplicationDone
        player = BigWorld.player()
        if player is not None and player.id == missile.replicableAvatarId:
            InputHandler.g_instance.onKeyDown -= self.__handleStartBoostKeyEvent
            InputHandler.g_instance.onKeyUp -= self.__handleEndBoostKeyEvent
            InputHandler.g_instance.onKeyDown -= self.__handleDetonateKeyEvent
        return

    @onAddedQuery(*(MISSILE_COMPONENTS + (MissileInputComponent,)))
    def onAddedInputHandling(self, go, missile, transform):
        player = BigWorld.player()
        if player is not None:
            InputHandler.g_instance.onKeyDown += self.__handleStartBoostKeyEvent
            InputHandler.g_instance.onKeyUp += self.__handleEndBoostKeyEvent
            InputHandler.g_instance.onKeyDown += self.__handleDetonateKeyEvent
        return

    @onRemovedQuery(*(MISSILE_COMPONENTS + (MissileInputComponent,)))
    def onRemovedInputHandling(self, go, missile, transform):
        player = BigWorld.player()
        if player is not None:
            InputHandler.g_instance.onKeyDown -= self.__handleStartBoostKeyEvent
            InputHandler.g_instance.onKeyUp -= self.__handleEndBoostKeyEvent
            InputHandler.g_instance.onKeyDown -= self.__handleDetonateKeyEvent
        return

    def __onReplicationDone(self, missileReplicable, _):
        go = missileReplicable.entity.entityGameObject
        player = BigWorld.player()
        go.createComponent(MissileReplicationDoneComponent)
        if player is not None and player.id == missileReplicable.replicableAvatarId:
            go.createComponent(ClientMissileComponent)
        return

    def __handleStartBoostKeyEvent(self, event):
        self.__processInputEvent(event=event, triggerCondition=event.isKeyDown(), key=Keys.KEY_LEFTMOUSE, actionName='startBoostEffect')

    def __handleEndBoostKeyEvent(self, event):
        self.__processInputEvent(event=event, triggerCondition=event.isKeyUp(), key=Keys.KEY_LEFTMOUSE, actionName='endBoostEffect')

    def __handleDetonateKeyEvent(self, event):
        self.__processInputEvent(event=event, triggerCondition=event.isKeyDown(), key=Keys.KEY_SPACE, actionName='detonateProjectile')

    def __processInputEvent(self, event, triggerCondition, key, actionName):
        if not (triggerCondition and event.key == key):
            return
        else:
            player = BigWorld.player()
            if player is None:
                return
            query = CGF.Query(self.spaceID, (MissileComponent, ClientMissileComponent))
            for missile, _ in query:
                if missile.replicableAvatarId == player.id:
                    getattr(missile.cell, actionName)()
                    break

            return


@registerMissileManager(CGF.DomainOption.DomainClient)
class MissileSystemInputModeManager(CGF.ComponentManager):
    MAX_COLLISION_DISTANCE_FROM_SCREEN = 5500.0
    ADJUSTED_COLLISION_DISTANCE = 2500
    _BASE = MISSILE_COMPONENTS + (ClientMissileComponent,)
    _PARAMS = {'tickGroup': 'Simulation',
     'period': SERVER_TICK_LENGTH}

    @onProcessQuery(*(_BASE + (ArcadeModeComponent,)), **_PARAMS)
    def onProcessArcadeMode(self, go, missile, transform, clientMissile, arcadeMode):
        self.__onProcessArcadeModeImpl(go, missile, transform, clientMissile, arcadeMode)

    def __onProcessArcadeModeImpl(self, go, missile, transform, clientMissile, arcadeMode):
        player = BigWorld.player()
        if player is not None and player.id == missile.replicableAvatarId:
            curPos = transform.position
            cursorPosition = GUI.mcursor().position
            ray, wpoint = cameras.getWorldRayAndPoint(cursorPosition.x, cursorPosition.y)
            skipFlags = 128
            collideResult = BigWorld.collideDynamicStatic(self.spaceID, wpoint, wpoint + ray * self.MAX_COLLISION_DISTANCE_FROM_SCREEN, skipFlags, -1, -1, 0)
            if player.vehicle:
                if collideResult:
                    collisionPoint = collideResult[0]
                    distance = int(collisionPoint.distTo(player.vehicle.position))
                else:
                    ray.normalise()
                    collisionPoint = wpoint + ray * self.ADJUSTED_COLLISION_DISTANCE
                    distance = self.ADJUSTED_COLLISION_DISTANCE
                clientMissile.distanceToTarget = distance
                direction = collisionPoint - curPos
                direction.normalise()
                missile.cell.setDestinationDirection(direction)
        return

    @onProcessQuery(*(_BASE + (FPVModeComponent,)), **_PARAMS)
    def onProcessFPVModes(self, go, missile, transform, clientMissile, fpvMode):
        pass
