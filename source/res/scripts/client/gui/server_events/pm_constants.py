# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/pm_constants.py
from gui.Scaleform.framework.entities.View import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class SOUNDS(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'personalMissions'
    FIRST_RUN_AWARD_APPEARANCE = 'pm_appearance_of_reward'
    AMBIENT = 'pm_ambient'
    MUSIC = 'pm_music'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'
    STATE_PLACE_MISSIONS = 'STATE_hangar_place_personalMissions'
    RTCP_MISSIONS_NUMBER = 'RTPC_ext_mission_number'
    RTCP_MISSIONS_ZOOM = 'RTPC_ext_mission_zoom'
    RTCP_DEBRIS_CONTROL = 'RTPC_ext_mission_debris_control'
    OPERATION_NAV_CLICK = 'tank_selection'
    OPERATION_NAV_CLICK_ANIMATION = 'pm_tank_select_animation'
    CHAIN_NAV_CLICK = 'pm_type_select_animation'
    REGION_CLICK = 'tabb'
    FREE_AWARD_LIST_SPENT = 'pm_reward_list_spend'
    AWARD_WINDOW = 'pm_standard_greeting'
    AWARD_LIST_AWARD_WINDOW = 'pm_special_greeting'
    WOMAN_AWARD_WINDOW = 'pm_special_greeting_woman'
    TANK_AWARD_WINDOW = 'pm_special_greeting_tank'
    RTCP_OVERLAY = 'RTPC_ext_greeting_overlay'
    ONE_AWARD_LIST_RECEIVED = 'pm_greeting_order_form'
    ONE_AWARD_LIST_RECEIVED_CONFIRM = 'pm_greeting_order_form_confirm'
    FOUR_AWARD_LISTS_RECEIVED = 'pm_conversion_order_form'
    FOUR_AWARD_LISTS_RECEIVED_CONFIRM = 'pm_conversion_order_form_confirm'
    MIN_MISSIONS_ZOOM = 0
    MAX_MISSIONS_ZOOM = 100


_SOUNDS_PRIORITIES = (SOUNDS.AWARD_WINDOW, SOUNDS.WOMAN_AWARD_WINDOW, SOUNDS.TANK_AWARD_WINDOW)
PERSONAL_MISSIONS_SOUND_SPACE = CommonSoundSpaceSettings(SOUNDS.COMMON_SOUND_SPACE, {SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_MISSIONS}, {SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_GARAGE}, (SOUNDS.MUSIC,), (SOUNDS.AMBIENT,), _SOUNDS_PRIORITIES, True, '', '')
PERSONAL_MISSIONS_SILENT_SOUND_SPACE = CommonSoundSpaceSettings(SOUNDS.COMMON_SOUND_SPACE, {}, {}, (), (), _SOUNDS_PRIORITIES, False, '', '')

class FIRST_ENTRY_STATE(CONST_CONTAINER):
    NOT_VISITED = 0
    TUTORIAL_WAS_SHOWN = 1
    AWARDS_WAS_SHOWN = 2


class PM_TUTOR_FIELDS(CONST_CONTAINER):
    FIRST_ENTRY_STATE = 'pm_first_entry'
    INITIAL_FAL_COUNT = 'pm_initial_free_award_lists_count'
    ONE_FAL_SHOWN = 'pm_first_free_award_list_shown'
    FOUR_FAL_SHOWN = 'pm_four_free_award_lists_shown'
