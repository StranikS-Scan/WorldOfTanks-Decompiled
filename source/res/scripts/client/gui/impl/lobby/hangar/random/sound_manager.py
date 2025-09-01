# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/random/sound_manager.py
from __future__ import absolute_import
from sound_gui_manager import CommonSoundSpaceSettings
SOUND_STATE_PLACE = 'STATE_hangar_place'
SOUND_STATE_SPACE = 'STATE_hangar_space'
SOUND_STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'
SOUND_STATE_ALL_VEHICLES_ON = 'STATE_hangar_space_on'
SOUND_STATE_ALL_VEHICLES_OFF = 'STATE_hangar_space_off'
SOUND_ALL_VEHICLES_ENTERED = 'gui_space_enter'
SOUND_ALL_VEHICLES_EXITED = 'gui_space_exit'
RANDOM_HANGAR_SOUND_SPACE = CommonSoundSpaceSettings(name='hangar', entranceStates={SOUND_STATE_PLACE: SOUND_STATE_PLACE_GARAGE}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
ALL_VEHICLES_SOUND_SPACE = CommonSoundSpaceSettings(name='allVehicles', entranceStates={SOUND_STATE_SPACE: SOUND_STATE_ALL_VEHICLES_ON}, exitStates={SOUND_STATE_SPACE: SOUND_STATE_ALL_VEHICLES_OFF}, enterEvent=(), exitEvent=(), persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
PLAY_LISTS_SOUND_SPACE = CommonSoundSpaceSettings(name='playlists', entranceStates={SOUND_STATE_SPACE: SOUND_STATE_ALL_VEHICLES_ON}, exitStates={SOUND_STATE_SPACE: SOUND_STATE_ALL_VEHICLES_OFF}, enterEvent=(), exitEvent=(), persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
