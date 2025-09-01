# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/vehicle_mechanics/stationary_reload_sequence_params_component.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent

@registerComponent
class StationaryReloadSequenceParamsComponent(object):
    category = 'Sequence'
    editorTitle = 'Stationary reload sequence params'
    domain = CGF.DomainOption.DomainAll
    sequencePreparingLayer = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Sequence preparing layer', value='')
    sequenceFinishingLayer = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Sequence finishing layer', value='')
