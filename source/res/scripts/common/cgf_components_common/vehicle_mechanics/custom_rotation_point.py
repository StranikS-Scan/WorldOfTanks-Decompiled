# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/vehicle_mechanics/custom_rotation_point.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent

@registerComponent
class CustomRotationPointComponent(object):
    category = 'Vehicle Mechanics'
    editorTitle = 'Custom Rotation Point Component'
    domain = CGF.DomainOption.DomainAll
    minSpeed = ComponentProperty(type=CGFMetaTypes.INT, editorName='Min speed bound (m/s)', value=0)
    minPoints = ComponentProperty(type=CGFMetaTypes.VECTOR3_LIST, editorName='Min points (left, right)', value=[])
    maxSpeed = ComponentProperty(type=CGFMetaTypes.INT, editorName='Max speed bound (m/s)', value=0)
    maxPoints = ComponentProperty(type=CGFMetaTypes.VECTOR3_LIST, editorName='Max points (left, right)', value=[])
    changeRailDirection = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Change rail direction', value=False)

    def __init__(self):
        self.physicsRef = None
        self.originGimletCOMOffset = None
        self.originRailCOMOffset = None
        return
