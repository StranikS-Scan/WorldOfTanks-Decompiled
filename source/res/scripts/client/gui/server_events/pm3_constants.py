# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/pm3_constants.py
from sound_gui_manager import CommonSoundSpaceSettings

class SOUNDS(object):
    COMMON_SOUND_SPACE = 'personalMissions'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_MISSIONS = 'STATE_hangar_place_personalMissions_lbz'
    AMBIENT = 'pm3_lbz_ambient'
    MUSIC = 'pm3_lbz_music'
    STATE_SCREEN_GROUP = 'STATE_pm_lbz'
    STATE_PLACE_SPLIT_SCREEN = 'STATE_pm_lbz_screen_01'
    STATE_PLACE_OPERATION_SCREEN = 'STATE_pm_lbz_screen_02'
    STATE_PLACE_TASK_SCREEN = 'STATE_pm_lbz_screen_03'
    PROJECTOR = 'pm3_lbz_projector_appear'
    PROJECTOR_SLIDE_IN = 'pm3_lbz_projector_slide_in'
    PROJECTOR_SLIDE_OUT = 'pm3_lbz_projector_slide_out'
    SWITCH_CARD_ANIMATION = 'pm_type_select_animation'
    AWARD_WINDOW = 'pm_standard_greeting'
    WOMAN_AWARD_WINDOW = 'pm_special_greeting_woman'
    TANK_AWARD_WINDOW = 'pm_special_greeting_tank'
    STATE_OVERLAY_HANGAR_GENERAL_GROUP = 'STATE_overlay_hangar_general'
    STATE_OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    STATE_OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'
    STATE_OPERATION_REWARD_PREVIEW_SCREEN = 'STATE_hangar_place_personalMissions_lbz_preview'
    EVENT_REWARD_SCREEN_GENERAL = 'gui_reward_screen_general'
    EVENT_SPECIAL_GREETING = 'gui_special_greeting'


_SOUNDS_PRIORITIES = (SOUNDS.AWARD_WINDOW, SOUNDS.WOMAN_AWARD_WINDOW, SOUNDS.TANK_AWARD_WINDOW)
PERSONAL_MISSIONS_3_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.COMMON_SOUND_SPACE, entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_MISSIONS}, exitStates={}, persistentSounds=(SOUNDS.MUSIC, SOUNDS.AMBIENT), stoppableSounds=(), priorities=_SOUNDS_PRIORITIES, autoStart=True, enterEvent='', exitEvent='')

class VoiceOvers(object):
    SPLIT_SCREEN_VO = 'pm3_cabinet_vo'
    STOP_SPLIT_SCREEN_VO = 'pm3_cabinet_vo_stop'
    OPERATION_SCREEN_VO = 'pm3_operation_vo'
    STOP_OPERATION_VO = 'pm3_operation_vo_stop'
    OPERATION_SCREEN_GROUP = 'SWITCH_ext_pm3_operation'
    SWITCH_OPERATION_01 = 'SWITCH_ext_pm3_operation_01'
    SWITCH_OPERATION_02 = 'SWITCH_ext_pm3_operation_02'
    SWITCH_OPERATION_03 = 'SWITCH_ext_pm3_operation_03'
    REWARD_SCREEN_VO = 'pm3_reward_vo'
    STOP_REWARD_VO = 'pm3_reward_vo_stop'
    REWARD_GROUP = 'SWITCH_ext_pm3_reward'
    REWARD_SWITCH_SIMPLE = 'SWITCH_ext_pm3_reward_simple'
    REWARD_SWITCH_HONOR = 'SWITCH_ext_pm3_reward_honor'


class VIDEO(object):
    GROUP = 'STATE_video_overlay'
    PLAY = 'STATE_video_overlay_on'
    STOP = 'STATE_video_overlay_off'
    STOP_EVENT = 'pm3_lbz_vid_stop'
    PAUSE = 'pm3_lbz_vid_pause'
    RESUME = 'pm3_lbz_vid_resume'
    RTPC = 'RTPC_ext_video_volume'
    SOUND_INTRO = 'pm3_lbz_vid_intro'
    SOUND_REWARD_1 = 'pm3_lbz_vid_A161_ARMT'
    SOUND_REWARD_2 = 'pm3_lbz_vid_A173_TF_2_CLARK'
    SOUND_REWARD_3 = 'pm3_lbz_vid_F119_Projet_Murat'
    SOUND_REWARD_4 = 'pm3_lbz_vid_T11'
