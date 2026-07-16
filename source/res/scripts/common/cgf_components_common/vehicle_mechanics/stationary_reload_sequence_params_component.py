# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/vehicle_mechanics/stationary_reload_sequence_params_component.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import ComponentProperty, registerComponent

@registerComponent
class StationaryReloadSequenceParamsComponent(object):
    category = 'Sequence'
    editorTitle = 'Stationary reload sequence params'
    domain = CGF.Domain.All
    sequencePreparingLayer = ComponentProperty(type=CGF.PropertyType.String, editorName='Sequence preparing layer', value='')
    sequenceFinishingLayer = ComponentProperty(type=CGF.PropertyType.String, editorName='Sequence finishing layer', value='')
