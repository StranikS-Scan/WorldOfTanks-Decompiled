# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/cgf_components/hexapod_component.py
from __future__ import absolute_import
import BigWorld
import CGF
import Math
from cgf_script.registration import registerComponent
from GenericComponents import DynamicModelComponent, ParticleComponent, RemoveGoDelayedComponent
from Vehicular import HaxapodMovementLegComponent
from EdgeDrawer import EdgeHighlightComponent
from Sound import SoundObject3DComponent
from cgf_components.highlight_component import HighlightComponent
from helpers.EffectMaterialCalculation import calcSurfaceMaterialNearPoint
from material_kinds import EFFECT_MATERIALS
from halloween_dyn_object_cache import getHexapodTerrainEffects
_LEG_EFFECT_OBJ_NAME = 'hexapod_terrain_effect'
_UP_VECTOR = Math.Vector3(0, 1, 0)

class HWHexapodHighlight(object):

    def __init__(self, colorIndex=None):
        self.colorIndex = colorIndex


@registerComponent
class HWIsHexapod(object):
    domain = CGF.Domain.ClientEditor
    editorTitle = 'HW Is Hexapod'
    category = 'Halloween'


@registerComponent
class HWHexapodStepSoundComponent(object):
    domain = CGF.Domain.Client

    def __init__(self, event):
        self.event = event


class HWHexapodSystem(CGF.System):
    VehicleHighlightActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(EdgeHighlightComponent))
    VehicleHighlightDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactHas(EdgeHighlightComponent))
    HexapodActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactHas(HWIsHexapod))
    HexapodLegActivated = CGF.ActivateReaction(CGF.ReactRo(HaxapodMovementLegComponent))
    HexapodLegDeactivated = CGF.DeactivateReaction(CGF.ReactRo(HaxapodMovementLegComponent))
    HexapodDeactivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactHas(HWIsHexapod))
    HexapodHighlightActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(HWHexapodHighlight), CGF.ReactRo(HighlightComponent))
    HexapodStepSoundActivated = CGF.ActivateReaction(CGF.ReactRo(HWHexapodStepSoundComponent), CGF.ReactRo(SoundObject3DComponent))
    HexapodHighlightDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactHas(HWHexapodHighlight), CGF.ReactRo(HighlightComponent))
    HighlightDeactivated = CGF.DeactivateReaction(CGF.ReactRo(HighlightComponent), CGF.ReactRo(DynamicModelComponent))
    HighlightModelIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Ro(HighlightComponent), CGF.Ro(DynamicModelComponent))
    DynamicModelAccess = CGF.AccessReaction(CGF.Ro(DynamicModelComponent))
    EdgeHighlightComponentAccess = CGF.AccessReaction(CGF.Ro(EdgeHighlightComponent))
    Reactions = CGF.Reactions(VehicleHighlightDeactivated, HexapodHighlightDeactivated, HighlightDeactivated, HexapodDeactivated, HexapodLegDeactivated, VehicleHighlightActivated, HexapodActivated, HexapodHighlightActivated, HexapodStepSoundActivated, HexapodLegActivated, HighlightModelIterate, DynamicModelAccess, EdgeHighlightComponentAccess)

    def __init__(self):
        super(HWHexapodSystem, self).__init__()
        self._hexapodGoByVehicleAppearance = {}
        self._effects = {}
        self._defaultEffect = None
        return

    def _init(self):
        self._effects = getHexapodTerrainEffects()
        self._defaultEffect = self._effects.get('default')

    def update(self):
        q = CGF.CommandQueue(self.gom)
        dynamicModelAccess = self.reaction(self.DynamicModelAccess)
        edgeHighlightComponentAccess = self.reaction(self.EdgeHighlightComponentAccess)
        highlightModelIterate = self.reaction(self.HighlightModelIterate)
        for go in self.reaction(self.VehicleHighlightDeactivated):
            self.onEdgeHighlightComponentRemoved(go, q)

        for go, highlightComponent in self.reaction(self.HexapodHighlightDeactivated):
            self.onHexapodHighlightRemoved(go, highlightComponent, dynamicModelAccess, highlightModelIterate)

        for highlightComponent, dynamicModelComponent in self.reaction(self.HighlightDeactivated):
            self.onHighlightComponentRemoved(highlightComponent, dynamicModelComponent, dynamicModelAccess)

        for go in self.reaction(self.HexapodDeactivated):
            self.onHexapodComponentRemoved(go, q, edgeHighlightComponentAccess)

        for leg in self.reaction(self.HexapodLegDeactivated):
            leg.onLegMovementFinished.remove(self._onLegMovementFinished)

        for go, edgeHighlightComp in self.reaction(self.VehicleHighlightActivated):
            self.onEdgeHighlightComponentAdded(go, edgeHighlightComp, q)

        for go in self.reaction(self.HexapodActivated):
            self.onHexapodComponentAdded(go, q, edgeHighlightComponentAccess)

        for go, hexapodHighlight, highlightComponent in self.reaction(self.HexapodHighlightActivated):
            self.onHexapodHighlightAdded(go, hexapodHighlight, highlightComponent, dynamicModelAccess, highlightModelIterate)

        for hexapodStepSoundComponent, sound3dComponent in self.reaction(self.HexapodStepSoundActivated):
            self.onStepSoundAdded(hexapodStepSoundComponent, sound3dComponent)

        for leg in self.reaction(self.HexapodLegActivated):
            leg.onLegMovementFinished.add(self._onLegMovementFinished)

    def onEdgeHighlightComponentAdded(self, go, edgeHighlightComp, queue):
        hexapod = self._hexapodGoByVehicleAppearance.get(go.uuid)
        if hexapod and not hexapod.hasComponent(HWHexapodHighlight):
            queue.createComponent(hexapod, HWHexapodHighlight, edgeHighlightComp.colorIndex + 1)

    def onHexapodComponentRemoved(self, go, queue, edgeHighlightComponentAccess):
        appearanceGameObject = self.hierarchy.getParent(go)
        if appearanceGameObject.uuid in self._hexapodGoByVehicleAppearance:
            self._hexapodGoByVehicleAppearance.pop(appearanceGameObject.uuid)
        edgeHighlightComp = edgeHighlightComponentAccess.find(appearanceGameObject)
        if edgeHighlightComp and go.hasComponent(HWHexapodHighlight):
            queue.removeComponent(go, HWHexapodHighlight)

    def onHexapodComponentAdded(self, go, queue, edgeHighlightComponentAccess):
        self._init()
        appearanceGameObject = self.hierarchy.getParent(go)
        self._hexapodGoByVehicleAppearance[appearanceGameObject.uuid] = go
        edgeHighlightComp = edgeHighlightComponentAccess.find(appearanceGameObject)
        if edgeHighlightComp and not go.hasComponent(HWHexapodHighlight):
            queue.createComponent(go, HWHexapodHighlight, edgeHighlightComp.colorIndex + 1)

    def onEdgeHighlightComponentRemoved(self, go, queue):
        hexapod = self._hexapodGoByVehicleAppearance.get(go.uuid)
        if hexapod and hexapod.hasComponent(HWHexapodHighlight):
            queue.removeComponent(hexapod, HWHexapodHighlight)

    def onHexapodHighlightAdded(self, go, hexapodHighlight, highlightComponent, dynamicModelAccess, highlightModelIterate):
        self.__enableGroupDraw(True, go, highlightComponent.groupName, dynamicModelAccess, highlightModelIterate, hexapodHighlight.colorIndex)

    def onHexapodHighlightRemoved(self, go, highlightComponent, dynamicModelAccess, highlightModelIterate):
        self.__enableGroupDraw(False, go, highlightComponent.groupName, dynamicModelAccess, highlightModelIterate)

    def onHighlightComponentRemoved(self, highlightComponent, dynamicModelComponent, dynamicModelAccess):
        self.__edgeDetectDynamicModel(False, highlightComponent, dynamicModelComponent, dynamicModelAccess)

    def _onLegMovementFinished(self, position):
        surfaceMaterial = calcSurfaceMaterialNearPoint(position, _UP_VECTOR, self.spaceID)
        effectName = ''
        if surfaceMaterial.effectIdx < len(EFFECT_MATERIALS):
            effectName = EFFECT_MATERIALS[surfaceMaterial.effectIdx]
        effect = self._effects.get(effectName, self._defaultEffect)
        if not effect:
            return
        queue = CGF.CommandQueue(self.gom)
        go = queue.createGameObject(name=_LEG_EFFECT_OBJ_NAME)
        queue.createComponent(go, CGF.TransformComponent, position)
        queue.createComponent(go, CGF.HierarchyComponent)
        queue.createComponent(go, RemoveGoDelayedComponent, effect.duration)
        queue.createComponent(go, ParticleComponent, effect.effect, True, effect.rate)
        if effect.sound:
            queue.createComponent(go, HWHexapodStepSoundComponent, effect.sound)
            queue.createComponent(go, SoundObject3DComponent, False)
        queue.activateGameObject(go)

    def __edgeDetectDynamicModel(self, enable, highlightComponent, dynamicModelComponent, dynamicModelAccess, colorIndex=None):
        dynamicModel = dynamicModelComponent
        highlightObj = self.gom.gameObject(highlightComponent.overridenHighlightModel)
        if highlightObj:
            overridenHighlightModel = dynamicModelAccess.find(highlightObj)
            if overridenHighlightModel:
                dynamicModel = overridenHighlightModel
        if enable:
            colorIndex = colorIndex if colorIndex else highlightComponent.colorIndex
            BigWorld.wgAddEdgeDetectDynamicModel(dynamicModel, colorIndex, highlightComponent.drawerMode)
        else:
            BigWorld.wgDelEdgeDetectDynamicModel(dynamicModel)

    def __enableGroupDraw(self, enable, go, groupName, dynamicModelAccess, highlightModelIterate, colorIndex=None):
        for highlightComponent, dynamicModelComponent in highlightModelIterate:
            if highlightComponent.groupName and highlightComponent.groupName == groupName and go.uuid == highlightComponent.overridenHighlightModel:
                self.__edgeDetectDynamicModel(enable, highlightComponent, dynamicModelComponent, dynamicModelAccess, colorIndex)

    def onStepSoundAdded(self, hexapodStepSoundComponent, sound3dComponent):
        sound3dComponent.play(hexapodStepSoundComponent.event)
