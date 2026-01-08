# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/maps_blacklist/sound_constants.py
from gui.sounds.filters import States, StatesGroup
from sound_gui_manager import CommonSoundSpaceSettings
BLACKLIST_SOUND_SETTINGS = CommonSoundSpaceSettings(name='blacklistHangar', entranceStates={StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_ON}, exitStates={StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
