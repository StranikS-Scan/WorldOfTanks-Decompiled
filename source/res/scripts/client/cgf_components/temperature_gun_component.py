# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/temperature_gun_component.py
import logging
import CGF
import GenericComponents
import Health
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
_logger = logging.getLogger(__name__)

@registerComponent
class OverheatEffect(object):
    editorTitle = 'Overheat Effect'
    category = 'Temperature Guns'
    effectPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Effect Path', value='')


@autoregister(presentInAllWorlds=True)
class TemperatureGunManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, Health.OverheatComponent)
    def onOverheatAdded(self, go, _):
        hierarchy = CGF.HierarchyManager(go.spaceID)
        root = hierarchy.getTopMostParent(go)
        overheatEffectGOList = hierarchy.findComponentsInHierarchy(root, OverheatEffect)
        for overheatGO, component in overheatEffectGOList:
            overheatGO.removeComponentByType(GenericComponents.ParticleComponent)
            overheatGO.createComponent(GenericComponents.ParticleComponent, component.effectPath, True, 1.0)
            overheatGO.activate()

    @onRemovedQuery(CGF.GameObject, Health.OverheatComponent)
    def onOverheatRemoved(self, go, _):
        hierarchy = CGF.HierarchyManager(go.spaceID)
        root = hierarchy.getTopMostParent(go)
        overheatEffectGOList = hierarchy.findComponentsInHierarchy(root, OverheatEffect)
        for overheatGO, _ in overheatEffectGOList:
            overheatGO.deactivate()
