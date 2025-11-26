# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/random/sound_manager.py
from __future__ import absolute_import
from gui.impl.lobby.hangar.base.sound_constants import HangarSoundStates
from sound_gui_manager import CommonSoundSpaceSettings
SOUND_ALL_VEHICLES_ENTERED = 'gui_space_enter'
SOUND_ALL_VEHICLES_EXITED = 'gui_space_exit'
RANDOM_HANGAR_SOUND_SPACE = CommonSoundSpaceSettings(name='hangar', entranceStates={HangarSoundStates.PLACE.value: HangarSoundStates.PLACE_GARAGE.value}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
ALL_VEHICLES_SOUND_SPACE = CommonSoundSpaceSettings(name='allVehicles', entranceStates={HangarSoundStates.SPACE.value: HangarSoundStates.ALL_VEHICLES_ON.value}, exitStates={HangarSoundStates.SPACE.value: HangarSoundStates.ALL_VEHICLES_OFF.value}, enterEvent=(), exitEvent=(), persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
PLAY_LISTS_SOUND_SPACE = CommonSoundSpaceSettings(name='playlists', entranceStates={HangarSoundStates.SPACE.value: HangarSoundStates.ALL_VEHICLES_ON.value}, exitStates={HangarSoundStates.SPACE.value: HangarSoundStates.ALL_VEHICLES_OFF.value}, enterEvent=(), exitEvent=(), persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
