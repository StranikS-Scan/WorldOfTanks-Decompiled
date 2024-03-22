# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/clan_supply/sound_helper.py
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class SOUNDS(CONST_CONTAINER):
    ENTER_EVENT = 'clans_supply_map_carro45t_enter'
    EXIT_EVENT = 'clans_supply_map_carro45t_exit'
    STATE_HP_CLANS_INSIDE = 'STATE_hp_clans_inside'
    STATE_HP_CLANS_INSIDE_SUPPLY = 'STATE_hp_clans_inside_supply'
    STATE_HP_CLANS_INSIDE_MAIN = 'STATE_hp_clans_inside_main'
    STATE_HANGAR_FILTERED = 'STATE_hangar_filtered'
    STATE_HANGAR_FILTERED_ON = 'STATE_hangar_filtered_on'
    STATE_HANGAR_FILTERED_OFF = 'STATE_hangar_filtered_off'
    STATE_HANGAR_PLACE = 'STATE_hangar_place'
    STATE_HANGAR_PLACE_CLANS = 'STATE_hangar_place_clans'


def getMainSoundSpace():
    return CommonSoundSpaceSettings(name='clan_supply_main_view', entranceStates={SOUNDS.STATE_HP_CLANS_INSIDE: SOUNDS.STATE_HP_CLANS_INSIDE_SUPPLY}, exitStates={SOUNDS.STATE_HP_CLANS_INSIDE: SOUNDS.STATE_HP_CLANS_INSIDE_MAIN}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SOUNDS.ENTER_EVENT, exitEvent=SOUNDS.EXIT_EVENT)


def getInfoPageSoundSpace():
    return CommonSoundSpaceSettings(name='clan_supply_info_page', entranceStates={SOUNDS.STATE_HANGAR_FILTERED: SOUNDS.STATE_HANGAR_FILTERED_ON}, exitStates={SOUNDS.STATE_HANGAR_FILTERED: SOUNDS.STATE_HANGAR_FILTERED_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
