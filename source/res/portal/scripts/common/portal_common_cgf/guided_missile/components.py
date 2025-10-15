# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/common/portal_common_cgf/guided_missile/components.py
import CGF
import Math
from Event import Event
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerReplicableComponent, registerComponent
from debug_utils import LOG_DEBUG

@registerComponent
class PortalGuidedMissileComponent(object):
    domain = CGF.DomainOption.DomainAll
    category = 'Portal'
    editorTitle = 'Guided Missile'
    direction = ComponentProperty(type=CGFMetaTypes.VECTOR3, editorName='Direction', value=Math.Vector3(1, 0, 0))
    avatarId = ComponentProperty(type=CGFMetaTypes.INT, editorName='Avatar Id', value=-1)
    currentSpeed = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Current Speed', value=5.0)
    baseSpeed = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Base Speed', value=5.0)
    targetSpeed = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Target Speed', value=15.0)
    accelerationRate = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Acceleration Rate', value=3.0)
    rotationRate = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='rotation Rate', value=3.0)
    explosionRadius = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Explosion Radius ', value=100.0)
    armorDamage = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Armor Damage ', value=100.0)
    deviceDamage = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Device Damage ', value=100.0)
    equipmentID = ComponentProperty(type=CGFMetaTypes.INT, editorName='Equipment Id', value=-1)
    shellID = ComponentProperty(type=CGFMetaTypes.INT, editorName='Shell Id', value=-1)
    explosionPrefabPath = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Explosion Prefab Path', annotations={'path': '*.prefab'})
    trailEffectPath = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Trail Effect Path', annotations={'path': '*.eff'})
    flightTime = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Flight Time', value=10.0)
    deployTime = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Deploy Time', value=5.0)


@registerReplicableComponent
class GuidedMissileReplicableComponent(object):
    category = 'Portal'
    editorTitle = 'Guided Missile Replicable Component'
    replicableAvatarId = ComponentProperty(type=CGFMetaTypes.INT, editorName='IntValue', value=-1)
    isDeploying = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='BoolValue', value=True)

    def __init__(self):
        self.onReplicated = Event()
        self.onDetonate = Event()

    def set_isDeploying(self, old):
        LOG_DEBUG('GuidedMissileReplicableComponent::set_isDeploying')
        self.onReplicated(self, self.replicableAvatarId)

    def set_isDetonateProjectile(self, prev):
        LOG_DEBUG('GuidedMissileReplicableComponent: detonate projectile')
        self.onDetonate(self)
