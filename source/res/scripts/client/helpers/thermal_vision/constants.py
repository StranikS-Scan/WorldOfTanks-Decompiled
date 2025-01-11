# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/thermal_vision/constants.py
from helpers.thermal_vision.sound_event import SoundEvent
from helpers.thermal_vision.sound_states_switcher import SoundStatesSwitcher
from helpers.thermal_vision.rtpc_sound_event import RTPCSoundEvent
RTPC_EVENT_WARNING = RTPCSoundEvent('RTPC_ext_un_pyrometer_detecting', 'un_pyrometer_detecting_start_PC', 'un_pyrometer_detecting_stop_PC')
SOUND_SWITCH_ACTIVATION = SoundStatesSwitcher('STATE_un_pyrometer', 'STATE_un_pyrometer_on', 'STATE_un_pyrometer_off')
SOUND_EVENT_ACTIVATION = SoundEvent('un_pyrometer_start', 'un_pyrometer_stop')
SOUND_EVENT_RELOADING = SoundEvent('ability_recharging')
RELOADING_DURATION = 3.0
SOUND_EVENT_NPC_DETECTED = SoundEvent('un_pyrometer_NPC_detected')
