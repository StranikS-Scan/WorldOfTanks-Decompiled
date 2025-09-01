# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/vehicle_mechanics_components.py
import CGF
from cgf_script.component_meta_class import CGFMetaTypes, ComponentProperty, registerComponent
_VEHICLE_MECHANICS_CATEGORY = 'Vehicle Mechanics'

@registerComponent
class VehicleMechanicSimpleActivationSounds(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'Vehicle Mechanic Simple Activation Sounds'
    soundTrigger = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Trigger sound', value='')
    soundNotReady = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Not ready sound', value='')


@registerComponent
class ConcentrationModeEffects(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'Concentration Mode Mechanic Effects'
    soundTransitionReady = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Transition to ready state sound', value='gui_abl_concentration_ready')
    soundTransitionStart = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Transition to active state sound', value='gui_abl_concentration_start')
    soundTransitionBrake = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Transition to disabled state sound', value='gui_abl_concentration_brake')
    soundTransitionStop = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Transition from active state sound', value='gui_abl_concentration_stop')
    soundObservationActiveStart = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Observing active state start', value='gui_abl_concentration_start_loop')
    soundObservationActiveStop = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Observing active state stop', value='gui_abl_concentration_stop_utility')
    soundStateConcentration = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Mechanic WWISE state sync', value='STATE_ext_abl_concentration')
    soundStateConcentrationOn = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Mechanic WWISE state on value', value='STATE_ext_abl_concentration_on')
    soundStateConcentrationOff = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Mechanic WWISE state off value', value='STATE_ext_abl_concentration_off')


@registerComponent
class PowerModeEffects(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'Power Mode Mechanic Effects'
    soundPowerModeActivation = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Power mode activation', value='abl_power_activation')
    soundPowerModeLoop = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Power mode loop', value='abl_power_loop')
    soundPowerModeStop = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Power mode stop loop', value='abl_power_stop_utility')
    soundPowerModeDeactivation = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Power mode deactivation', value='abl_power_disable')
    soundPowerModeActivationNPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Power mode activation', value='abl_power_activation_npc')
    soundPowerModeLoopNPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Power mode loop', value='abl_power_loop_npc')
    soundPowerModeStopNPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Power mode stop loop', value='abl_power_stop_npc_utility')
    soundPowerModeDeactivationNPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Power mode deactivation', value='abl_power_disable_npc')
    startNodesList = ComponentProperty(type=CGFMetaTypes.OBJECT_LINK_LIST, editorName='Start Nodes', value=())
    idleNodesList = ComponentProperty(type=CGFMetaTypes.OBJECT_LINK_LIST, editorName='Idle Nodes', value=())
    endNodesList = ComponentProperty(type=CGFMetaTypes.OBJECT_LINK_LIST, editorName='End Nodes', value=())


@registerComponent
class AccuracyStacksEffects(object):
    editorTitle = 'Accuracy Stacks Mechanic Effects'
    category = _VEHICLE_MECHANICS_CATEGORY
    domain = CGF.DomainOption.DomainClient
    soundGainStack = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Gain stack sound', value='gui_abl_stab_stack_gain')
    soundStacksLimitReached = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Stacks limit reached sound', value='gui_abl_stab_stack_limit_reached')
    soundWarningNotification = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Warning notification sound', value='gui_abl_stab_stack_warning')
    soundGainStacksStart = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Start gaining stacks sound', value='gui_abl_stab_stack_progress')
    soundGainStacksStop = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Stop gaining stacks sound', value='gui_abl_stab_stack_progress_stop')
    soundGainStacksPause = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Pause gaining stacks sound', value='gui_abl_stab_stack_pause')
    soundGainStacksResume = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Resume gaining stacks sound', value='gui_abl_stab_stack_resume')


@registerComponent
class AccuracyStacksRTPCComponent(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'Accuracy stacks gaining RTPC'
    RTPCName = ComponentProperty(type=CGFMetaTypes.STRING, value='RTPC_ext_abl_stab_stack_progress', editorName='RTPC name')

    def __init__(self):
        super(AccuracyStacksRTPCComponent, self).__init__()
        self.controllerGO = None
        self.progress = -1.0
        return


@registerComponent
class BattleFuryModeEffects(object):
    category = _VEHICLE_MECHANICS_CATEGORY
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'Battle Fury Mechanic Effects'
    soundGainStack = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Gain stack sound', value='gui_abl_stack_gain')
    soundStacksLimitReached = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Stacks limit reached sound', value='gui_abl_stack_limit_reached')
    soundDropStack = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Drop stack sound', value='gui_abl_stack_drop')
    soundRefreshStack = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Refresh stack sound', value='gui_abl_stack_refresh')


@registerComponent
class SupportWeaponEffects(object):
    editorTitle = 'Support Weapon Mechanic Effects'
    category = 'Vehicle Mechanics'
    domain = CGF.DomainOption.DomainClient
    delayedReloadMinTime = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Min time for delayed reload', value=0.0)
    delayedReloadMaxTime = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Max time for delayed reload', value=3.0)
    soundDelayedReload = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Delayed sound for reload finishing', value='gui_abl_saw_reload')
    soundDelayedReloadCancel = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Finishing reload sound cancellation', value='gui_abl_saw_reload_stop')
    soundTransitionReady = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Transition to ready state sound', value='gui_abl_saw_ready')
    soundTransitionStart = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Transition to active state sound', value='gui_abl_saw_start')
    soundTransitionBreak = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Transition to disabled state sound', value='gui_abl_saw_break')
    soundTransitionStop = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Transition from active state sound', value='gui_abl_saw_stop')
    soundGeneralUtilityStop = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Mechanic sounds finalization', value='gui_abl_saw_stop_utility')


@registerComponent
class PillboxSiegeModeSoundEffects(object):
    editorTitle = 'Pillbox Siege Mode Sound Effects'
    category = 'Vehicle Mechanics'
    domain = CGF.DomainOption.DomainClient
    longpressActivation = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Long press activation 2D', value='gui_abl_pillbox_activation_longpress')
    longpressDeactivation = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Long press deactivation 2D', value='gui_abl_pillbox_deactivation_longpress')
    longpressError = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Long press unavailable 2D', value='gui_abl_button_not_ready')
    abilityActivationStart = ComponentProperty(CGFMetaTypes.STRING, editorName='Ability activation start 2D', value='gui_abl_pillbox_activation_phase_start')
    abilityActivationStartEngine = ComponentProperty(CGFMetaTypes.STRING, editorName='Ability activation start Engine', value='gp_abl_pillbox_engine_activation_phase_start')
    abilityActivationStop = ComponentProperty(CGFMetaTypes.STRING, editorName='Ability activation stop 2D', value='gui_abl_pillbox_activation_phase_stop ')
    abilityActivationStopEngine = ComponentProperty(CGFMetaTypes.STRING, editorName='Ability activation stop Engine', value='gp_abl_pillbox_engine_activation_phase_stop')
    abilityDeactivationStart = ComponentProperty(CGFMetaTypes.STRING, editorName='Ability deactivation start 2D', value='gui_abl_pillbox_deactivation_phase_start')
    abilityDeactivationStartEngine = ComponentProperty(CGFMetaTypes.STRING, editorName='Ability deactivation start Engine', value='gp_abl_pillbox_engine_deactivation_phase_start')
    abilityDeactivationStop = ComponentProperty(CGFMetaTypes.STRING, editorName='Ability deactivation stop 2D', value='gui_abl_pillbox_deactivation_phase_stop')
    abilityDeactivationStopEngine = ComponentProperty(CGFMetaTypes.STRING, editorName='Ability deactivation stop Engine', value='gp_abl_pillbox_engine_deactivation_phase_stop')
    engineStateGroup = ComponentProperty(CGFMetaTypes.STRING, editorName='Engine state group', value='STATE_ext_abl_pillbox_engine_damage')
    engineDamageOn = ComponentProperty(CGFMetaTypes.STRING, editorName='Engine damage on', value='STATE_ext_abl_pillbox_engine_damage_on')
    engineDamageOff = ComponentProperty(CGFMetaTypes.STRING, editorName='Engine damage off', value='STATE_ext_abl_pillbox_engine_damage_off')


@registerComponent
class OverheatStacksEffects(object):
    editorTitle = 'Overheat Stacks mechanic effects'
    category = _VEHICLE_MECHANICS_CATEGORY
    domain = CGF.DomainOption.DomainClient
    soundDelayTimerUp = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Delay Timer boot up sound', value='gui_abl_charge_delay_up')
    soundDelayTimerDown = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Drop Delay shut down sound', value='gui_abl_charge_delay_down')
    eventChargingOn = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Start/continue charging event', value='gui_abl_charge_start')
    eventChargingOff = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Stop/pause charging event', value='gui_abl_charge_stop')
    eventChargingSilentInterrupt = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Stop/pause charging silently', value='gui_abl_charge_stop_utility')
    RTPCChargingProcess = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Charging process rtpc', value='RTPC_ext_abl_charge_progress')
    soundChargeMax = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Charge Max sound', value='gui_abl_charge_max')


@registerComponent
class RechargeableNitroEffects(object):
    editorTitle = 'Rechargeable Nitro Effects'
    category = 'Vehicle Mechanics'
    domain = CGF.DomainOption.DomainClient
    idle = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Idle Object', value=CGF.GameObject)
    start = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Start Object', value=CGF.GameObject)
    end = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Stop Object', value=CGF.GameObject)
    endSwitch = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Stop switch Object', value=CGF.GameObject)
    startFail = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Start fail Object', value=CGF.GameObject)
    nearEnd = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Near end Object', value=CGF.GameObject)
    soundNodes = ComponentProperty(type=CGFMetaTypes.OBJECT_LINK_LIST, editorName='Sound nodes', value=())
    rtpcHolder = ComponentProperty(type=CGFMetaTypes.LINK, editorName='RTPC component holder', value=CGF.GameObject)
    soundActivePC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Active PC sound', value='gp_abl_nitro_start_PC')
    soundStopPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Stop PC sound', value='gp_abl_nitro_stop_PC')
    soundActiveNPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Active NPC sound', value='gp_abl_nitro_start_NPC')
    soundStopNPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Stop NPC sound', value='gp_abl_nitro_stop_NPC')
    soundReady = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Ready sound', value='gui_abl_nitro_ready')
    soundDisable = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Disable sound', value='gui_abl_nitro_disable')
    soundDelayEnded = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Delay ended sound', value='gui_abl_nitro_delay_end')
    soundExhausted = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Charge exhausted sound', value='gui_abl_nitro_overheat')
    eventRTPCStart = ComponentProperty(type=CGFMetaTypes.STRING, editorName='RTPC start event', value='gui_abl_nitro_start_utility')
    eventRTPCStop = ComponentProperty(type=CGFMetaTypes.STRING, editorName='RTPC stop event', value='gui_abl_nitro_stop_utility')


@registerComponent
class ChargeShotEffects(object):
    editorTitle = 'Charge Shot Mechanic Effects'
    category = _VEHICLE_MECHANICS_CATEGORY
    domain = CGF.DomainOption.DomainClient
    soundActivation = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Activation sound', value='gui_abl_button_trigger')
    soundActivationDisabled = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Disabled activation sound', value='gui_abl_button_not_ready')
    soundChargeStart = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Charge start sound', value='gui_abl_charged_shot_start')
    soundChargeLevel1 = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Charge level 1 sound', value='gui_abl_charged_shot_reach_level_01')
    soundChargeLevel2 = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Charge level 2 sound', value='gui_abl_charged_shot_reach_level_02')
    soundChargeLevelMax = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Charge level Max sound', value='gui_abl_charged_shot_reach_level_03')
    soundShootLevel0 = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Shoot level 0 sound', value='gui_abl_charged_shot_fire_level_00')
    soundShootLevel1 = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Shoot level 1 sound', value='gui_abl_charged_shot_fire_level_01')
    soundShootLevel2 = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Shoot level 2 sound', value='gui_abl_charged_shot_fire_level_02')
    soundShootLevelMax = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Shoot level Max sound', value='gui_abl_charged_shot_fire_level_03')
    soundOverheat = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Overheat sound', value='gui_abl_charged_shot_overheat')
    soundMechanicStop = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Mechanic stop sound', value='gui_abl_charged_shot_stop_utility')


@registerComponent
class TargetDesignatorEffects(object):
    editorTitle = 'Target Designator Mechanic Effects'
    category = _VEHICLE_MECHANICS_CATEGORY
    domain = CGF.DomainOption.DomainClient
    soundReadyState = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Ready state sound', value='gui_abl_tda_ready')
    soundActiveState = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Active state sound', value='gui_abl_tda_start')
    soundCooldownState = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Cooldown state sound', value='gui_abl_tda_stop')
    soundActivation = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Activation button sound', value='gui_abl_button_trigger')
    soundActivationDisabled = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Disabled activation sound', value='gui_abl_button_not_ready')
    soundMechanicStop = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Mechanic stop sound', value='gui_abl_tda_stop_utility')


@registerComponent
class StanceDanceEffects(object):
    editorTitle = 'Stance Dance Mechanic Effects'
    category = _VEHICLE_MECHANICS_CATEGORY
    domain = CGF.DomainOption.DomainClient
    sound3DTurboActivatedPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Turbo activate 3D sound (PC)', value='gp_abl_stance_turbo_active_on_pc')
    sound3DTurboDeactivatedPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Turbo deactivate 3D sound (PC)', value='gp_abl_stance_turbo_active_off_pc')
    sound3DTurboActivatedNPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Turbo activate 3D sound (NPC)', value='gp_abl_stance_turbo_active_on_npc')
    sound3DTurboDeactivatedNPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Turbo deactivate 3D sound (NPC)', value='gp_abl_stance_turbo_active_off_npc')
    soundTurboFullEnergy = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Turbo full energy sound', value='gui_abl_stance_turbo_full')
    soundFightFullEnergy = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Fight full energy sound', value='gui_abl_stance_shooting_full')
    soundTurboModeOn = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Turbo mode on sound', value='gui_abl_stance_turbo_on_pc')
    soundFightModeOn = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Fight mode on sound', value='gui_abl_stance_shooting_on_pc')
    soundFightActivated = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Fight activate sound', value='gui_abl_stance_shooting_active_on_pc')
    soundFightDeactivated = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Fight deactivate sound', value='gui_abl_stance_shooting_active_off_pc')
    soundMechanicStopPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Mechanic stop sound (PC)', value='abl_stance_stop_utility')
    soundMechanicStopNPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Mechanic stop sound (NPC)', value='abl_stance_stop_npc_utility')
    soundActivation = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Activation sound', value='gui_abl_button_trigger')
    soundActivationDisabled = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Disabled activation sound', value='gui_abl_button_not_ready')
    soundSwitch = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Switch sound', value='gui_abl_stance_mode_switch')


@registerComponent
class StationaryReloadEffects(object):
    editorTitle = 'Stationary Reload Mechanic Effects'
    category = 'Vehicle Mechanics'
    domain = CGF.DomainOption.DomainClient
    soundTurretMoveStart = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Turret starts moving sound', value='gui_abl_podrld_turret_start')
    soundTurretMoveEnd = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Turret at load point sound', value='gui_abl_podrld_turret_loadpoint')
    soundTurretLoadStop = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Turret load stop sound', value='gui_abl_podrld_turret_loadstop')
    soundTurretStopUtility = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Turret stop utility sound', value='gui_abl_podrld_turret_stop_utility')
    soundTurretBrake = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Turret break brake sound', value='gp_abl_podrld_pods_brake')
    soundDelayStart = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Delay start sound', value='gui_abl_podrld_turret_delay_start')
    soundDelayStop = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Delay stop sound', value='gui_abl_podrld_turret_delay_stop')
