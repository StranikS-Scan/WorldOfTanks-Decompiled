# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/vehicle_mechanics/staged_jet_boosters.py
from enum import IntEnum
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes

class StagedJetBoostersControllerDescriptor(object):
    category = 'Vehicle Mechanics'
    editorTitle = 'Staged Jet Boosters Controller'
    domain = CGF.DomainOption.DomainAll
    left = ComponentProperty(CGFMetaTypes.LINK, editorName='Left Rocket', value=CGF.GameObject)
    right = ComponentProperty(CGFMetaTypes.LINK, editorName='Right Rocket', value=CGF.GameObject)
    stateController = ComponentProperty(CGFMetaTypes.LINK, editorName='State Controller', value=CGF.GameObject)
