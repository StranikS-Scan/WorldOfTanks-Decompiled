# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/cgf_components/loot_transparency.py
import CGF
import GenericComponents
import Math
import Triggers
from aih_constants import CTRL_MODE_NAME, CTRL_MODES
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from constants import IS_CLIENT
if IS_CLIENT:
    from Avatar import PlayerAvatar
else:

    class PlayerAvatar(object):
        pass


@registerComponent
class LootSensorComponent(object):
    editorTitle = 'Loot Sensor'
    category = 'Steel Hunter'
    domain = CGF.DomainOption.DomainClient
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AreaTrigger', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        super(LootSensorComponent, self).__init__()
        self.enterReactionID = -1
        self.exitReactionID = -1


@registerComponent
class LootTransparencyTriggerComponent(object):
    editorTitle = 'Loot Transparency Sensor'
    category = 'Steel Hunter'
    domain = CGF.DomainOption.DomainClient
    modelMaterial = ComponentProperty(type=CGFMetaTypes.STRING, editorName='MaterialName', value='TintlColor')
    baseColor = ComponentProperty(type=CGFMetaTypes.VECTOR4, editorName='Base Color', value=Math.Vector4(1.0, 1.0, 1, 1.0), annotations={'colorPicker': {'255Range': False,
                     'useAlpha': True}})
    alphaColor = ComponentProperty(type=CGFMetaTypes.VECTOR4, editorName='Alpha Color', value=Math.Vector4(1.0, 1.0, 1, 0.5), annotations={'colorPicker': {'255Range': False,
                     'useAlpha': True}})
    baseOpacity = ComponentProperty(CGFMetaTypes.FLOAT, editorName='Base Opacity', value=1.0)
    alphaOpacity = ComponentProperty(CGFMetaTypes.FLOAT, editorName='Alpha Opacity', value=0.5)
    baseEmissionRate = ComponentProperty(CGFMetaTypes.FLOAT, editorName='Base Emission Rate', value=1.0)
    alphaEmissionRate = ComponentProperty(CGFMetaTypes.FLOAT, editorName='Alpha Emission Rate', value=0.5)
    model = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Particles', value=GenericComponents.DynamicModelComponent)
    particles = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Model', value=GenericComponents.ParticleComponent)

    def __init__(self):
        super(LootTransparencyTriggerComponent, self).__init__()
        self.enterReactionID = -1
        self.exitReactionID = -1


@bonusCapsManager(bonusCap=ARENA_BONUS_TYPE_CAPS.BATTLEROYALE)
class LootSensorComponentManager(CGF.ComponentManager):
    _LOOT_SENSOR_PREFAB = 'content/CGFPrefabs/steel_hunter/player_loot_sensor.prefab'
    _SENSOR_CTRL_MODES = (CTRL_MODES.index(CTRL_MODE_NAME.SNIPER), CTRL_MODES.index(CTRL_MODE_NAME.DUAL_GUN))

    @onAddedQuery(PlayerAvatar, CGF.GameObject)
    def onAvatarAdded(self, _, gameObject):
        CGF.loadGameObjectIntoHierarchy(self._LOOT_SENSOR_PREFAB, gameObject, Math.Vector3(0.0))

    @onAddedQuery(LootSensorComponent)
    def onAdded(self, lootSensor):
        trigger = lootSensor.trigger()
        if trigger is not None:
            lootSensor.enterReactionID = trigger.addEnterReaction(self.__onEnter)
            lootSensor.exitReactionID = trigger.addExitReaction(self.__onExit)
        return

    @onRemovedQuery(LootSensorComponent)
    def onRemoved(self, lootSensor):
        trigger = lootSensor.trigger()
        if trigger is not None:
            trigger.removeEnterReaction(lootSensor.enterReactionID)
            lootSensor.enterReactionID = -1
            trigger.removeExitReaction(lootSensor.exitReactionID)
            lootSensor.exitReactionID = -1
        return

    def __onEnter(self, who, _):
        transparencyTrigger = who.findComponentByType(LootTransparencyTriggerComponent)
        if transparencyTrigger is not None:
            self.__changeModelMaterial(transparencyTrigger.model(), transparencyTrigger.modelMaterial, transparencyTrigger.alphaColor)
            self.__changeParticleProperies(transparencyTrigger.particles(), transparencyTrigger.alphaOpacity, transparencyTrigger.alphaEmissionRate)
        return

    def __onExit(self, who, _):
        transparencyTrigger = who.findComponentByType(LootTransparencyTriggerComponent)
        if transparencyTrigger is not None:
            self.__changeModelMaterial(transparencyTrigger.model(), transparencyTrigger.modelMaterial, transparencyTrigger.baseColor)
            self.__changeParticleProperies(transparencyTrigger.particles(), transparencyTrigger.baseOpacity, transparencyTrigger.baseEmissionRate)
        return

    def __changeParticleProperies(self, particle, opacity, emissionRate):
        if particle is not None:
            particle.opacity = opacity
            particle.emissionRate = emissionRate
        return

    def __changeModelMaterial(self, model, materialName, color):
        if model is not None:
            model.setMaterialParameterVector4(materialName, color)
        return
