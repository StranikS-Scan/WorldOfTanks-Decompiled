# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/sound_constants.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class SOUNDS(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'c11n'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_C11N = 'STATE_hangar_place_customization'
    STATE_STYLEINFO = 'STATE_infopage_show'
    STATE_STYLEINFO_SHOW = 'STATE_infopage_show_on'
    STATE_STYLEINFO_HIDE = 'STATE_infopage_show_off'
    RTPC_STYLEINFO = 'RTPC_ext_infopage_show'
    ENTER = 'cust_mode_entering'
    EXIT = 'cust_mode_exiting'
    SEASON_SELECT = 'cust_camtype_{}'
    SEASON_SELECT_SUMMER = 'cust_camtype_summer'
    SEASON_SELECT_DESERT = 'cust_camtype_desert'
    SEASON_SELECT_WINTER = 'cust_camtype_winter'
    TAB_SWITCH = 'cust_tab_switch'
    EDIT_MODE_SWITCH_ON = 'cust_style_edit_on'
    EDIT_MODE_SWITCH_OFF = 'cust_style_edit_off'
    NEW_PROGRESSIVE_DECAL = 'cust_progress_reward'
    PROGRESSIVE_DECAL_COULD_BE_INSTALLED = 'cust_progress_reward_edit'
    PROGRESSIVE_DECAL_UPGRADE = 'cust_progress_upgrade'
    SELECT = 'cust_select'
    REMOVE = 'cust_select_remove'
    CHOOSE = 'cust_tankmodule_choose'
    HOVER = 'cust_tankmodule_mouseover'
    PICK = 'cust_color_take'
    RELEASE = 'cust_color_release'
    APPLY = 'cust_color_apply'
    CUST_TICK_ON = 'cust_tick_on'
    CUST_TICK_ON_ALL = 'cust_tick_on_all'
    CUST_TICK_OFF = 'cust_tick_off'
    CUST_CHOICE_NUMBER = 'cust_choice_number'
    CUST_CHOICE_NUMBER_OVER = 'cust_choise_number_over'
    CUST_CHOICE_BACKSPACE = 'cust_choice_backspace'
    CUST_CHOICE_DELETE = 'cust_choice_delete'
    CUST_CHOICE_NUMBER_DENIED = 'cust_choice_number_denied'
    CUST_CHOICE_ESC = 'cust_choise_esc'
    CUST_CHOICE_ENTER = 'cust_choice_enter'


C11N_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.COMMON_SOUND_SPACE, entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_C11N}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SOUNDS.ENTER, exitEvent=SOUNDS.EXIT)
