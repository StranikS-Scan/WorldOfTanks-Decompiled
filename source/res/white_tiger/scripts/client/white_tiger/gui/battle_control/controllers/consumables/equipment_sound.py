# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/consumables/equipment_sound.py
import SoundGroups
from items import vehicles
from cgf_components import sound_helpers
from constants import EQUIPMENT_STAGES
from gui.battle_control.controllers.consumables.equipment_ctrl import EquipmentSound
_ABILITIES_VOICEOVERS = {'builtinPlasmaExtractor_wt': {EQUIPMENT_STAGES.READY: 'wt_vo_ability_energy_steal_ready',
                               EQUIPMENT_STAGES.ACTIVE: 'wt_vo_ability_energy_steal_work'},
 'builtinHyperion_wt_2025': {EQUIPMENT_STAGES.READY: 'wt_vo_ability_bells_ready'},
 'builtinStunArea_wt': {EQUIPMENT_STAGES.READY: 'wt_vo_ability_emp_web_ready',
                        EQUIPMENT_STAGES.COOLDOWN: 'wt_vo_ability_emp_web_work'}}
_WT_STUN_AREA_HIT_VO = 'wt_hunters_vo_ability_emp_web_debuff'
_WT_PLASMA_EXTRACTOR_HIT_VO = 'wt_hunters_vo_ability_energy_steal_applied'

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
    def playCancel(item):
        equipment = vehicles.g_cache.equipments()[item.getEquipmentID()]
        if equipment is not None:
            sound = equipment.soundPressedCancel
            if sound is not None:
                SoundGroups.g_instance.playSound2D(sound)
        return

    @staticmethod
    def playVoiceOver(voiceOver):
        sound_helpers.playNotification(voiceOver)


def playAbilityVoiceOver(item):
    ability = _ABILITIES_VOICEOVERS.get(item.getDescriptor().name, None)
    if ability:
        vo = ability.get(item.getStage(), None)
        WtEquipmentSound.playVoiceOver(vo)
    return


def playStunAreaHunterVO():
    WtEquipmentSound.playVoiceOver(_WT_STUN_AREA_HIT_VO)


def playPlasmaExtractorHunterVO():
    WtEquipmentSound.playVoiceOver(_WT_PLASMA_EXTRACTOR_HIT_VO)
