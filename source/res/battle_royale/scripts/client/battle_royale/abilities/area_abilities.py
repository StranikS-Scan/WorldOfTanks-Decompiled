# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/area_abilities.py
from __future__ import absolute_import
import CGF
import Math
from battle_royale.abilities.adaptation_restore_health import AdaptationHealthRestoreEffectArea
from cgf_script.registration import ComponentProperty, registerComponent
from battle_royale_artefacts import ThunderStrike, ZonesCircle

@registerComponent
class AreaAbilityVisualizer(object):
    editorTitle = 'Area Ability Visualizer'
    group = 'Abilities'
    domain = CGF.Domain.ClientEditor
    areaTransform = ComponentProperty(type=CGF.PropertyType.Link, value=CGF.TransformComponent, editorName='Area object')

    def __init__(self):
        super(AreaAbilityVisualizer, self).__init__()
        self.manualRadius = None
        return


class AreaAbilityVisualizationSystem(CGF.System):
    VisualizerActivated = CGF.ActivateReaction(CGF.ReactRw(AreaAbilityVisualizer))
    ThunderStrikeActivated = CGF.ActivateReaction(AreaAbilityVisualizer, CGF.ReactRw(ThunderStrike))
    ZonesCircleActivated = CGF.ActivateReaction(AreaAbilityVisualizer, CGF.ReactRw(ZonesCircle))
    HealthRestoreActivated = CGF.ActivateReaction(AreaAbilityVisualizer, CGF.ReactRw(AdaptationHealthRestoreEffectArea))
    TransformAccess = CGF.AccessReaction(CGF.Rw(CGF.TransformComponent))
    Reactions = CGF.Reactions(VisualizerActivated, ThunderStrikeActivated, ZonesCircleActivated, HealthRestoreActivated, TransformAccess)

    def update(self):
        transformAccess = self.reaction(self.TransformAccess)
        for visualizer in self.reaction(self.VisualizerActivated):
            self.checkManualRadius(visualizer, transformAccess)

        for visualizer, thunderStrike in self.reaction(self.ThunderStrikeActivated):
            self.resizeThunderTransform(visualizer, thunderStrike, transformAccess)

        for visualizer, zonesCircle in self.reaction(self.ZonesCircleActivated):
            self.resizeZonesCircle(visualizer, zonesCircle, transformAccess)

        for visualizer, area in self.reaction(self.HealthRestoreActivated):
            self.resizeHealthRestoreAbilityCircle(visualizer, area, transformAccess)

    def __applyScale(self, transformComponent, radius):
        scaleMatrix = Math.Matrix()
        scaleMatrix.setScale(Math.Vector3(radius, 1.0, radius))
        matrix = transformComponent.transform
        matrix.preMultiply(scaleMatrix)
        transformComponent.transform = matrix

    def __resizeVisualizer(self, visualizer, radius, transformAccess):
        if visualizer.manualRadius is None:
            self.__applyScale(transformAccess.find(visualizer.areaTransform), radius)
        return

    def checkManualRadius(self, visualizer, transformAccess):
        if visualizer.manualRadius is not None:
            self.__applyScale(transformAccess.find(visualizer.areaTransform), visualizer.manualRadius)
        return

    def resizeThunderTransform(self, visualizer, thunderStrike, transformAccess):
        self.__resizeVisualizer(visualizer, thunderStrike.damageRadius, transformAccess)

    def resizeZonesCircle(self, visualizer, zonesCircle, transformAccess):
        self.__resizeVisualizer(visualizer, zonesCircle.radius, transformAccess)

    def resizeHealthRestoreAbilityCircle(self, visualizer, area, transformAccess):
        self.__applyScale(transformAccess.find(visualizer.areaTransform), area.teamMateRestoringRadius)
