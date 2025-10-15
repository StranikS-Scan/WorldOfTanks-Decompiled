# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/common/portal_common_cgf/force_field/components.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent

@registerComponent
class ForceFieldAffected(object):
    domain = CGF.DomainOption.DomainAll
    category = 'Portal'
    editorTitle = 'ForceFieldAffected'

    def __init__(self, forceFieldGO):
        self.forceFieldGO = forceFieldGO


@registerComponent
class CylindricalForceFieldComponent(object):
    domain = CGF.DomainOption.DomainAll
    category = 'Portal'
    editorTitle = 'CylindricalForceField'

    def __init__(self):
        self.vehiclesToIgnore = set()
        self.enterReactionID = None
        self.exitReactionID = None
        return

    def destroy(self):
        self.vehiclesToIgnore.clear()
        self.vehiclesToIgnore = None
        return

    radius = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Radius', value=5.0)
    maxForce = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Max Force', value=10.0)
    forceExponent = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Force Exponent', value=2.0)
    falloffStart = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Falloff Start', value=0.2)
    isActive = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Is force field active', value=True)
