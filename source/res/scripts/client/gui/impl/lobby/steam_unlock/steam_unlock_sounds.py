# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/steam_unlock/steam_unlock_sounds.py
from gui.sounds.filters import StatesGroup, States
from sound_gui_manager import CommonSoundSpaceSettings
SOUND_SPACE_NAME = 'steam_unlock'
SOUND_SPACE_NAME_ENTER_EVENT = 'bp_reward_screen'
STEAM_UNLOCK_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUND_SPACE_NAME, entranceStates={StatesGroup.OVERLAY_HANGAR_GENERAL: States.OVERLAY_HANGAR_GENERAL_ON}, exitStates={StatesGroup.OVERLAY_HANGAR_GENERAL: States.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SOUND_SPACE_NAME_ENTER_EVENT, exitEvent='', parentSpace='')
