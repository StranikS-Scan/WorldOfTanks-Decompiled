# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/one_time_gift_sounds.py
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class Sounds(CONST_CONTAINER):
    OVERLAY_SPACE_NAME = 'one_time_gift_overlay'
    OVERLAY_HANGAR_GENERAL = 'STATE_overlay_hangar_general'
    OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'


ONE_TIME_GIFT_OVERLAY_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.OVERLAY_SPACE_NAME, entranceStates={Sounds.OVERLAY_HANGAR_GENERAL: Sounds.OVERLAY_HANGAR_GENERAL_ON}, exitStates={Sounds.OVERLAY_HANGAR_GENERAL: Sounds.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
