# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/on_shot_components.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import ComponentProperty, registerComponent

@registerComponent
class EffectOnShotComponent(object):
    group = 'Shooting'
    editorTitle = 'Effect On Shot'
    domain = CGF.Domain.ClientEditor
    effectPath = ComponentProperty(type=CGF.PropertyType.String, editorName='Effect Prefab', annotations={'path': '*.prefab'})


@registerComponent
class SoundOnShotComponent(object):
    group = 'Shooting'
    editorTitle = 'Sound On Shot'
    domain = CGF.Domain.ClientEditor
    soundPath = ComponentProperty(type=CGF.PropertyType.String, editorName='Sound Prefab', annotations={'path': '*.prefab'})
