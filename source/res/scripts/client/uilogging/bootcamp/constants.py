# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/bootcamp/constants.py
from enum import Enum

class BCLogActions(Enum):
    CLOSE = 'close'
    CLICK = 'click'
    CONFIRM = 'confirm'
    SHOW = 'show'
    SELECT = 'select'
    LEAVE = 'leave'
    BUTTON_BACK_TO_HANGAR = 'button_back_to_hangar'
    BUTTON_VIEW_IN_HANGAR = 'button_view_in_hangar'
    VIDEO_FINISHED = 'video_finished'


class BCLogKeys(Enum):
    BC_CURRENT_PROGRESS_WIDGET = 'bc_current_progress_widget'
    BC_PROGRESS_WIDGET = 'bc_progress_widget'
    BC_EXIT_VIEW = 'bc_exit_view'
    BC_DEVICE_SETUP_SUB_VIEW = 'bc_device_setup_sub_view'
    BC_CONSUMABLE_SETUP_SUB_VIEW = 'bc_consumable_setup_sub_view'
    BC_QUESTS_VIEW = 'bc_quests_view'
