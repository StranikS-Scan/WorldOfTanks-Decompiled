# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/sound_constants.py
from sound_gui_manager import CommonSoundSpaceSettings
from gui.sounds.filters import States, StatesGroup
FIELD_POST_SOUND_SETTINGS = CommonSoundSpaceSettings(name='field_post', entranceStates={'STATE_hangar_place': 'STATE_hangar_place_garage',
 StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_ON}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
SUBVIEW_SOUND_SPACE = CommonSoundSpaceSettings(name='sub_view', entranceStates={'STATE_hangar_place': 'STATE_hangar_place_garage',
 StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_ON}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
BROWSER_VIEW_SOUND_SPACES = {FIELD_POST_SOUND_SETTINGS.name: FIELD_POST_SOUND_SETTINGS,
 SUBVIEW_SOUND_SPACE.name: SUBVIEW_SOUND_SPACE}
