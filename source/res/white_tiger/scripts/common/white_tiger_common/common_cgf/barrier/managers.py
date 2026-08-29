# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/common_cgf/barrier/managers.py
import BigWorld
import CGF
from Math import Vector3
from math import pi
from GenericComponents import TransformComponent
from cgf_script.managers_registrator import onAddedQuery, onProcessQuery
from white_tiger_common.common_cgf.barrier.helpers import WT_BARRIER_COMPONENTS
from white_tiger_common.common_cgf.cgf_helpers import registerWTManager
from white_tiger_common.common_cgf.barrier.components import WTBarrierHelperComponent, WTBarrierRotatorComponent

@registerWTManager(CGF.DomainOption.DomainServer)
class WTBarrierServerManager(CGF.ComponentManager):
    _OFFSET = Vector3(0, 1, 0)

    @onAddedQuery(*(WT_BARRIER_COMPONENTS + (WTBarrierHelperComponent,)))
    def onAddedReplication(self, go, barrier, barrierHelper):
        barrier.replicableAvatarId = barrierHelper.avatarID

    @onProcessQuery(*(WT_BARRIER_COMPONENTS + (WTBarrierRotatorComponent,)))
    def onProcess(self, go, barrier, rotator):
        avatar = BigWorld.entities.get(barrier.replicableAvatarId)
        if avatar.vehicle is None:
            return
        else:
            self.__rotateStaticBarrier(go, avatar.vehicle, rotator.settingDistance)
            return

    def __rotateStaticBarrier(self, go, vehicle, distance):
        transformComponent = go.findComponentByType(TransformComponent)
        gunAngles = vehicle.gunRotator.gunAngles
        _, direction = vehicle.gunRotator.shotPointAndDirection
        direction.normalise()
        if transformComponent:
            transformComponent.position = vehicle.position + self._OFFSET + direction * distance
            transformComponent.rotation = Vector3(gunAngles[0] + vehicle.yaw + pi / 2, 0, gunAngles[1])
