# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/cgf_client_module.py
from __future__ import absolute_import
import BigWorld
import CGF
import CameraComponents
import Vehicular
import cgf_components.vehicle_mechanics_components
import GenericComponents
import GpuDecals
from CustomEffectManager import CustomEffectManager, CustomEffectManagerSystem
from DestructibleEntityState import DestructibleEntityStatesSystem
from DetachedTurret import DetachedTurretSystem
from cgf_components.audition_component_2d import AuditionsSystem
from cgf_components.mechanic_components.cyclic_rocket.accelerator_status_tracker import AcceleratorStatusTrackerComponentSystem, AcceleratorStatusTrackerComponent
from cgf_components.mechanic_components.cyclic_rocket.nozzle_controller import NozzleController, NozzleActivationSyncComponent, NozzleControllerComponentSystem
from cgf_components.mechanic_components.cyclic_rocket.staged_jet_boosters import StagedJetBoostersComponentSystem
from constants import IS_EDITOR, IS_CGF_DUMP
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from cgf_components.client_worlds_helpers import clientWorldsPredicate, ClientWorld
from cgf_components.temperature_gun_rtpc_component import TemperatureGunMechanicSystem
from constants import HAS_DEV_RESOURCES, SERVER_TICK_LENGTH
from cgf_script.registration import bonusCapsPredicate, registerModule
from cgf_components.accuracy_stacks_manager import AccuracyStacksMechanicSystem
from cgf_components.arena_camera_manager import ArenaCameraSystem
from cgf_components.armor_inspector_component import ArmorInspectorComponent, ArmorInspectorSystem
from cgf_components.attack_artillery_fort_components import ArtilleryFortColorComponent, AttackArtilleryFortColorSystem, ColorComponent, ColorSystem
from cgf_components.color_blind_component import ChangeModelOnColorBlindComponent, ChangeModelOnColorBlindComponentSystem
from cgf_components.gun_audition_component import GunAuditionsSystem
from cgf_components.hangar_camera_manager import HangarCameraSystem
from cgf_components.highlight_component import HighlightComponent, HighlightSystem, IsHighlighted
from cgf_components.hover_component import HoverSystem, IsHoveredComponent, SelectionComponent, HoverGroupTrackerComponent
from cgf_components.hover_group_components import HoverGroupSystem, HoverableComponent, HoverSoundComponent
from cgf_components.marker_component import CombatMarker, CombatMarkerSystem, GFMarkersCreatorSystem, LobbyFlashMarker, LobbyFlashMarkerVisibility, LobbyMarkersSystem, LobbyMarkersVisibilitySystem
from cgf_components.on_click_components import ClickSystem, ClickVSEComponentsSystem, ClientSelectableComponentsSystem, OpenBrowserOnClickComponent
from cgf_components.on_death_components import ChangeModelOnDeathComponent, EffectOnDeathComponent, SoundOnDeathComponent
from cgf_components.on_player_in_zone_manager import OnPlayerInZoneSystem
from cgf_components.on_shot_components import EffectOnShotComponent, SoundOnShotComponent
from cgf_components.pbs_components import PostBattleBoardComponent, PostBattleSystem
from cgf_components.pm30_hangar_components import AssemblingStagesComponent, HangarOperationsComponent, HangarOperationsSystem, PersonalMissionsSelectionComponent
from cgf_components.power_mode_components import PowerModeActiveProgressLayers, PowerModeMechanicSystem, PowerModeRTPCComponent
from cgf_components.rechargeable_nitro_components import RechargeableNitroMechanicSystem, RechargeableNitroRTPCComponent
from cgf_components.rocket_acceleration_component import RocketAccelerationStateListener, RocketAccelerationSystem, RocketAccelerationTerrainEffect
from cgf_components.rtpc_component_manager import RTPCComponentSystem
from cgf_components.sequence_components import PrefabSpawnerSystem
from cgf_components.serial_number_component import SerialNumberComponent, SerialNumberComponentSystem, SerialNumberSwitcher
from cgf_components.shot_color_transmission_component import ShotColorTransmissionComponent
from cgf_components.stats_display_components import StatisticDisplayComponent, TrackedStatisticComponentSystem
from cgf_components.target_designator_manager import TargetDesignatorSoundSystem
from cgf_components.trigger_vse_component import TriggerVSEComponent, TriggerVisualScriptComponentsSystem
from cgf_components.vehicle_health_observer_manager import VehicleHealthObserverSystem
from cgf_components.visual_effect_component_manager import KillCamVisualEffectComponentSystem
from cgf_components.zone_components import MapZoneSystem, RandomEventZoneUINotification, WeatherZoneUINotification, ZoneHint, ZoneMarker
from gui.pet_system.cgf_components.pet_place_component import PetPlaceComponent, PetPrefabSystem
from vehicle_systems.components.vehicle_to_camera_alignment_components import VehicleToCameraAlignmentSystem, VehicleToCameraAlignmentComponent
from DeathComponent import DeathComponentSystem
from SequenceNetworkSync import SequenceNetworkSyncSystem
from ShotsReceiver import ShotReceiverSystem, ShotsReceiver
from VehicleStickers import VehicleStickersSystem
from vehicle_systems.components.hull_aiming_controller import HullAimingSystem, HullAimingController
from vehicle_systems.components.CrashedTracks import CrashedTracksController, CrashedTracksSystem
from vehicle_systems.components.highlighter import Highlighter
from vehicle_systems.components.vehicle_shadow_manager import VehicleShadowManager, VehicleShadowSystem
from vehicle_systems.components.siegeEffectsController import SiegeEffectsController
from vehicle_appearance.component import VehicleAppearanceComponent
from vehicle_appearance.systems import CommonTankAppearanceActivateSystem, CommonTankAppearanceUpdateSystem, CompoundAppearanceDirtUpdateSystem
if HAS_DEV_RESOURCES:
    from cgf_components.rocket_acceleration_component import RocketAccelerationSystemDebug
if IS_EDITOR or IS_CGF_DUMP:

    class HangarAppearanceSystem(object):
        Reactions = CGF.Reactions()


else:
    from gui.hangar_vehicle_appearance_system import HangarAppearanceSystem

@registerModule
class ClientCommonModule(object):
    name = 'Client Module'
    desc = 'Client Common Functionalities'
    group = 'Common'
    systems = [CGF.RegisterSystem(VehicleHealthObserverSystem, domain=CGF.Domain.Client, updateBefore=(GenericComponents.StateSwitcherSystem,)),
     CGF.RegisterSystem(TriggerVisualScriptComponentsSystem, domain=CGF.Domain.ClientEditor),
     CGF.RegisterSystem(TargetDesignatorSoundSystem, domain=CGF.Domain.Client),
     CGF.RegisterSystem(TrackedStatisticComponentSystem, domain=CGF.Domain.ClientEditor, updateAfter=(GenericComponents.DecalComponentSystem,)),
     CGF.RegisterSystem(AccuracyStacksMechanicSystem, updatePeriod=0.2, domain=CGF.Domain.ClientEditor, predicate=clientWorldsPredicate(ClientWorld.BATTLE | ClientWorld.EDITOR)),
     CGF.RegisterSystem(ArenaCameraSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem,)),
     CGF.RegisterSystem(ChangeModelOnColorBlindComponentSystem, domain=CGF.Domain.Client),
     CGF.RegisterSystem(GunAuditionsSystem, domain=CGF.Domain.ClientEditor, updateBefore=(CGF.TransformUpdateSystem,)),
     CGF.RegisterSystem(HoverGroupSystem, domain=CGF.Domain.ClientEditor, updateBefore=(CGF.TransformUpdateSystem,)),
     CGF.RegisterSystem(OnPlayerInZoneSystem, domain=CGF.Domain.Client, updateBefore=(CGF.TransformUpdateSystem,)),
     CGF.RegisterSystem(CombatMarkerSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem,), predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID)),
     CGF.RegisterSystem(GFMarkersCreatorSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem,)),
     CGF.RegisterSystem(SerialNumberComponentSystem, domain=CGF.Domain.ClientEditor, updateAfter=(GenericComponents.DecalComponentSystem,)),
     CGF.RegisterSystem(RTPCComponentSystem, domain=CGF.Domain.ClientEditor),
     CGF.RegisterSystem(ShotReceiverSystem, domain=CGF.Domain.ClientServer),
     CGF.RegisterSystem(DeathComponentSystem, domain=CGF.Domain.ClientEditor, updateAfter=(CGF.TransformUpdateSystem,)),
     CGF.RegisterSystem(SequenceNetworkSyncSystem, domain=CGF.Domain.Client, updateBefore=(GenericComponents.SequenceSystem,)),
     CGF.RegisterSystem(RocketAccelerationSystem, domain=CGF.Domain.Client, updateAfter=(GenericComponents.VseComponentSystem,), predicate=clientWorldsPredicate(ClientWorld.BATTLE)),
     CGF.RegisterSystem(MapZoneSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem,), updatePeriod=1.0, predicate=clientWorldsPredicate(ClientWorld.BATTLE | ClientWorld.EDITOR)),
     CGF.RegisterSystem(RechargeableNitroMechanicSystem, domain=CGF.Domain.Client, updatePeriod=0.2, predicate=clientWorldsPredicate(ClientWorld.BATTLE | ClientWorld.EDITOR)),
     CGF.RegisterSystem(PowerModeMechanicSystem, domain=CGF.Domain.Client, updatePeriod=0.2, predicate=clientWorldsPredicate(ClientWorld.BATTLE | ClientWorld.EDITOR)),
     CGF.RegisterSystem(PrefabSpawnerSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem,)),
     CGF.RegisterSystem(VehicleStickersSystem, domain=CGF.Domain.ClientEditor, updateAfter=(GpuDecals.GpuDecalsReceiverComponentSystem,)),
     CGF.RegisterSystem(TemperatureGunMechanicSystem, domain=CGF.Domain.Client, updatePeriod=0.2, predicate=clientWorldsPredicate(ClientWorld.BATTLE | ClientWorld.EDITOR)),
     CGF.RegisterSystem(AuditionsSystem, domain=CGF.Domain.Client),
     CGF.RegisterSystem(AcceleratorStatusTrackerComponentSystem, domain=CGF.Domain.Client, predicate=clientWorldsPredicate(ClientWorld.BATTLE), updatePeriod=0.1),
     CGF.RegisterSystem(NozzleControllerComponentSystem, domain=CGF.Domain.ClientEditor, predicate=clientWorldsPredicate(ClientWorld.BATTLE | ClientWorld.EDITOR)),
     CGF.RegisterSystem(StagedJetBoostersComponentSystem, domain=CGF.Domain.Client, predicate=clientWorldsPredicate(ClientWorld.BATTLE | ClientWorld.EDITOR)),
     CGF.RegisterSystem(DestructibleEntityStatesSystem, domain=CGF.Domain.Client, predicate=clientWorldsPredicate(ClientWorld.BATTLE)),
     CGF.RegisterSystem(DetachedTurretSystem, domain=CGF.Domain.Client, predicate=clientWorldsPredicate(ClientWorld.BATTLE), updatePeriod=SERVER_TICK_LENGTH)]
    components = [cgf_components.vehicle_mechanics_components.VehicleMechanicSimpleActivationSounds,
     cgf_components.vehicle_mechanics_components.ConcentrationModeEffects,
     cgf_components.vehicle_mechanics_components.PowerModeEffects,
     cgf_components.vehicle_mechanics_components.AccuracyStacksEffects,
     cgf_components.vehicle_mechanics_components.AccuracyStacksRTPCComponent,
     cgf_components.vehicle_mechanics_components.BattleFuryModeEffects,
     cgf_components.vehicle_mechanics_components.SupportWeaponEffects,
     cgf_components.vehicle_mechanics_components.PillboxSiegeModeSoundEffects,
     cgf_components.vehicle_mechanics_components.OverheatStacksEffects,
     cgf_components.vehicle_mechanics_components.RechargeableNitroEffects,
     cgf_components.vehicle_mechanics_components.ChargeShotEffects,
     cgf_components.vehicle_mechanics_components.TargetDesignatorEffects,
     cgf_components.vehicle_mechanics_components.StanceDanceEffects,
     cgf_components.vehicle_mechanics_components.StationaryReloadEffects,
     cgf_components.vehicle_mechanics_components.ChargeShotEffects,
     AcceleratorStatusTrackerComponent,
     TriggerVSEComponent,
     StatisticDisplayComponent,
     SelectionComponent,
     HoverGroupTrackerComponent,
     HoverableComponent,
     HoverSoundComponent,
     HighlightComponent,
     ChangeModelOnColorBlindComponent,
     SoundOnShotComponent,
     EffectOnShotComponent,
     ChangeModelOnDeathComponent,
     SoundOnDeathComponent,
     EffectOnDeathComponent,
     CombatMarker,
     OpenBrowserOnClickComponent,
     SerialNumberComponent,
     SerialNumberSwitcher,
     ShotColorTransmissionComponent,
     RocketAccelerationStateListener,
     RocketAccelerationTerrainEffect,
     RechargeableNitroRTPCComponent,
     PowerModeRTPCComponent,
     PowerModeActiveProgressLayers,
     ZoneMarker,
     WeatherZoneUINotification,
     ZoneHint,
     RandomEventZoneUINotification,
     ShotsReceiver,
     NozzleController,
     NozzleActivationSyncComponent]


@registerModule
class ClientKillCamModule(object):
    name = 'Kill Cam Client Module'
    desc = 'Client side for killcam support'
    group = 'Common'
    systems = [CGF.RegisterSystem(KillCamVisualEffectComponentSystem, domain=CGF.Domain.ClientEditor)]
    components = []


@registerModule
class ClientArmorInspectorModule(object):
    name = 'Armor Inspector Client Module'
    group = 'Armor Inspector'
    systems = [CGF.RegisterSystem(ArmorInspectorSystem, CGF.Domain.Client)]
    components = [ArmorInspectorComponent]


@registerModule
class ClientUiModule(object):
    name = 'UI Client Module'
    group = 'UI'
    systems = [CGF.RegisterSystem(ColorSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem,))]
    components = [ColorComponent]


@registerModule
class ClientAbilitiesModule(object):
    name = 'Abilities Client Module'
    group = 'Abilities'
    systems = [CGF.RegisterSystem(AttackArtilleryFortColorSystem, domain=CGF.Domain.Client)]
    components = [ArtilleryFortColorComponent]


@registerModule
class HangarSelectionModule(object):
    name = 'Hangar Selection Client Module'
    group = 'Hangar rules'
    systems = [CGF.RegisterSystem(HoverSystem, domain=CGF.Domain.Client, predicate=clientWorldsPredicate(ClientWorld.HANGAR), perTickUpdate=True, updateAfter=(CGF.TransformUpdateSystem,)), CGF.RegisterSystem(HighlightSystem, domain=CGF.Domain.Client, predicate=clientWorldsPredicate(ClientWorld.HANGAR)), CGF.RegisterSystem(ClickSystem, domain=CGF.Domain.Client, predicate=clientWorldsPredicate(ClientWorld.HANGAR))]
    components = [IsHighlighted, IsHoveredComponent]


@registerModule
class HangarCameraModule(object):
    name = 'Hangar Camera Client Module'
    group = 'Hangar rules'
    systems = [CGF.RegisterSystem(HangarCameraSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem, CameraComponents.CameraComponentSystem), predicate=clientWorldsPredicate(ClientWorld.HANGAR), perTickUpdate=True)]


@registerModule
class VehicleToCameraAlignmentModule(object):
    name = 'Vehicle To Camera Alignment Module'
    group = 'Hangar rules'
    systems = [CGF.RegisterSystem(VehicleToCameraAlignmentSystem, domain=CGF.Domain.Client, predicate=clientWorldsPredicate(ClientWorld.HANGAR), perTickUpdate=True)]
    components = [VehicleToCameraAlignmentComponent]


@registerModule
class PostBattleModule(object):
    name = 'Post Battle Client Module'
    group = 'Hangar rules'
    systems = [CGF.RegisterSystem(PostBattleSystem, domain=CGF.Domain.Client, predicate=clientWorldsPredicate(ClientWorld.HANGAR))]
    components = [PostBattleBoardComponent]


@registerModule
class HangarOperationsModule(object):
    name = 'Hangar Operations Client Module'
    group = 'Hangar rules'
    if not IS_EDITOR:
        systems = [CGF.RegisterSystem(HangarOperationsSystem, predicate=clientWorldsPredicate(ClientWorld.HANGAR), updateAfter=(CGF.TransformUpdateSystem, CameraComponents.CameraComponentSystem))]
    components = [HangarOperationsComponent, PersonalMissionsSelectionComponent, AssemblingStagesComponent]


@registerModule
class LobbyModule(object):
    name = 'Lobby Client Module'
    group = 'lobby'
    systems = [CGF.RegisterSystem(LobbyMarkersVisibilitySystem, predicate=clientWorldsPredicate(ClientWorld.HANGAR), domain=CGF.Domain.Client),
     CGF.RegisterSystem(LobbyMarkersSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem,), predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, spaceID)),
     CGF.RegisterSystem(ClientSelectableComponentsSystem, domain=CGF.Domain.Client),
     CGF.RegisterSystem(ClickVSEComponentsSystem, domain=CGF.Domain.Client, updateAfter=(GenericComponents.VseComponentSystem,))]
    components = [LobbyFlashMarkerVisibility, LobbyFlashMarker, OpenBrowserOnClickComponent]


@registerModule
class PetModule(object):
    group = 'Hangar rules'
    name = 'Pet Placement Module'
    systems = [CGF.RegisterSystem(PetPrefabSystem, predicate=clientWorldsPredicate(ClientWorld.HANGAR), domain=CGF.Domain.Client)]
    components = [PetPlaceComponent]


@registerModule
class VehicleAppearanceModule(object):
    name = 'Vehicle Appearance Module'
    group = 'Vehicle'
    systems = [CGF.RegisterSystem(CommonTankAppearanceActivateSystem, domain=CGF.Domain.ClientEditor, predicate=clientWorldsPredicate(ClientWorld.BATTLE | ClientWorld.EDITOR), updateAfter=(BigWorld.CollisionUpdateSystem, Vehicular.TerrainMatKindSensorSystem), updateBefore=(Vehicular.VehicleAuditionSystem, Vehicular.GeneralWheelsAnimatorSystem)),
     CGF.RegisterSystem(CommonTankAppearanceUpdateSystem, domain=CGF.Domain.ClientEditor, predicate=clientWorldsPredicate(ClientWorld.BATTLE | ClientWorld.EDITOR), updateAfter=(CommonTankAppearanceActivateSystem,)),
     CGF.RegisterSystem(CompoundAppearanceDirtUpdateSystem, domain=CGF.Domain.Client, predicate=clientWorldsPredicate(ClientWorld.BATTLE), updateAfter=(CommonTankAppearanceUpdateSystem,)),
     CGF.RegisterSystem(HangarAppearanceSystem, domain=CGF.Domain.Client, predicate=clientWorldsPredicate(ClientWorld.HANGAR), updateAfter=(BigWorld.CollisionUpdateSystem,)),
     CGF.RegisterSystem(CrashedTracksSystem, domain=CGF.Domain.ClientEditor, predicate=clientWorldsPredicate(ClientWorld.BATTLE | ClientWorld.EDITOR)),
     CGF.RegisterSystem(HullAimingSystem, domain=CGF.Domain.ClientEditor, predicate=clientWorldsPredicate(ClientWorld.BATTLE | ClientWorld.EDITOR)),
     CGF.RegisterSystem(VehicleShadowSystem, domain=CGF.Domain.ClientEditor),
     CGF.RegisterSystem(CustomEffectManagerSystem, domain=CGF.Domain.ClientEditor, predicate=clientWorldsPredicate(ClientWorld.BATTLE | ClientWorld.EDITOR))]
    components = [VehicleAppearanceComponent,
     CrashedTracksController,
     HullAimingController,
     Highlighter,
     VehicleShadowManager,
     SiegeEffectsController,
     CustomEffectManager]


if HAS_DEV_RESOURCES:

    @registerModule
    class RamDebugModule(object):
        name = 'Rocker Acceleration Debug Module'
        desc = 'Debug RAM in battles'
        group = 'Debug'
        systems = [CGF.RegisterSystem(RocketAccelerationSystemDebug, domain=CGF.Domain.Client, perTickUpdate=True, updatePeriod=0.3)]
        components = []
