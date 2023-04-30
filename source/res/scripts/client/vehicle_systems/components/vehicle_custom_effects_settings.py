# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_custom_effects_settings.py
import CGF
import Vehicular
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, autoregister
from constants import IS_CGF_DUMP
if not IS_CGF_DUMP:
    from CustomEffectManager import CustomEffectManager

@registerComponent
class VehicleCustomEffectsSettings(object):
    domain = CGF.DomainOption.DomainClient
    category = 'Vehicle'
    editorTitle = 'Vehicle Custom Effects Settings'
    disableDefaultChassis = ComponentProperty(type=CGFMetaTypes.BOOL, value=False, editorName='Disable Default Chassis Effects')
    disableDefaultHull = ComponentProperty(type=CGFMetaTypes.BOOL, value=False, editorName='Disable Default Hull Effects')
    additionalEngineSoundPC = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Additional Engine Sound PC')
    additionalEngineSoundNPC = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Additional Engine Sound NPC')


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor)
class VehicleCustomEffectsManager(CGF.ComponentManager):

    @onAddedQuery(VehicleCustomEffectsSettings, CGF.GameObject)
    def onAdded(self, effectsSettings, gameObject):
        hierarchy = CGF.HierarchyManager(self.spaceID)
        parent = hierarchy.getParent(gameObject)
        if not parent.isValid():
            return
        vehicleAudition = parent.findComponentByType(Vehicular.VehicleAudition)
        if vehicleAudition:
            vehicleAudition.initAdditionalEngineEvent(effectsSettings.additionalEngineSoundPC, effectsSettings.additionalEngineSoundNPC)
        effects = parent.findComponentByType(CustomEffectManager)
        if effects:
            effects.disableDefaultSelectors(effectsSettings.disableDefaultChassis, effectsSettings.disableDefaultHull)
