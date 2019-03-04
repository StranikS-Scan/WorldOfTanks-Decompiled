# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/sound_constants.py
from gui.Scaleform.framework.entities.View import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class Sounds(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'techtree'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_TECHTREE = 'STATE_hangar_place_research'
    AMBIENT = 'researches_ambience'
    MUSIC = 'researches_music'
    BLUEPRINT_VIEW_ON_SOUND_ID = 'gui_blueprint_view_switch_on'
    BLUEPRINT_VIEW_OFF_SOUND_ID = 'gui_blueprint_view_switch_off'
    BLUEPRINT_VIEW_PLUS_SOUND_ID = 'gui_blueprint_view_switch_on_plus'


TECHTREE_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.COMMON_SOUND_SPACE, entranceStates={Sounds.STATE_PLACE: Sounds.STATE_PLACE_TECHTREE}, exitStates={}, persistentSounds=(Sounds.MUSIC, Sounds.AMBIENT), stoppableSounds=(), priorities=(), autoStart=True)
