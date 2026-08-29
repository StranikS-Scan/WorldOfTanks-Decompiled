# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/client_cgf/barrier/managers.py
import BigWorld
import CGF
import logging
from constants import IS_EDITOR
from GenericComponents import TransformComponent, DynamicModelComponent, AnimatorComponent
from ShotsReceiver import ShotsReceiver
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from white_tiger.client_cgf.barrier.components import WTBarrierEffectComponent, WTBarrierDynamicComponent, WTBarrierStaticComponent, WTBarrierClientComponent
from white_tiger_common.common_cgf.barrier.helpers import WT_BARRIER_COMPONENTS
from white_tiger_common.common_cgf.cgf_helpers import registerWTManager
from white_tiger_common.wt_constants import BarrierMode
if IS_EDITOR:

    class Vehicle(object):
        pass


else:
    from Vehicle import Vehicle
_logger = logging.getLogger(__name__)

@registerWTManager(CGF.DomainOption.DomainClient)
class WTBarrierReplicationManager(CGF.ComponentManager):

    @onAddedQuery(*WT_BARRIER_COMPONENTS)
    def onAdded(self, go, barrier):
        if barrier.replicableAvatarId != -1:
            self.__onReplicationDone(barrier)
        else:
            barrier.onReplicationDone += self.__onReplicationDone
        barrier.onChangeMode += self.__onChangeMode

    def __onReplicationDone(self, barrierReplicableComponent):
        go = barrierReplicableComponent.entity.entityGameObject
        player = BigWorld.player()
        if player is None:
            _logger.error('No player found while set go=%s', go.id)
            return
        else:
            go.createComponent(WTBarrierClientComponent)
            if barrierReplicableComponent.mode != BarrierMode.DYNAMIC.value:
                return
            self.__changeMode(go, barrierReplicableComponent.mode)
            return

    def __onChangeMode(self, barrierReplicableComponent, mode):
        go = barrierReplicableComponent.entity.entityGameObject
        player = BigWorld.player()
        if player is None:
            _logger.error('No player found while set go %s', go.id)
            return
        else:
            self.__changeMode(go, mode)
            return

    def __changeMode(self, go, mode):
        dynamic = go.findComponentByType(WTBarrierDynamicComponent)
        static = go.findComponentByType(WTBarrierStaticComponent)
        if mode == BarrierMode.DYNAMIC.value and dynamic is None:
            go.createComponent(WTBarrierDynamicComponent)
        elif mode == BarrierMode.STATIC.value:
            if dynamic:
                go.removeComponent(dynamic)
            if static is None:
                go.createComponent(WTBarrierStaticComponent)
        return


@registerWTManager(CGF.DomainOption.DomainClient)
class WTBarrierEffectManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, WTBarrierClientComponent)
    def onBarrierAdded(self, go, barrierComponent):
        shotReceiver = go.findComponentByType(ShotsReceiver)
        shotReceiver.onShot += self.__onShotReceived

    @onRemovedQuery(CGF.GameObject, WTBarrierClientComponent)
    def onBarrierRemoved(self, go, barrierComponent):
        shotReceiver = go.findComponentByType(ShotsReceiver)
        shotReceiver.onShot -= self.__onShotReceived

    def __onShotReceived(self, position, normal, shotID, effectIndex, matKind, gameObjectID):
        effectQuery = CGF.Query(self.spaceID, (CGF.GameObject,
         ShotsReceiver,
         WTBarrierClientComponent,
         WTBarrierEffectComponent,
         TransformComponent))
        for gameObject, _, barrierComponent, effectComponent, transform in effectQuery:
            if gameObject.id == gameObjectID and barrierComponent.isVisible:
                self.__processEffect(gameObject, position, effectComponent, transform)

    def __processEffect(self, gameObject, position, effect, transform):
        if not effect.effectPath:
            _logger.error('No effect path found on barrier Shot received (go=%s)', gameObject.id)
            return
        localTransform = transform.worldTransform
        localTransform.invert()
        localPosition = localTransform.applyPoint(position)
        CGF.loadGameObjectIntoHierarchy(effect.effectPath, gameObject, localPosition)


@registerWTManager(CGF.DomainOption.DomainClient)
class WTBarrierVisibilityManager(CGF.ComponentManager):
    ON = 0
    IDLE_DYNAMIC = 1
    IDLE_STATIC = 2
    OFF = 3
    IDLE_SOUND = 4

    @onAddedQuery(Vehicle)
    def onVehicleAdded(self, vehicle):
        self.__onVehicleAdded(vehicle)

    @onAddedQuery(*(WT_BARRIER_COMPONENTS + (TransformComponent, WTBarrierDynamicComponent)))
    def onDynamicBarrierAdded(self, go, barrierComponent, transform, _):
        self.__onDynamicBarrierAdded(go, barrierComponent.replicableAvatarId, transform)

    @onAddedQuery(*(WT_BARRIER_COMPONENTS + (WTBarrierStaticComponent,)))
    def onStaticBarrierAdded(self, go, barrierComponent, _):
        self.__handleVisibility(go, True)
        self.__switchToStatic(go)

    @onRemovedQuery(Vehicle)
    def onVehicleRemoved(self, vehicle):
        self.__onVehicleRemoved(vehicle)

    def __onVehicleAdded(self, vehicle):
        barrierQuery = CGF.Query(self.spaceID, WT_BARRIER_COMPONENTS + (WTBarrierDynamicComponent,))
        for go, barrierComponent, _ in barrierQuery:
            if barrierComponent.replicableAvatarId == vehicle.avatarID:
                self.__handleVisibility(go, True)
                break

    def __onVehicleRemoved(self, __):
        avatar = BigWorld.player()
        if avatar is None:
            return
        else:
            barrierQuery = CGF.Query(self.spaceID, WT_BARRIER_COMPONENTS + (WTBarrierDynamicComponent,))
            for go, barrierComponent, _ in barrierQuery:
                st = any((v.avatarID == barrierComponent.replicableAvatarId for v in avatar.vehicles))
                self.__handleVisibility(go, st)

            return

    def __onDynamicBarrierAdded(self, go, replicableAvatarId, transform):
        self.__handleVisibility(go, False)
        vehicles = BigWorld.player().vehicles
        for vehicle in vehicles:
            if replicableAvatarId == vehicle.avatarID:
                self.__handleVisibility(go, True)
                self.__playOnSound(go)
                break

    def __handleVisibility(self, go, isVisible):
        model = go.findComponentByType(DynamicModelComponent)
        animator = go.findComponentByType(AnimatorComponent)
        barrierComponent = go.findComponentByType(WTBarrierClientComponent)
        barrierComponent.isVisible = isVisible
        model.setIsVisible(isVisible)
        animator.setIsVisible(isVisible)
        if isVisible:
            animator.startLayer(self.IDLE_SOUND)
        else:
            animator.stopLayer(self.IDLE_SOUND)

    def __playOnSound(self, go):
        animator = go.findComponentByType(AnimatorComponent)
        animator.startLayer(self.ON)

    def __switchToStatic(self, go):
        animator = go.findComponentByType(AnimatorComponent)
        animator.stopLayer(self.ON)
        animator.stopLayer(self.IDLE_DYNAMIC)
        animator.startLayer(self.IDLE_STATIC)
        animator.startLayer(self.OFF)
