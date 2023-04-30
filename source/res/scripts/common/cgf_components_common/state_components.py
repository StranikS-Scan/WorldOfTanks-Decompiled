# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/state_components.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerReplicableComponent, registerComponent
_DEFAULT_HEALTH = 300

class DEATH_REASON(object):
    UNKNOWN = 0
    DESTROYED = 1


@registerReplicableComponent
class DeathComponent(object):
    category = 'Common'
    editorTitle = 'Death Component'


@registerReplicableComponent
class HealthComponent(object):
    category = 'Common'
    editorTitle = 'Health Component'
    maxHealth = ComponentProperty(type=CGFMetaTypes.INT, editorName='MaxHealth', value=_DEFAULT_HEALTH)
    health = ComponentProperty(type=CGFMetaTypes.INT, editorName='CurrentHealth', value=_DEFAULT_HEALTH)


@registerComponent
class RemoveOnDeathComponent(object):
    category = 'Death'
    editorTitle = 'Remove On Death Component'
    domain = CGF.DomainOption.DomainAll
    delay = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Delay', value=0.0)


@registerComponent
class SpawnOnDeathComponent(object):
    category = 'Death'
    editorTitle = 'Spawn On Death Component'
    domain = CGF.DomainOption.DomainAll
    prefabPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Spawn Prefab', annotations={'path': '*.prefab'})
    delay = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Delay', value=0.0)
    attachToGO = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Attach to GO', value=True)


@registerComponent
class StateSwitcherComponent(object):
    category = 'Common'
    editorTitle = 'State Switcher'
    domain = CGF.DomainOption.DomainAll
    normal = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Normal', value=CGF.GameObject)
    damaged = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Damaged', value=CGF.GameObject)
    critical = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Critical', value=CGF.GameObject)

    def __init__(self):
        self.callback = None
        return
