# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_core_common/events_core_cgf/missile_system/components.py
import CGF
import Math
from cgf_script.component_meta_class import CGFMetaTypes, ComponentProperty, registerReplicableComponent, registerComponent

@registerReplicableComponent
class MissileComponent(object):
    category = 'Events Core'
    editorTitle = 'Missile'
    baseSpeed = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Base Speed', value=5.0)
    targetSpeed = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Target Speed', value=15.0)
    accelerationRate = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Acceleration Rate', value=3.0)
    rotationRate = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Rotation Rate', value=3.0)
    flightTime = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Flight Time', value=10.0)
    explosionPrefabPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Explosion Prefab', value='', annotations={'path': '*.prefab'})
    destinationDirection = ComponentProperty(type=CGFMetaTypes.VECTOR3, editorName='Destination Direction', value=Math.Vector3(0, 1, 0))
    canRotate = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='canRotate', value=True)

    def __init__(self):
        super(MissileComponent, self).__init__()
        self.currentDirection = self.destinationDirection
        self.currentSpeed = self.baseSpeed
        self.isBoostEnabled = False
        self.replicableAvatarId = -1
        self.flightFinishTime = 0.0


@registerComponent
class MissileDeploymentComponent(object):
    category = 'Events Core'
    editorTitle = 'Missile Deployment'
    domain = CGF.DomainOption.DomainAll
    deployTime = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Deploy Time', value=4.0)
    deployOffset = ComponentProperty(type=CGFMetaTypes.VECTOR3, editorName='Deploy Offset', value=Math.Vector3(0, 10, 0))

    def __init__(self, angle=0):
        self.angle = angle
        self.deployTransformCallback = None
        return


@registerComponent
class MissileDetonationComponent(object):
    category = 'Events Core'
    domain = CGF.DomainOption.DomainServer
