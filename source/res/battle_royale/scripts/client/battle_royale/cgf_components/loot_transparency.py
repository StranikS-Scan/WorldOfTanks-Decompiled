# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/cgf_components/loot_transparency.py
from __future__ import absolute_import
import CGF
import GenericComponents
import Math
import Triggers
from aih_constants import CTRL_MODE_NAME, CTRL_MODES
from cgf_script.registration import ComponentProperty, registerComponent
from constants import IS_CLIENT
if IS_CLIENT:
    from Avatar import PlayerAvatar
else:

    class PlayerAvatar(object):
        pass


@registerComponent
class LootSensorComponent(object):
    editorTitle = 'Loot Sensor'
    group = 'Steel Hunter'
    domain = CGF.Domain.Client
    trigger = ComponentProperty(type=CGF.PropertyType.Link, editorName='AreaTrigger', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        super(LootSensorComponent, self).__init__()
        self.enterReactionID = -1
        self.exitReactionID = -1


@registerComponent
class LootTransparencyTriggerComponent(object):
    editorTitle = 'Loot Transparency Sensor'
    group = 'Steel Hunter'
    domain = CGF.Domain.Client
    modelMaterial = ComponentProperty(type=CGF.PropertyType.String, editorName='MaterialName', value='TintlColor')
    baseColor = ComponentProperty(type=CGF.PropertyType.Vector4, editorName='Base Color', value=Math.Vector4(1.0, 1.0, 1, 1.0), annotations={'colorPicker': {'255Range': False,
                     'useAlpha': True}})
    alphaColor = ComponentProperty(type=CGF.PropertyType.Vector4, editorName='Alpha Color', value=Math.Vector4(1.0, 1.0, 1, 0.5), annotations={'colorPicker': {'255Range': False,
                     'useAlpha': True}})
    baseOpacity = ComponentProperty(CGF.PropertyType.Float, editorName='Base Opacity', value=1.0)
    alphaOpacity = ComponentProperty(CGF.PropertyType.Float, editorName='Alpha Opacity', value=0.5)
    baseEmissionRate = ComponentProperty(CGF.PropertyType.Float, editorName='Base Emission Rate', value=1.0)
    alphaEmissionRate = ComponentProperty(CGF.PropertyType.Float, editorName='Alpha Emission Rate', value=0.5)
    particles = ComponentProperty(type=CGF.PropertyType.Link, editorName='Particles', value=GenericComponents.DynamicModelComponent)
    model = ComponentProperty(type=CGF.PropertyType.Link, editorName='Model', value=GenericComponents.ParticleComponent)

    def __init__(self):
        super(LootTransparencyTriggerComponent, self).__init__()
        self.enterReactionID = -1
        self.exitReactionID = -1


class LootSensorSystem(CGF.System):
    _LOOT_SENSOR_PREFAB = 'content/CGFPrefabs/steel_hunter/player_loot_sensor.prefab'
    _SENSOR_CTRL_MODES = (CTRL_MODES.index(CTRL_MODE_NAME.SNIPER), CTRL_MODES.index(CTRL_MODE_NAME.DUAL_GUN))
    AvatarActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(PlayerAvatar))
    LootSensorActivated = CGF.ActivateReaction(CGF.ReactRw(LootSensorComponent))
    LootSensorDeactivated = CGF.DeactivateReaction(CGF.ReactRw(LootSensorComponent))
    AreaTriggerAccess = CGF.AccessReaction(CGF.Rw(Triggers.AreaTriggerComponent))
    DynamicModelAccess = CGF.AccessReaction(CGF.Rw(GenericComponents.DynamicModelComponent))
    ParticleAccess = CGF.AccessReaction(CGF.Rw(GenericComponents.ParticleComponent))
    TransparencyTriggerAccess = CGF.AccessReaction(CGF.Rw(LootTransparencyTriggerComponent))
    Reactions = CGF.Reactions(AvatarActivated, LootSensorActivated, LootSensorDeactivated, AreaTriggerAccess, DynamicModelAccess, ParticleAccess, TransparencyTriggerAccess)

    def update(self):
        triggerAccess = self.reaction(self.AreaTriggerAccess)
        for lootSensor in self.reaction(self.LootSensorDeactivated):
            self.onRemoved(lootSensor, triggerAccess)

        for gameObject, _ in self.reaction(self.AvatarActivated):
            self.onAvatarAdded(gameObject)

        for lootSensor in self.reaction(self.LootSensorActivated):
            self.onAdded(lootSensor, triggerAccess)

    def onAvatarAdded(self, gameObject):
        CGF.loadAndCreatePrefabWithParent(self._LOOT_SENSOR_PREFAB, gameObject, Math.Vector3(0.0))

    def onAdded(self, lootSensor, triggerAccess):
        trigger = triggerAccess.find(lootSensor.trigger)
        if trigger:
            lootSensor.enterReactionID = trigger.addEnterReaction(self.__onEnter)
            lootSensor.exitReactionID = trigger.addExitReaction(self.__onExit)

    def onRemoved(self, lootSensor, triggerAccess):
        trigger = triggerAccess.find(lootSensor.trigger)
        if trigger:
            trigger.removeEnterReaction(lootSensor.enterReactionID)
            lootSensor.enterReactionID = -1
            trigger.removeExitReaction(lootSensor.exitReactionID)
            lootSensor.exitReactionID = -1

    def __onEnter(self, who, _):
        transparencyTriggerAccess = self.reaction(self.TransparencyTriggerAccess)
        modelAccess = self.reaction(self.DynamicModelAccess)
        particleAccess = self.reaction(self.ParticleAccess)
        transparencyTrigger = transparencyTriggerAccess.find(who)
        if transparencyTrigger is not None:
            self.__changeModelMaterial(modelAccess.find(transparencyTrigger.model), transparencyTrigger.modelMaterial, transparencyTrigger.alphaColor)
            self.__changeParticleProperies(particleAccess.find(transparencyTrigger.particles), transparencyTrigger.alphaOpacity, transparencyTrigger.alphaEmissionRate)
        return

    def __onExit(self, who, _):
        transparencyTriggerAccess = self.reaction(self.TransparencyTriggerAccess)
        modelAccess = self.reaction(self.DynamicModelAccess)
        particleAccess = self.reaction(self.ParticleAccess)
        transparencyTrigger = transparencyTriggerAccess.find(who)
        if transparencyTrigger is not None:
            self.__changeModelMaterial(modelAccess.find(transparencyTrigger.model), transparencyTrigger.modelMaterial, transparencyTrigger.baseColor)
            self.__changeParticleProperies(particleAccess.find(transparencyTrigger.particles), transparencyTrigger.baseOpacity, transparencyTrigger.baseEmissionRate)
        return

    def __changeParticleProperies(self, particle, opacity, emissionRate):
        if particle:
            particle.opacity = opacity
            particle.emissionRate = emissionRate

    def __changeModelMaterial(self, model, materialName, color):
        if model:
            model.setMaterialParameterVector4(materialName, color)
