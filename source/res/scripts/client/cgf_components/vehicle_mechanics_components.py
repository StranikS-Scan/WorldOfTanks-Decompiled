# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/vehicle_mechanics_components.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import ComponentProperty, registerComponent
_VEHICLE_MECHANICS_CATEGORY = 'Vehicle Mechanics'

@registerComponent
class VehicleMechanicSimpleActivationSounds(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    editorTitle = 'Vehicle Mechanic Simple Activation Sounds'
    domain = CGF.Domain.Client
    soundTrigger = ComponentProperty(type=CGF.PropertyType.String, editorName='Trigger sound', value='')
    soundNotReady = ComponentProperty(type=CGF.PropertyType.String, editorName='Not ready sound', value='')


@registerComponent
class ConcentrationModeEffects(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    editorTitle = 'Concentration Mode Mechanic Effects'
    domain = CGF.Domain.Client
    soundTransitionReady = ComponentProperty(type=CGF.PropertyType.String, editorName='Transition to ready state sound', value='gui_abl_concentration_ready')
    soundTransitionStart = ComponentProperty(type=CGF.PropertyType.String, editorName='Transition to active state sound', value='gui_abl_concentration_start')
    soundTransitionBrake = ComponentProperty(type=CGF.PropertyType.String, editorName='Transition to disabled state sound', value='gui_abl_concentration_brake')
    soundTransitionStop = ComponentProperty(type=CGF.PropertyType.String, editorName='Transition from active state sound', value='gui_abl_concentration_stop')
    soundObservationActiveStart = ComponentProperty(type=CGF.PropertyType.String, editorName='Observing active state start', value='gui_abl_concentration_start_loop')
    soundObservationActiveStop = ComponentProperty(type=CGF.PropertyType.String, editorName='Observing active state stop', value='gui_abl_concentration_stop_utility')
    soundStateConcentration = ComponentProperty(type=CGF.PropertyType.String, editorName='Mechanic WWISE state sync', value='STATE_ext_abl_concentration')
    soundStateConcentrationOn = ComponentProperty(type=CGF.PropertyType.String, editorName='Mechanic WWISE state on value', value='STATE_ext_abl_concentration_on')
    soundStateConcentrationOff = ComponentProperty(type=CGF.PropertyType.String, editorName='Mechanic WWISE state off value', value='STATE_ext_abl_concentration_off')


@registerComponent
class PowerModeEffects(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    editorTitle = 'Power Mode Mechanic Effects'
    domain = CGF.Domain.Client
    soundPowerModeActivation = ComponentProperty(type=CGF.PropertyType.String, editorName='Power mode activation', value='abl_power_activation')
    soundPowerModeLoop = ComponentProperty(type=CGF.PropertyType.String, editorName='Power mode loop', value='abl_power_loop')
    soundPowerModeStop = ComponentProperty(type=CGF.PropertyType.String, editorName='Power mode stop loop', value='abl_power_stop_utility')
    soundPowerModeDeactivation = ComponentProperty(type=CGF.PropertyType.String, editorName='Power mode deactivation', value='abl_power_disable')
    soundPowerModeActivationNPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Power mode activation', value='abl_power_activation_npc')
    soundPowerModeLoopNPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Power mode loop', value='abl_power_loop_npc')
    soundPowerModeStopNPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Power mode stop loop', value='abl_power_stop_npc_utility')
    soundPowerModeDeactivationNPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Power mode deactivation', value='abl_power_disable_npc')
    startNodesList = ComponentProperty(type=CGF.PropertyType.LinkList, editorName='Start Nodes', value=())
    idleNodesList = ComponentProperty(type=CGF.PropertyType.LinkList, editorName='Idle Nodes', value=())
    endNodesList = ComponentProperty(type=CGF.PropertyType.LinkList, editorName='End Nodes', value=())


@registerComponent
class AccuracyStacksEffects(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    editorTitle = 'Accuracy Stacks Mechanic Effects'
    domain = CGF.Domain.Client
    soundGainStack = ComponentProperty(type=CGF.PropertyType.String, editorName='Gain stack sound', value='gui_abl_stab_stack_gain')
    soundStacksLimitReached = ComponentProperty(type=CGF.PropertyType.String, editorName='Stacks limit reached sound', value='gui_abl_stab_stack_limit_reached')
    soundWarningNotification = ComponentProperty(type=CGF.PropertyType.String, editorName='Warning notification sound', value='gui_abl_stab_stack_warning')
    soundGainStacksStart = ComponentProperty(type=CGF.PropertyType.String, editorName='Start gaining stacks sound', value='gui_abl_stab_stack_progress')
    soundGainStacksStop = ComponentProperty(type=CGF.PropertyType.String, editorName='Stop gaining stacks sound', value='gui_abl_stab_stack_progress_stop')
    soundGainStacksPause = ComponentProperty(type=CGF.PropertyType.String, editorName='Pause gaining stacks sound', value='gui_abl_stab_stack_pause')
    soundGainStacksResume = ComponentProperty(type=CGF.PropertyType.String, editorName='Resume gaining stacks sound', value='gui_abl_stab_stack_resume')


@registerComponent
class AccuracyStacksRTPCComponent(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    editorTitle = 'Accuracy stacks gaining RTPC'
    domain = CGF.Domain.Client
    RTPCName = ComponentProperty(type=CGF.PropertyType.String, value='RTPC_ext_abl_stab_stack_progress', editorName='RTPC name')

    def __init__(self):
        super(AccuracyStacksRTPCComponent, self).__init__()
        self.controllerGO = None
        self.progress = -1.0
        return


@registerComponent
class BattleFuryModeEffects(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    editorTitle = 'Battle Fury Mechanic Effects'
    domain = CGF.Domain.Client
    soundGainStack = ComponentProperty(type=CGF.PropertyType.String, editorName='Gain stack sound', value='gui_abl_stack_gain')
    soundStacksLimitReached = ComponentProperty(type=CGF.PropertyType.String, editorName='Stacks limit reached sound', value='gui_abl_stack_limit_reached')
    soundDropStack = ComponentProperty(type=CGF.PropertyType.String, editorName='Drop stack sound', value='gui_abl_stack_drop')
    soundRefreshStack = ComponentProperty(type=CGF.PropertyType.String, editorName='Refresh stack sound', value='gui_abl_stack_refresh')


@registerComponent
class SupportWeaponEffects(object):
    category = 'Vehicle Mechanics'
    editorTitle = 'Support Weapon Mechanic Effects'
    domain = CGF.Domain.Client
    delayedReloadMinTime = ComponentProperty(type=CGF.PropertyType.Float, editorName='Min time for delayed reload', value=0.0)
    delayedReloadMaxTime = ComponentProperty(type=CGF.PropertyType.Float, editorName='Max time for delayed reload', value=3.0)
    soundDelayedReload = ComponentProperty(type=CGF.PropertyType.String, editorName='Delayed sound for reload finishing', value='gui_abl_saw_reload')
    soundDelayedReloadCancel = ComponentProperty(type=CGF.PropertyType.String, editorName='Finishing reload sound cancellation', value='gui_abl_saw_reload_stop')
    soundTransitionReady = ComponentProperty(type=CGF.PropertyType.String, editorName='Transition to ready state sound', value='gui_abl_saw_ready')
    soundTransitionStart = ComponentProperty(type=CGF.PropertyType.String, editorName='Transition to active state sound', value='gui_abl_saw_start')
    soundTransitionBreak = ComponentProperty(type=CGF.PropertyType.String, editorName='Transition to disabled state sound', value='gui_abl_saw_break')
    soundTransitionStop = ComponentProperty(type=CGF.PropertyType.String, editorName='Transition from active state sound', value='gui_abl_saw_stop')
    soundGeneralUtilityStop = ComponentProperty(type=CGF.PropertyType.String, editorName='Mechanic sounds finalization', value='gui_abl_saw_stop_utility')


@registerComponent
class PillboxSiegeModeSoundEffects(object):
    category = 'Vehicle Mechanics'
    editorTitle = 'Pillbox Siege Mode Sound Effects'
    domain = CGF.Domain.Client
    longpressActivation = ComponentProperty(type=CGF.PropertyType.String, editorName='Long press activation 2D', value='gui_abl_pillbox_activation_longpress')
    longpressDeactivation = ComponentProperty(type=CGF.PropertyType.String, editorName='Long press deactivation 2D', value='gui_abl_pillbox_deactivation_longpress')
    longpressError = ComponentProperty(type=CGF.PropertyType.String, editorName='Long press unavailable 2D', value='gui_abl_button_not_ready')
    abilityActivationStart = ComponentProperty(CGF.PropertyType.String, editorName='Ability activation start 2D', value='gui_abl_pillbox_activation_phase_start')
    abilityActivationStartEngine = ComponentProperty(CGF.PropertyType.String, editorName='Ability activation start Engine', value='gp_abl_pillbox_engine_activation_phase_start')
    abilityActivationStop = ComponentProperty(CGF.PropertyType.String, editorName='Ability activation stop 2D', value='gui_abl_pillbox_activation_phase_stop ')
    abilityActivationStopEngine = ComponentProperty(CGF.PropertyType.String, editorName='Ability activation stop Engine', value='gp_abl_pillbox_engine_activation_phase_stop')
    abilityDeactivationStart = ComponentProperty(CGF.PropertyType.String, editorName='Ability deactivation start 2D', value='gui_abl_pillbox_deactivation_phase_start')
    abilityDeactivationStartEngine = ComponentProperty(CGF.PropertyType.String, editorName='Ability deactivation start Engine', value='gp_abl_pillbox_engine_deactivation_phase_start')
    abilityDeactivationStop = ComponentProperty(CGF.PropertyType.String, editorName='Ability deactivation stop 2D', value='gui_abl_pillbox_deactivation_phase_stop')
    abilityDeactivationStopEngine = ComponentProperty(CGF.PropertyType.String, editorName='Ability deactivation stop Engine', value='gp_abl_pillbox_engine_deactivation_phase_stop')
    engineStateGroup = ComponentProperty(CGF.PropertyType.String, editorName='Engine state group', value='STATE_ext_abl_pillbox_engine_damage')
    engineDamageOn = ComponentProperty(CGF.PropertyType.String, editorName='Engine damage on', value='STATE_ext_abl_pillbox_engine_damage_on')
    engineDamageOff = ComponentProperty(CGF.PropertyType.String, editorName='Engine damage off', value='STATE_ext_abl_pillbox_engine_damage_off')


@registerComponent
class OverheatStacksEffects(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    editorTitle = 'Overheat Stacks mechanic effects'
    domain = CGF.Domain.Client
    soundDelayTimerUp = ComponentProperty(type=CGF.PropertyType.String, editorName='Delay Timer boot up sound', value='gui_abl_charge_delay_up')
    soundDelayTimerDown = ComponentProperty(type=CGF.PropertyType.String, editorName='Drop Delay shut down sound', value='gui_abl_charge_delay_down')
    eventChargingOn = ComponentProperty(type=CGF.PropertyType.String, editorName='Start/continue charging event', value='gui_abl_charge_start')
    eventChargingOff = ComponentProperty(type=CGF.PropertyType.String, editorName='Stop/pause charging event', value='gui_abl_charge_stop')
    eventChargingSilentInterrupt = ComponentProperty(type=CGF.PropertyType.String, editorName='Stop/pause charging silently', value='gui_abl_charge_stop_utility')
    RTPCChargingProcess = ComponentProperty(type=CGF.PropertyType.String, editorName='Charging process rtpc', value='RTPC_ext_abl_charge_progress')
    soundChargeMax = ComponentProperty(type=CGF.PropertyType.String, editorName='Charge Max sound', value='gui_abl_charge_max')


@registerComponent
class RechargeableNitroEffects(object):
    category = 'Vehicle Mechanics'
    editorTitle = 'Rechargeable Nitro Effects'
    domain = CGF.Domain.Client
    idle = ComponentProperty(type=CGF.PropertyType.Link, editorName='Idle Object', value=CGF.GameObject)
    start = ComponentProperty(type=CGF.PropertyType.Link, editorName='Start Object', value=CGF.GameObject)
    end = ComponentProperty(type=CGF.PropertyType.Link, editorName='Stop Object', value=CGF.GameObject)
    endSwitch = ComponentProperty(type=CGF.PropertyType.Link, editorName='Stop switch Object', value=CGF.GameObject)
    startFail = ComponentProperty(type=CGF.PropertyType.Link, editorName='Start fail Object', value=CGF.GameObject)
    nearEnd = ComponentProperty(type=CGF.PropertyType.Link, editorName='Near end Object', value=CGF.GameObject)
    soundNodes = ComponentProperty(type=CGF.PropertyType.LinkList, editorName='Sound nodes', value=())
    rtpcHolder = ComponentProperty(type=CGF.PropertyType.Link, editorName='RTPC component holder', value=CGF.GameObject)
    soundActivePC = ComponentProperty(type=CGF.PropertyType.String, editorName='Active PC sound', value='gp_abl_nitro_start_PC')
    soundStopPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Stop PC sound', value='gp_abl_nitro_stop_PC')
    soundActiveNPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Active NPC sound', value='gp_abl_nitro_start_NPC')
    soundStopNPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Stop NPC sound', value='gp_abl_nitro_stop_NPC')
    soundReady = ComponentProperty(type=CGF.PropertyType.String, editorName='Ready sound', value='gui_abl_nitro_ready')
    soundDisable = ComponentProperty(type=CGF.PropertyType.String, editorName='Disable sound', value='gui_abl_nitro_disable')
    soundDelayEnded = ComponentProperty(type=CGF.PropertyType.String, editorName='Delay ended sound', value='gui_abl_nitro_delay_end')
    soundExhausted = ComponentProperty(type=CGF.PropertyType.String, editorName='Charge exhausted sound', value='gui_abl_nitro_overheat')
    eventRTPCStart = ComponentProperty(type=CGF.PropertyType.String, editorName='RTPC start event', value='gui_abl_nitro_start_utility')
    eventRTPCStop = ComponentProperty(type=CGF.PropertyType.String, editorName='RTPC stop event', value='gui_abl_nitro_stop_utility')


@registerComponent
class ChargeShotEffects(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    editorTitle = 'Charge Shot Mechanic Effects'
    domain = CGF.Domain.Client
    soundActivation = ComponentProperty(type=CGF.PropertyType.String, editorName='Activation sound', value='gui_abl_button_trigger')
    soundActivationDisabled = ComponentProperty(type=CGF.PropertyType.String, editorName='Disabled activation sound', value='gui_abl_button_not_ready')
    soundChargeStart = ComponentProperty(type=CGF.PropertyType.String, editorName='Charge start sound', value='gui_abl_charged_shot_start')
    soundChargeLevel1 = ComponentProperty(type=CGF.PropertyType.String, editorName='Charge level 1 sound', value='gui_abl_charged_shot_reach_level_01')
    soundChargeLevel2 = ComponentProperty(type=CGF.PropertyType.String, editorName='Charge level 2 sound', value='gui_abl_charged_shot_reach_level_02')
    soundChargeLevelMax = ComponentProperty(type=CGF.PropertyType.String, editorName='Charge level Max sound', value='gui_abl_charged_shot_reach_level_03')
    soundShootLevel0 = ComponentProperty(type=CGF.PropertyType.String, editorName='Shoot level 0 sound', value='gui_abl_charged_shot_fire_level_00')
    soundShootLevel1 = ComponentProperty(type=CGF.PropertyType.String, editorName='Shoot level 1 sound', value='gui_abl_charged_shot_fire_level_01')
    soundShootLevel2 = ComponentProperty(type=CGF.PropertyType.String, editorName='Shoot level 2 sound', value='gui_abl_charged_shot_fire_level_02')
    soundShootLevelMax = ComponentProperty(type=CGF.PropertyType.String, editorName='Shoot level Max sound', value='gui_abl_charged_shot_fire_level_03')
    soundOverheat = ComponentProperty(type=CGF.PropertyType.String, editorName='Overheat sound', value='gui_abl_charged_shot_overheat')
    soundMechanicStop = ComponentProperty(type=CGF.PropertyType.String, editorName='Mechanic stop sound', value='gui_abl_charged_shot_stop_utility')


@registerComponent
class TargetDesignatorEffects(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    editorTitle = 'Target Designator Mechanic Effects'
    domain = CGF.Domain.Client
    soundReadyState = ComponentProperty(type=CGF.PropertyType.String, editorName='Ready state sound', value='gui_abl_tda_ready')
    soundActiveState = ComponentProperty(type=CGF.PropertyType.String, editorName='Active state sound', value='gui_abl_tda_start')
    soundCooldownState = ComponentProperty(type=CGF.PropertyType.String, editorName='Cooldown state sound', value='gui_abl_tda_stop')
    soundActivation = ComponentProperty(type=CGF.PropertyType.String, editorName='Activation button sound', value='gui_abl_button_trigger')
    soundActivationDisabled = ComponentProperty(type=CGF.PropertyType.String, editorName='Disabled activation sound', value='gui_abl_button_not_ready')
    soundMechanicStop = ComponentProperty(type=CGF.PropertyType.String, editorName='Mechanic stop sound', value='gui_abl_tda_stop_utility')


@registerComponent
class StanceDanceEffects(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    editorTitle = 'Stance Dance Mechanic Effects'
    domain = CGF.Domain.Client
    sound3DTurboActivatedPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Turbo activate 3D sound (PC)', value='gp_abl_stance_turbo_active_on_pc')
    sound3DTurboDeactivatedPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Turbo deactivate 3D sound (PC)', value='gp_abl_stance_turbo_active_off_pc')
    sound3DTurboActivatedNPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Turbo activate 3D sound (NPC)', value='gp_abl_stance_turbo_active_on_npc')
    sound3DTurboDeactivatedNPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Turbo deactivate 3D sound (NPC)', value='gp_abl_stance_turbo_active_off_npc')
    soundTurboFullEnergy = ComponentProperty(type=CGF.PropertyType.String, editorName='Turbo full energy sound', value='gui_abl_stance_turbo_full')
    soundFightFullEnergy = ComponentProperty(type=CGF.PropertyType.String, editorName='Fight full energy sound', value='gui_abl_stance_shooting_full')
    soundTurboModeOn = ComponentProperty(type=CGF.PropertyType.String, editorName='Turbo mode on sound', value='gui_abl_stance_turbo_on_pc')
    soundFightModeOn = ComponentProperty(type=CGF.PropertyType.String, editorName='Fight mode on sound', value='gui_abl_stance_shooting_on_pc')
    soundFightActivated = ComponentProperty(type=CGF.PropertyType.String, editorName='Fight activate sound', value='gui_abl_stance_shooting_active_on_pc')
    soundFightDeactivated = ComponentProperty(type=CGF.PropertyType.String, editorName='Fight deactivate sound', value='gui_abl_stance_shooting_active_off_pc')
    soundMechanicStopPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Mechanic stop sound (PC)', value='abl_stance_stop_utility')
    soundMechanicStopNPC = ComponentProperty(type=CGF.PropertyType.String, editorName='Mechanic stop sound (NPC)', value='abl_stance_stop_npc_utility')
    soundActivation = ComponentProperty(type=CGF.PropertyType.String, editorName='Activation sound', value='gui_abl_button_trigger')
    soundActivationDisabled = ComponentProperty(type=CGF.PropertyType.String, editorName='Disabled activation sound', value='gui_abl_button_not_ready')
    soundSwitch = ComponentProperty(type=CGF.PropertyType.String, editorName='Switch sound', value='gui_abl_stance_mode_switch')


@registerComponent
class StationaryReloadEffects(object):
    category = 'Vehicle Mechanics'
    editorTitle = 'Stationary Reload Mechanic Effects'
    domain = CGF.Domain.Client
    soundTurretMoveStart = ComponentProperty(type=CGF.PropertyType.String, editorName='Turret starts moving sound', value='gui_abl_podrld_turret_start')
    soundTurretMoveEnd = ComponentProperty(type=CGF.PropertyType.String, editorName='Turret at load point sound', value='gui_abl_podrld_turret_loadpoint')
    soundTurretLoadStop = ComponentProperty(type=CGF.PropertyType.String, editorName='Turret load stop sound', value='gui_abl_podrld_turret_loadstop')
    soundTurretStopUtility = ComponentProperty(type=CGF.PropertyType.String, editorName='Turret stop utility sound', value='gui_abl_podrld_turret_stop_utility')
    soundTurretBrake = ComponentProperty(type=CGF.PropertyType.String, editorName='Turret break brake sound', value='gp_abl_podrld_pods_brake')
    soundDelayStart = ComponentProperty(type=CGF.PropertyType.String, editorName='Delay start sound', value='gui_abl_podrld_turret_delay_start')
    soundDelayStop = ComponentProperty(type=CGF.PropertyType.String, editorName='Delay stop sound', value='gui_abl_podrld_turret_delay_stop')


@registerComponent
class OverheatGunEffects(object):
    category = 'OverheatGun'
    editorTitle = 'Overheat Gun Effects'
    domain = CGF.Domain.Client
    soundHeating = ComponentProperty(type=CGF.PropertyType.String, editorName='Gun heating start sound', value='gui_abl_overheat_gun_heating')
    soundCooling = ComponentProperty(type=CGF.PropertyType.String, editorName='Gun colling start sound', value='gui_abl_overheat_gun_cooling')
    soundIdle = ComponentProperty(type=CGF.PropertyType.String, editorName='Gun colling stop sound', value='gui_abl_overheat_gun_cooling_stop')
    soundUtilityStop = ComponentProperty(type=CGF.PropertyType.String, editorName='Utility stop', value='gui_abl_overheat_gun_utility_stop')
    soundOverheatWarning = ComponentProperty(type=CGF.PropertyType.String, editorName='Overheat warning sound', value='gui_abl_overheat_gun_block_on_pre')
    soundOverheated = ComponentProperty(type=CGF.PropertyType.String, editorName='Overheat occurs sound', value='gui_abl_overheat_gun_block_on')
    soundPreCooled = ComponentProperty(type=CGF.PropertyType.String, editorName='Overheat near end sound', value='gui_abl_overheat_gun_block_off_pre')
    soundCooled = ComponentProperty(type=CGF.PropertyType.String, editorName='Overheat ended sound', value='gui_abl_overheat_gun_block_off')


@registerComponent
class HeatingZonesGunEffects(object):
    category = 'HeatingZonesGun'
    editorTitle = 'Heating Zones Gun State Effects'
    domain = CGF.Domain.Client
    soundHeatingOn = ComponentProperty(type=CGF.PropertyType.String, editorName='Heating start sound', value='gui_abl_gun_heating_on')
    soundHeatingOff = ComponentProperty(type=CGF.PropertyType.String, editorName='Heating stop sound', value='gui_abl_gun_heating_off')
    soundHeatingDropMarker = ComponentProperty(type=CGF.PropertyType.String, editorName='Heating marker drop sound', value='gui_abl_gun_heating_marker')
    soundHeatingIdleMarker = ComponentProperty(type=CGF.PropertyType.String, editorName='Heating marker idle sound', value='gui_abl_gun_heating_marker_last_aim')
    soundUtilityStop = ComponentProperty(type=CGF.PropertyType.String, editorName='Heating utility stop', value='gui_abl_gun_heating_stop_utility')


@registerComponent
class PropellantGunEffects(object):
    category = 'PropellantGun'
    editorTitle = 'Propellant Gun Effects'
    domain = CGF.Domain.Client
    soundActivationDisabled = ComponentProperty(type=CGF.PropertyType.String, editorName='Disabled activation sound', value='gui_abl_button_not_ready')
    soundChargeMin = ComponentProperty(type=CGF.PropertyType.String, editorName='Normal charge mode was set', value='gui_abl_afterburner_set_min')
    soundChargeMax = ComponentProperty(type=CGF.PropertyType.String, editorName='Overcharge mode was set', value='gui_abl_afterburner_set_max')
    soundPreCharge = ComponentProperty(type=CGF.PropertyType.String, editorName='Precharging sound', value='gui_abl_afterburner_pre_min')
    soundPreOvercharge = ComponentProperty(type=CGF.PropertyType.String, editorName='Preovercharging sound', value='gui_abl_afterburner_pre_max')
    soundReachCharge = ComponentProperty(type=CGF.PropertyType.String, editorName='Charge reach sound', value='gui_abl_afterburner_reach_min')
    soundReachOvercharge = ComponentProperty(type=CGF.PropertyType.String, editorName='Overcharge reach sound', value='gui_abl_afterburner_reach_max')
    soundStartOvercharge = ComponentProperty(type=CGF.PropertyType.String, editorName='Start overcharging  sound', value='gui_abl_afterburner_exceed_min')
    soundShotFromMinCharge = ComponentProperty(type=CGF.PropertyType.String, editorName='Shot from normal charge limit', value='gui_abl_afterburner_min_shot')
    soundShotExitOvercharge = ComponentProperty(type=CGF.PropertyType.String, editorName='Shot in overcharge range', value='gui_abl_afterburner_max_shot')
    soundShotNocharge = ComponentProperty(type=CGF.PropertyType.String, editorName='Shot under charge limit', value='gui_abl_afterburner_nocharge_shot')
    soundDropOvercharge = ComponentProperty(type=CGF.PropertyType.String, editorName='Drop overcharge', value='gui_abl_afterburner_drop_max_switch')
    soundUtilityStop = ComponentProperty(type=CGF.PropertyType.String, editorName='Propellant utility stop', value='gui_abl_afterburner_stop_utility')
