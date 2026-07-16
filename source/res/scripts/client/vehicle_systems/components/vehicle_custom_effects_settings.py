# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_custom_effects_settings.py
import CGF
import Vehicular
from cgf_script.registration import ComponentProperty, registerComponent
from constants import IS_CGF_DUMP
if not IS_CGF_DUMP:
    from CustomEffectManager import CustomEffectManager
else:

    class CustomEffectManager(object):
        pass


@registerComponent
class VehicleCustomEffectsSettings(object):
    domain = CGF.Domain.Client
    category = 'Vehicle'
    editorTitle = 'Vehicle Custom Effects Settings'
    disableDefaultChassis = ComponentProperty(type=CGF.PropertyType.Bool, value=False, editorName='Disable Default Chassis Effects')
    disableDefaultHull = ComponentProperty(type=CGF.PropertyType.Bool, value=False, editorName='Disable Default Hull Effects')
    additionalEngineSoundPC = ComponentProperty(type=CGF.PropertyType.String, value='', editorName='Additional Engine Sound PC')
    additionalEngineSoundNPC = ComponentProperty(type=CGF.PropertyType.String, value='', editorName='Additional Engine Sound NPC')


class VehicleCustomEffectsSystem(CGF.System):
    VehicleCustomEffectsSettings = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(VehicleCustomEffectsSettings))
    CustomEffectManagerAccess = CGF.AccessReaction(CGF.Rw(CustomEffectManager))
    AuditionAccess = CGF.AccessReaction(CGF.Rw(Vehicular.VehicleAudition))
    Reactions = CGF.Reactions(VehicleCustomEffectsSettings, CustomEffectManagerAccess, AuditionAccess)

    def update(self):
        hierarchy = self.hierarchy
        customAccess = self.reaction(self.CustomEffectManagerAccess)
        auditionAccess = self.reaction(self.AuditionAccess)
        for go, settings in self.reaction(self.VehicleCustomEffectsSettings):
            parent = hierarchy.getParent(go)
            if not parent.valid:
                return
            vehicleAudition = auditionAccess.find(parent)
            if vehicleAudition:
                vehicleAudition.initAdditionalEngineEvent(settings.additionalEngineSoundPC, settings.additionalEngineSoundNPC)
            effects = customAccess.find(parent)
            if effects:
                effects.disableDefaultSelectors(settings.disableDefaultChassis, settings.disableDefaultHull)
