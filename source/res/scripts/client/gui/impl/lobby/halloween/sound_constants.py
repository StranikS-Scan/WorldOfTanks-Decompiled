# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/sound_constants.py
from shared_utils import CONST_CONTAINER
from gui.sounds.filters import StatesGroup, States
from sound_gui_manager import CommonSoundSpaceSettings

class EventHangarSound(CONST_CONTAINER):
    HANGAR = 'hangar'
    SOUND_STATE_PLACE = 'STATE_hangar_place'
    SOUND_STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'
    ARTEFACTS_GROUP = 'STATE_ev_halloween_2021_artefcats'
    ARTEFACTS_INTRO = 'STATE_ev_halloween_2021_artefcats_begin'
    ARTEFACTS_ENCREPTED = 'STATE_ev_halloween_2021_artefcats_encrypted'
    ARTEFACTS_OPENED = 'STATE_ev_halloween_2021_artefcats_open'
    ARTEFACTS_CLOSED = 'STATE_ev_halloween_2021_artefcats_closed'
    ARTEFACTS_KING_TIGGER = 'STATE_ev_halloween_2021_artefcats_king_tiger'
    DIFFICULTY_LEVEL_EVENT = 'ev_halloween_2021_hangar_ui_dificult_level_{}'
    PLAY_VIDEO = 'ev_halloween_2021_hangar_ui_play_video'
    DECODED_REWARD = 'ev_halloween_2021_hangar_ui_decoded'
    TIGER_REWARD = 'ev_halloween_2021_hangar_ui_king_tiger_reward'
    STANDARD_REWARD = 'ev_halloween_2021_hangar_ui_greeting_standard'
    KEY_COUNTER_ENTER = 'ev_halloween_2021_hangar_ui_key_enter'
    KEY_COUNTER_EXIT = 'ev_halloween_2021_hangar_ui_key_exit'
    BOSSFIGHT_OPENED = 'ev_halloween_2021_vo_bossfight_open'


EVENT_HANGAR_SOUND_SPACE = CommonSoundSpaceSettings(name=EventHangarSound.HANGAR, entranceStates={EventHangarSound.SOUND_STATE_PLACE: EventHangarSound.SOUND_STATE_PLACE_GARAGE,
 StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
