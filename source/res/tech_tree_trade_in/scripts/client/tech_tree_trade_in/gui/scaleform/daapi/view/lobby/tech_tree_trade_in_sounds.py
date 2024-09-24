# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/scaleform/daapi/view/lobby/tech_tree_trade_in_sounds.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class Sounds(CONST_CONTAINER):
    OVERLAY_SPACE_NAME = 'tech_tree_trade_in_overlay'
    OVERLAY_HANGAR_GENERAL = 'STATE_overlay_hangar_general'
    OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'


TECH_TREE_TRADE_IN_OVERLAY_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.OVERLAY_SPACE_NAME, entranceStates={Sounds.OVERLAY_HANGAR_GENERAL: Sounds.OVERLAY_HANGAR_GENERAL_ON}, exitStates={Sounds.OVERLAY_HANGAR_GENERAL: Sounds.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
