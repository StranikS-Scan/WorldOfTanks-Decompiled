# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/cgf_components/highlight_manager.py
import BigWorld
import CGF
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from cgf_script.component_meta_class import CGFComponent
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

class IsHighlighted(CGFComponent):
    pass


class HighlightComponent(CGFComponent):

    def __init__(self, owner, colorIndex, drawMode=0, playersTank=False, includeAuxiliaryEmbodiments=True, disableDepthTest=True, onHighlightCallback=None, onFadeCallback=None):
        super(HighlightComponent, self).__init__()
        self.owner = owner
        self.colorIndex = colorIndex
        self.drawMode = drawMode
        self.playersTank = playersTank
        self.includeAuxiliaryEmbodiments = includeAuxiliaryEmbodiments
        self.disableDepthTest = disableDepthTest
        self.onHighlightCallback = onHighlightCallback
        self.onFadeCallback = onFadeCallback


class HighlightGroupComponent(CGFComponent):

    def __init__(self, selectionGroupIdx):
        super(HighlightGroupComponent, self).__init__()
        self.selectionGroupIdx = selectionGroupIdx


@autoregister(presentInAllWorlds=True)
class HighlightManager(CGF.ComponentManager):
    _hangarSpace = dependency.descriptor(IHangarSpace)

    @onAddedQuery(IsHighlighted, HighlightComponent)
    def onIsHighlightedAdded(self, _, highlightComponent):
        BigWorld.wgAddEdgeDetectEntity(highlightComponent.owner, highlightComponent.colorIndex, highlightComponent.drawMode, highlightComponent.playersTank, highlightComponent.includeAuxiliaryEmbodiments, highlightComponent.disableDepthTest)
        if highlightComponent.onHighlightCallback is not None:
            highlightComponent.onHighlightCallback()
        return

    @onRemovedQuery(IsHighlighted, HighlightComponent)
    def onIsHighlightedRemoved(self, _, highlightComponent):
        BigWorld.wgDelEdgeDetectEntity(highlightComponent.owner)
        if highlightComponent.onFadeCallback is not None:
            highlightComponent.onFadeCallback()
        return

    @onAddedQuery(HighlightComponent)
    def onHighlightComponentAdded(self, highlightComponent):
        selectedEntity = BigWorld.player().selectedEntity
        if selectedEntity is not None and selectedEntity.id == highlightComponent.owner.id:
            self.toggleEntityHighlight(highlightComponent.owner, True)
        return

    @onRemovedQuery(HighlightComponent, CGF.GameObject)
    def onHighlightComponentRemoved(self, _, go):
        go.removeComponentByType(IsHighlighted)

    @classmethod
    def toggleEntityHighlight(cls, entity, isHighlighted):
        highlightComponent = entity.entityGameObject.findComponentByType(HighlightComponent)
        if highlightComponent is None:
            return
        else:
            groupComponent = entity.entityGameObject.findComponentByType(HighlightGroupComponent)
            if groupComponent is not None:
                highlightQuery = CGF.Query(cls._hangarSpace.spaceID, (HighlightGroupComponent, CGF.GameObject))
                for component, go in highlightQuery:
                    if component.selectionGroupIdx == groupComponent.selectionGroupIdx:
                        cls._updateHighlightComponent(go, isHighlighted)

            else:
                cls._updateHighlightComponent(entity.entityGameObject, isHighlighted)
            return

    @classmethod
    def _updateHighlightComponent(cls, go, isHighlighted):
        if isHighlighted:
            if go.findComponentByType(IsHighlighted) is None:
                go.createComponent(IsHighlighted)
        else:
            go.removeComponentByType(IsHighlighted)
        return
