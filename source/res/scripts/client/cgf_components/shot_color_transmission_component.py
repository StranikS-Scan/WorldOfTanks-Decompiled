# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/shot_color_transmission_component.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import ComponentProperty, registerComponent

@registerComponent
class ShotColorTransmissionComponent(object):
    editorTitle = 'Gun Shot Effect Component'
    category = 'Animator Triggers'
    domain = CGF.Domain.ClientEditor
    materialParam = ComponentProperty(type=CGF.PropertyType.String, editorName='material property', value='TintColor')
    startValue = ComponentProperty(type=CGF.PropertyType.Float, editorName='start value', value=0.0)
    endValue = ComponentProperty(type=CGF.PropertyType.Float, editorName='end value', value=0.5)
