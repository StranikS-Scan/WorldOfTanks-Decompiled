# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/vehicle_mechanics/crest_moving_sequence_params_component.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import ComponentProperty, registerComponent

@registerComponent
class CrestMovingSequenceParamsComponent(object):
    category = 'Sequence'
    editorTitle = 'Crest moving sequence params'
    domain = CGF.Domain.All
    sequence0PosLayer = ComponentProperty(type=CGF.PropertyType.String, editorName='Sequence 0 position layer', value='')
    sequence1PosLayer = ComponentProperty(type=CGF.PropertyType.String, editorName='Sequence 1 position layer', value='')
    sequence2PosLayer = ComponentProperty(type=CGF.PropertyType.String, editorName='Sequence 2 position layer', value='')
    sequence3PosLayer = ComponentProperty(type=CGF.PropertyType.String, editorName='Sequence 3 position layer', value='')
