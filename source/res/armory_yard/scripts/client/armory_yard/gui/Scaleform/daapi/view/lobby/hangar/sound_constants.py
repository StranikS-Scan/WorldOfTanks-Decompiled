# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/Scaleform/daapi/view/lobby/hangar/sound_constants.py
from gui.sounds.filters import StatesGroup, States
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class SOUNDS(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'armory_yard'
    COMMON_SOUND_INTRO_SPACE = 'armory_yard_intro'
    COMMON_SOUND_VIDEO_REWARD_SPACE = 'armory_yard_reward_video'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_AY = 'STATE_hangar_place_customization'
    STATE_PLACE_VEHICLE_PREVIEW = 'STATE_ay_preview'
    STATE_PLACE_VEHICLE_PREVIEW_ENTER = 'STATE_ay_preview_enter'
    STATE_PLACE_VEHICLE_PREVIEW_EXIT = 'STATE_ay_preview_exit'
    VO_TAPE_RECORDER = 'ay_voiceover_taperecorder_ep_03_stage_{:02d}_start'
    FIRST_ENTER = 'armory_yard_enter_first'
    ENTER = 'armory_yard_enter'
    EXIT = 'armory_yard_exit'


def getStageVoTapeRecorderName(stage):
    return SOUNDS.VO_TAPE_RECORDER.format(stage)


ARMORY_YARD_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.COMMON_SOUND_SPACE, entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_AY,
 SOUNDS.STATE_PLACE_VEHICLE_PREVIEW: SOUNDS.STATE_PLACE_VEHICLE_PREVIEW_EXIT}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
ARMORY_YARD_INTRO_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.COMMON_SOUND_INTRO_SPACE, entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_AY,
 StatesGroup.VIDEO_OVERLAY: States.VIDEO_OVERLAY_ON}, exitStates={StatesGroup.VIDEO_OVERLAY: States.VIDEO_OVERLAY_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
ARMORY_YARD_REWARD_VIDEO_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.COMMON_SOUND_VIDEO_REWARD_SPACE, entranceStates={StatesGroup.VIDEO_OVERLAY: States.VIDEO_OVERLAY_ON}, exitStates={StatesGroup.VIDEO_OVERLAY: States.VIDEO_OVERLAY_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
ARMORY_YARD_VEHICLE_PREVIEW_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.COMMON_SOUND_SPACE, entranceStates={SOUNDS.STATE_PLACE_VEHICLE_PREVIEW: SOUNDS.STATE_PLACE_VEHICLE_PREVIEW_ENTER}, exitStates={SOUNDS.STATE_PLACE_VEHICLE_PREVIEW: SOUNDS.STATE_PLACE_VEHICLE_PREVIEW_EXIT}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
