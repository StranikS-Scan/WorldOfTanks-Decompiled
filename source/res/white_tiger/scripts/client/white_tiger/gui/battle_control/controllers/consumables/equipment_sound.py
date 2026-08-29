# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/consumables/equipment_sound.py
import SoundGroups
from items import vehicles
from cgf_components import sound_helpers
from constants import EQUIPMENT_STAGES
from gui.battle_control.controllers.consumables.equipment_ctrl import EquipmentSound
_INVISIBILITY_MOD_A_START_VO = 'wt_vo_ability_invisibility_a_in'
_INVISIBILITY_MOD_A_STOP_VO = 'wt_vo_ability_invisibility_a_out'
_INVISIBILITY_MOD_B_START_VO = 'wt_vo_ability_invisibility_b_in'
_ABILITIES_VOICEOVERS = {'wt_hyperion_mod_b': {EQUIPMENT_STAGES.READY: 'wt_vo_ability_bells_ready'},
 'wt_extractor_shot': {EQUIPMENT_STAGES.ACTIVE: 'wt_vo_ability_energy_steal_work'},
 'wt_stun_area': {EQUIPMENT_STAGES.COOLDOWN: 'wt_vo_ability_emp_web_work'},
 'wt_invisibility_mod_a': {EQUIPMENT_STAGES.ACTIVE: _INVISIBILITY_MOD_A_START_VO,
                           EQUIPMENT_STAGES.COOLDOWN: _INVISIBILITY_MOD_A_STOP_VO},
 'wt_invisibility_mod_b': {EQUIPMENT_STAGES.ACTIVE: _INVISIBILITY_MOD_B_START_VO}}
_DECREASE_RELOAD_SOUND_BY_LEVEL = ['ev_wt_ability_decrease_reload_time_00',
 'ev_wt_ability_decrease_reload_time_01',
 'ev_wt_ability_decrease_reload_time_02',
 'ev_wt_ability_decrease_reload_time_03',
 'ev_wt_ability_decrease_reload_time_04',
 'ev_wt_ability_decrease_reload_time_05']
_INCREASE_DAMAGE_SOUND_BY_LEVEL = ['ev_wt_ability_increase_damage_ui_00',
 'ev_wt_ability_increase_damage_ui_01',
 'ev_wt_ability_increase_damage_ui_02',
 'ev_wt_ability_increase_damage_ui_03',
 'ev_wt_ability_increase_damage_ui_04',
 'ev_wt_ability_increase_damage_ui_05']
_INCREASE_DAMAGE_SOUND_3D_BY_LEVEL = {1: 'ev_wt_ability_increase_damage_shot_01',
 2: 'ev_wt_ability_increase_damage_shot_02',
 3: 'ev_wt_ability_increase_damage_shot_03',
 4: 'ev_wt_ability_increase_damage_shot_04',
 5: 'ev_wt_ability_increase_damage_shot_05'}
_EXPLOSIVE_SHIELD_SOUNDS = {'Start': 'ev_wt_ability_explosive_shield_start',
 'Hit': 'ev_wt_ability_explosive_shield_hit',
 'End': 'ev_wt_ability_explosive_shield_stop',
 'Explode': 'ev_wt_ability_explosive_shield_explode'}
_WT_STUN_AREA_HIT_VO = 'wt_hunters_vo_ability_emp_web_debuff'
_WT_VAMPIRISM_REPAIR = 'ev_wt_gameplay_full_repair_impulse'
_WT_STUN_SHOT_PC = 'ev_white_tiger_gameplay_wt_stun_shot_pc'
_WT_STUN_SHOT_NPC = 'ev_white_tiger_gameplay_wt_stun_shot_npc'
_WT_ENHANCED_SHOT_ON_SHOT_PC = 'ev_wt_ability_enhanced_shot_PC'
_WT_ENHANCED_SHOT_ON_SHOT_NPC = 'ev_wt_ability_enhanced_shot_NPC'
_WT_DOME_ENTER = 'ev_wt_ability_dome_in'
_WT_DOME_EXIT = 'ev_wt_ability_dome_out'
_WT_HYPERION_CANCELED_VO = 'wt23_both_vo_hyperion_canceled'
_WT_HYPERION_MOD_B_CHARGING = 'ev_wt_gameplay_bells_charging'
_WT_HYPERION_MOD_B_SHOOTING = 'ev_wt_gameplay_bells_blast_main'
_WT_HYPERION_MOD_B_INTERRUPTION = 'ev_wt_gameplay_bells_start_up_interrupted'
_WT_INVISIBILITY_MOD_A_ENTRANCE = 'ev_wt_ability_invisibility_a_in_PC'
_WT_INVISIBILITY_MOD_A_ESCAPE = 'ev_wt_ability_invisibility_a_out_PC'
_WT_INVISIBILITY_MOD_B = 'ev_wt_ability_invisibility_b'

class WtEquipmentSound(EquipmentSound):

    @staticmethod
    def playPressed(item, result):
        equipment = vehicles.g_cache.equipments()[item.getEquipmentID()]
        if equipment is not None:
            sound = equipment.soundPressedReady if result else equipment.soundPressedNotReady
            if sound is not None:
                SoundGroups.g_instance.playSound2D(sound)
        return

    @staticmethod
    def playVoiceOver(voiceOver):
        sound_helpers.playNotification(voiceOver)

    @staticmethod
    def playSound3D(soundEvent, position):
        SoundGroups.g_instance.playSoundPos(soundEvent, position)

    @staticmethod
    def playSound2D(sound):
        SoundGroups.g_instance.playSound2D(sound)


def playAbilityVoiceOver(item):
    ability = _ABILITIES_VOICEOVERS.get(item.getDescriptor().name, None)
    if ability:
        vo = ability.get(item.getStage(), None)
        WtEquipmentSound.playVoiceOver(vo)
    return


def playStunAreaHunterVO():
    WtEquipmentSound.playVoiceOver(_WT_STUN_AREA_HIT_VO)


def playVampirismRepair(position):
    WtEquipmentSound.playSound3D(_WT_VAMPIRISM_REPAIR, position)


def playExtractorShot(isPC, position):
    sound = _WT_STUN_SHOT_PC if isPC else _WT_STUN_SHOT_NPC
    WtEquipmentSound.playSound3D(sound, position)


def playStunAreaShot(isPC, position):
    playExtractorShot(isPC, position)


def playEnhancedShotOnShotSound(position, isPC):
    WtEquipmentSound.playSound3D(_WT_ENHANCED_SHOT_ON_SHOT_PC if isPC else _WT_ENHANCED_SHOT_ON_SHOT_NPC, position)


def playDecreaseReloadByLevel(level):
    sound = _DECREASE_RELOAD_SOUND_BY_LEVEL[level]
    WtEquipmentSound.playSound2D(sound)


def playIncreaseDamageByLevel(level, position):
    sound = _INCREASE_DAMAGE_SOUND_BY_LEVEL[level]
    WtEquipmentSound.playSound2D(sound)
    sound = _INCREASE_DAMAGE_SOUND_3D_BY_LEVEL.get(level)
    if sound:
        WtEquipmentSound.playSound3D(sound, position)


def playExplosiveShieldSound(layerName, vehicle):
    event = _EXPLOSIVE_SHIELD_SOUNDS.get(layerName)
    if event:
        sound_helpers.playVehicleSound(event, vehicle)


def playDomeSound(isEntered):
    sound = _WT_DOME_ENTER if isEntered else _WT_DOME_EXIT
    WtEquipmentSound.playSound2D(sound)


def playHyperionModBCharging(position):
    WtEquipmentSound.playSound3D(_WT_HYPERION_MOD_B_CHARGING, position)


def playHyperionModBShooting(position):
    WtEquipmentSound.playSound3D(_WT_HYPERION_MOD_B_SHOOTING, position)


def playHyperionModBInterruption(position):
    WtEquipmentSound.playVoiceOver(_WT_HYPERION_CANCELED_VO)
    WtEquipmentSound.playSound3D(_WT_HYPERION_MOD_B_INTERRUPTION, position)


def playInvisibilityModASound(isEntrance):
    sound = _WT_INVISIBILITY_MOD_A_ENTRANCE if isEntrance else _WT_INVISIBILITY_MOD_A_ESCAPE
    WtEquipmentSound.playSound2D(sound)


def playInvisibilityModBSound():
    WtEquipmentSound.playSound2D(_WT_INVISIBILITY_MOD_B)


def playVOInvisibilityModAStart():
    WtEquipmentSound.playVoiceOver(_INVISIBILITY_MOD_A_START_VO)


def playVOInvisibilityModAStop():
    WtEquipmentSound.playVoiceOver(_INVISIBILITY_MOD_A_STOP_VO)


def playVOInvisibilityModBStart():
    WtEquipmentSound.playVoiceOver(_INVISIBILITY_MOD_B_START_VO)
