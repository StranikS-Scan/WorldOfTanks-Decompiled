# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/sound_constants.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class SOUNDS(CONST_CONTAINER):
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_AD = 'STATE_hangar_place_acc_dashboard'
    EVENT_ENTER = 'ev_acc_dashboard_enter'
    EVENT_EXIT = 'ev_acc_dashboard_exit'


ACC_DASHBOARD_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.STATE_PLACE, entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_AD}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SOUNDS.EVENT_ENTER, exitEvent=SOUNDS.EVENT_EXIT)
