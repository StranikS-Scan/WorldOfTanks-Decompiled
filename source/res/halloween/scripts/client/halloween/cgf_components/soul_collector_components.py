# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/cgf_components/soul_collector_components.py
from __future__ import absolute_import
import CGF
import GenericComponents
from cgf_script.registration import ComponentProperty, registerComponent

@registerComponent
class SoulCollectorProgressComponent(object):
    category = 'Halloween'
    editorTitle = 'Soul Collector Progress Component'
    progressSectors = ComponentProperty(type=CGF.PropertyType.Int, editorName='Progress Sectors', value=0)
    sectorOffsetY = ComponentProperty(type=CGF.PropertyType.Float, editorName='Progress Sector Y Offset', value=0.0)
    progressSequence = ComponentProperty(type=CGF.PropertyType.String, editorName='Progress Sequence', value='')


@registerComponent
class SoulCollectorComponent(object):
    category = 'Halloween'
    editorTitle = 'SoulCollectorComponent'
    loadProgressGO = ComponentProperty(type=CGF.PropertyType.Link, editorName='Progress GO', value=CGF.GameObject)
    energyGlowAnimator = ComponentProperty(type=CGF.PropertyType.Link, editorName='Energy Glow Animator', value=GenericComponents.AnimatorComponent)
    auraAnimator = ComponentProperty(type=CGF.PropertyType.Link, editorName='Aura Animator', value=GenericComponents.AnimatorComponent)
    drainerAnimator = ComponentProperty(type=CGF.PropertyType.Link, editorName='Drainer Animator', value=GenericComponents.AnimatorComponent)
