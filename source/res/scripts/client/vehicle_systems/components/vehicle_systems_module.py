# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_systems_module.py
import CGF
import GenericComponents
from cgf_components.client_worlds_helpers import clientWorldsPredicate, ClientWorld
from cgf_script.registration import registerModule
from vehicle_systems.components.debris_crashed_track_component import DebrisCrashedTrackComponent
from vehicle_systems.components.debris_crashed_track_manager import DebrisCrashedTrackSystem
from vehicle_systems.components.decal_manager import DecalComponentSystem
from vehicle_systems.components.insignia_stickers_receiver_component import InsigniaStickersReceiverSystem, InsigniaStickersReceiverComponent
from vehicle_systems.components.shot_damage_components import DamageStickerSystem, DamageStickerComponent
from vehicle_systems.components.vehicle_assembly_manager import VehicleAssemblySystem, HangarVehicleStateSwitcherSystem
from vehicle_systems.components.vehicle_custom_effects_settings import VehicleCustomEffectsSystem, VehicleCustomEffectsSettings
from vehicle_systems.components.vehicle_pickup_manager import VehiclePickupSystem

@registerModule
class VehicleSystemsModule(object):
    name = 'Vehicle Module'
    desc = 'Vehicle Core Systems'
    group = 'Vehicle'
    systems = [CGF.RegisterSystem(VehicleCustomEffectsSystem, domain=CGF.Domain.ClientEditor),
     CGF.RegisterSystem(DamageStickerSystem, domain=CGF.Domain.ClientEditor, updateAfter=(CGF.TransformUpdateSystem,)),
     CGF.RegisterSystem(DebrisCrashedTrackSystem, domain=CGF.Domain.ClientEditor),
     CGF.RegisterSystem(DecalComponentSystem, domain=CGF.Domain.ClientEditor),
     CGF.RegisterSystem(InsigniaStickersReceiverSystem, domain=CGF.Domain.ClientEditor, updateAfter=(CGF.TransformUpdateSystem, GenericComponents.ModelComponentSystem)),
     CGF.RegisterSystem(VehicleAssemblySystem, domain=CGF.Domain.ClientEditor, predicate=clientWorldsPredicate(ClientWorld.AllWorlds)),
     CGF.RegisterSystem(VehiclePickupSystem, domain=CGF.Domain.ClientEditor, updateAfter=(CGF.TransformUpdateSystem,)),
     CGF.RegisterSystem(HangarVehicleStateSwitcherSystem, domain=CGF.Domain.ClientEditor, predicate=clientWorldsPredicate(ClientWorld.HANGAR | ClientWorld.EDITOR))]
    components = [VehicleCustomEffectsSettings,
     DamageStickerComponent,
     InsigniaStickersReceiverComponent,
     DebrisCrashedTrackComponent]
