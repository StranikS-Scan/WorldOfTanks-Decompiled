# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/lobby/sounds.py
from __future__ import absolute_import
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class SOUNDS(CONST_CONTAINER):
    SPACE = 'open_bundle_space'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_BUNDLE = 'STATE_hangar_place_open_bundle'
    BUNDLE_ENTER = 'openbundle_enter'
    BUNDLE_EXIT = 'openbundle_exit'


OPEN_BUNDLE_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.SPACE, entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_BUNDLE}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SOUNDS.BUNDLE_ENTER, exitEvent=SOUNDS.BUNDLE_EXIT)
