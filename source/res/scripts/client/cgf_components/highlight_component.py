# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/highlight_component.py
import BigWorld
import CGF
from cgf_components import IsHighlighted
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes
from GenericComponents import DynamicModelComponent
from hover_component import IsHovered

class HighlightComponent(CGFComponent):
    editorTitle = 'Highlight'
    category = 'Common'
    color = ComponentProperty(type=CGFMetaTypes.VECTOR4, editorName='Color', value=(0, 0, 0, 1))
    groupName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Group name')


class HighlightManager(CGF.ComponentManager):

    @onAddedQuery(IsHovered, CGF.GameObject)
    def onHoverAdded(self, _, gameObject):
        gameObject.createComponent(IsHighlighted)

    @onRemovedQuery(IsHovered, CGF.GameObject)
    def onHoverRemoved(self, _, gameObject):
        gameObject.removeComponentByType(IsHighlighted)

    @onAddedQuery(IsHighlighted, HighlightComponent, DynamicModelComponent)
    def onDynamicModelHighlightAdded(self, _, highlightComponent, dynamicModelComponent):
        BigWorld.wgSetEdgeDetectEdgeColor(3, highlightComponent.color)
        BigWorld.wgAddEdgeDetectDynamicModel(dynamicModelComponent)
        self.__enableGroupDraw(True, highlightComponent.groupName)

    @onRemovedQuery(IsHighlighted, HighlightComponent, DynamicModelComponent)
    def onDynamicModelHighlightRemoved(self, _, highlightComponent, dynamicModelComponent):
        BigWorld.wgDelEdgeDetectDynamicModel(dynamicModelComponent)
        self.__enableGroupDraw(False, highlightComponent.groupName)

    def __enableGroupDraw(self, enable, groupName):
        highlightQuery = CGF.Query(self.spaceID, (HighlightComponent, DynamicModelComponent))
        for highlightComponent, dynamicModelComponent in highlightQuery:
            if highlightComponent.groupName and highlightComponent.groupName == groupName:
                if enable:
                    BigWorld.wgAddEdgeDetectDynamicModel(dynamicModelComponent)
                else:
                    BigWorld.wgDelEdgeDetectDynamicModel(dynamicModelComponent)
