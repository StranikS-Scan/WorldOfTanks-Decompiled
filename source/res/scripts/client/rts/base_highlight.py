# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/rts/base_highlight.py
import CGF
import GenericComponents
import Triggers
from Math import Vector3
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery, autoregister
from math_utils import createSRTMatrix

class BaseHighlightComponent(CGFComponent):
    id = ComponentProperty(CGFMetaTypes.INT, value=0, editorName='ID')
    teamID = ComponentProperty(CGFMetaTypes.INT, value=0, editorName='TeamID')
    hovered = ComponentProperty(CGFMetaTypes.BOOL, value=False, editorName='Hovered')
    animator = ComponentProperty(CGFMetaTypes.LINK, value=GenericComponents.AnimatorComponent, editorName='Animator')

    def trigger(self):
        if self.animator is not None:
            self.animator().setTrigger('click')
        return

    def setHovered(self, value):
        self.hovered = value
        if self.animator is not None:
            self.animator().setBoolParam('hovered', value)
        return


@autoregister(presentInEditor=True, presentInAllWorlds=True)
class BaseHighlightComponentManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, BaseHighlightComponent, Triggers.CylinderAreaComponent, tickGroup='Simulation')
    def onAdded(self, go, highlighter, area):
        transform = go.findComponentByType(GenericComponents.TransformComponent)
        animator = go.findComponentByType(GenericComponents.AnimatorComponent)
        if transform is None or animator is None:
            return
        else:
            radius = area.radius
            translation = transform.position
            transform.transform = createSRTMatrix((radius, 1.0, radius), Vector3(), translation)
            highlighter.setHovered(highlighter.hovered)
            return
