# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/common_cgf/missile_system/managers.py
import typing
from math import sin, cos, pi
from functools import partial
import CGF
from Math import Vector3
from GenericComponents import TransformComponent
from Triggers import TimeTriggerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from events_core_common.events_core_cgf.missile_system.helpers import registerMissileManager
from events_core_common.events_core_cgf.missile_system.components import MissileDeploymentComponent, MissileDetonationComponent
from white_tiger_common.common_cgf.missile_system.components import WTSpawnerComponent
from constants import IS_CELLAPP
if typing.TYPE_CHECKING:
    import BigWorld
    from typing import Dict
if IS_CELLAPP:
    from server_constants import ATTACKER_TYPE
    from MissileComponent import MissileComponent
    from events_core_cell.events_core_cgf.missile_system.components import MissileAvatarIDComponent, MissileExplosionComponent
else:

    class MissileAvatarIDComponent(object):
        pass


    class MissileComponent(object):
        pass


    class MissileExplosionComponent(object):
        pass


@registerMissileManager(CGF.DomainOption.DomainServer)
class WTMissileSpawnerManager(CGF.ComponentManager):
    RADIUS = 1.5
    ANGULAR_SPEED = 2.0
    WT_MISSILE_COMPONENTS = (CGF.GameObject,
     TimeTriggerComponent,
     MissileAvatarIDComponent,
     WTSpawnerComponent)

    def __init__(self):
        super(WTMissileSpawnerManager, self).__init__()
        self._timeTriggerReactions = {}

    @onAddedQuery(*WT_MISSILE_COMPONENTS)
    def onAddedSpawner(self, go, trigger, missileAvatar, spawner):
        wrappedCb = partial(self.__spawn, missileAvatar.avatarID, spawner)
        self.__spawn(missileAvatar.avatarID, spawner, go)
        trigger.reset(spawner.spawnDelay, spawner.missileNumber - 1)
        reactionID = trigger.addFireReaction(wrappedCb)
        self._timeTriggerReactions[go.id] = reactionID

    @onRemovedQuery(*WT_MISSILE_COMPONENTS)
    def onRemovedSpawner(self, go, trigger, missileAvatar, spawner):
        spawner.alive = False
        trigger.removeFireReaction(self._timeTriggerReactions[go.id])
        self._timeTriggerReactions.pop(go.id)
        for missile in spawner.missiles:
            if missile.isValid():
                CGF.removeGameObject(missile)

        spawner.missiles = []

    @onRemovedQuery(CGF.GameObject, MissileComponent, TransformComponent)
    def onRemovedMissile(self, go, missile, transform):
        spawners = CGF.Query(self.spaceID, (MissileAvatarIDComponent, WTSpawnerComponent))
        spawner = None
        for avatarIDComponent, spawnerComponent in spawners:
            if missile.replicableAvatarId == avatarIDComponent.avatarID:
                spawner = spawnerComponent
                break

        if spawner is None:
            return
        else:
            component = go.findComponentByType(MissileDetonationComponent)
            if not component:
                attackerInfo, attackerVehicle = self._createMissileAttackerInfo(missile)

                def postloadSetup(attackerInfo, attackerVehicle, go):
                    explosionComponent = go.findComponentByType(MissileExplosionComponent)
                    explosionComponent.attackerInfo = attackerInfo
                    explosionComponent.attackerVehicle = attackerVehicle

                CGF.loadGameObject(missile.explosionPrefabPath, self.spaceID, transform.worldTransform, partial(postloadSetup, attackerInfo, attackerVehicle))
            spawner.missiles = [ m for m in spawner.missiles if m.id != go.id ]
            if not spawner.missiles:
                spawner.deactivateCallback()
            return

    def transformMissiles(self, entity, _, deployment):
        deployment.angle += self.ANGULAR_SPEED * self.clock.gameDelta
        position = entity.position + deployment.deployOffset
        position.x = position.x + self.RADIUS * cos(deployment.angle)
        position.z = position.z + self.RADIUS * sin(deployment.angle)
        return position

    def __spawn(self, avatarID, spawner, go):

        def onLoaded(aId, sp, go):
            if not sp.alive:
                CGF.removeGameObject(go)
                return
            go.createComponent(MissileAvatarIDComponent, aId)
            deploy = go.findComponentByType(MissileDeploymentComponent)
            deploy.angle = len(sp.missiles) * (2 * pi / sp.missileNumber + sp.spawnDelay * self.ANGULAR_SPEED)
            deploy.deployTransformCallback = self.transformMissiles
            sp.missiles.append(go)

        wrappedCb = partial(onLoaded, avatarID, spawner)
        CGF.loadGameObject(spawner.missilePrefabPath, self.spaceID, Vector3(0, 0, 0), wrappedCb)

    def __createMissileAttackerInfo(self, missile):
        avatar = BigWorld.entities.get(missile.replicableAvatarId)
        if avatar is None or avatar.vehicle is None:
            return (None, None)
        else:
            attackerVehicle = avatar.vehicle
            attackerInfo = attackerVehicle.makeAttackerInfoFromSelf()
            attackerInfo['attackerType'] = ATTACKER_TYPE.MISSILE
            return (attackerInfo, attackerVehicle)
