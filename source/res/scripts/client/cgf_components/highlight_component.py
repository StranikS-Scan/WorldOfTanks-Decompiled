# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/highlight_component.py
import BigWorld
import CGF
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from GenericComponents import DynamicModelComponent
from hover_component import IsHoveredComponent, SelectionComponent

@registerComponent
class IsHighlighted(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor


@registerComponent
class HighlightComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Highlight'
    category = 'Common'
    color = ComponentProperty(type=CGFMetaTypes.VECTOR4, editorName='Color', value=(0, 0, 0, 1), annotations={'colorPicker': {'255Range': False,
                     'useAlpha': True}})
    groupName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Group name')
    drawerMode = ComponentProperty(type=CGFMetaTypes.INT, value=0, editorName='drawerMode')
    colorIndex = ComponentProperty(type=CGFMetaTypes.INT, value=4, editorName='colorIndex')
    overridenHighlightModel = ComponentProperty(type=CGFMetaTypes.LINK, value=CGF.GameObject, editorName='overridenHighlightModel')

    def __init__(self):
        super(HighlightComponent, self).__init__()
        self.callbackID = None
        return


class HighlightManager(CGF.ComponentManager):

    @onAddedQuery(IsHoveredComponent, SelectionComponent, CGF.GameObject)
    def onHoverAdded(self, _, selection, gameObject):
        if selection.highlight:
            gameObject.createComponent(IsHighlighted)

    @onRemovedQuery(IsHoveredComponent, SelectionComponent, CGF.GameObject)
    def onHoverRemoved(self, _, selection, gameObject):
        if selection.highlight:
            gameObject.removeComponentByType(IsHighlighted)

    @onAddedQuery(IsHighlighted, HighlightComponent, DynamicModelComponent)
    def onDynamicModelHighlightAdded(self, _, highlightComponent, dynamicModelComponent):
        BigWorld.wgSetEdgeDetectEdgeColor(highlightComponent.colorIndex - 1, highlightComponent.color)
        self.__edgeDetectDynamicModel(True, highlightComponent, dynamicModelComponent)
        self.__enableGroupDraw(True, highlightComponent.groupName)

    @onRemovedQuery(IsHighlighted, HighlightComponent, DynamicModelComponent)
    def onDynamicModelHighlightRemoved(self, _, highlightComponent, dynamicModelComponent):
        self.__edgeDetectDynamicModel(False, highlightComponent, dynamicModelComponent)
        self.__enableGroupDraw(False, highlightComponent.groupName)

    @onRemovedQuery(HighlightComponent, DynamicModelComponent)
    def onHighlightComponentRemoved(self, highlightComponent, dynamicModelComponent):
        self.__edgeDetectDynamicModel(False, highlightComponent, dynamicModelComponent)

    def __edgeDetectDynamicModel(self, enable, highlightComponent, dynamicModelComponent):
        dynamicModel = dynamicModelComponent
        if highlightComponent.overridenHighlightModel.isValid():
            overridenHighlightModel = highlightComponent.overridenHighlightModel.findComponentByType(DynamicModelComponent)
            if overridenHighlightModel:
                dynamicModel = overridenHighlightModel
        if enable:
            BigWorld.wgAddEdgeDetectDynamicModel(dynamicModel, highlightComponent.colorIndex, highlightComponent.drawerMode)
        else:
            BigWorld.wgDelEdgeDetectDynamicModel(dynamicModel)

    def __enableGroupDraw(self, enable, groupName):
        highlightQuery = CGF.Query(self.spaceID, (HighlightComponent, DynamicModelComponent))
        for highlightComponent, dynamicModelComponent in highlightQuery:
            if highlightComponent.groupName and highlightComponent.groupName == groupName:
                self.__edgeDetectDynamicModel(enable, highlightComponent, dynamicModelComponent)
