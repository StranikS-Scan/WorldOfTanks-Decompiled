# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/epic_battle/constants.py
from enum import Enum
FEATURE = 'epic_battle'

class EpicBattleLogActions(Enum):
    OPEN = 'open'
    CLOSE = 'close'
    CLICK = 'click'
    TOOLTIP_WATCHED = 'tooltip_watched'
    VIEW_WATCHED = 'view_watched'


class EpicBattleLogKeys(Enum):
    ABILITIES_CONFIRM = 'abilities_confirm'
    SETUP_VIEW = 'setup_view'
    DROP_SKILL_DIALOG_CONFIRM = 'drop_skill_dialog_confirm'
    BUTTON = 'button'
    HANGAR = 'hangar'
    CONTAINER_VIEW = 'container_view'
    PROGRESS_VIEW = 'progress_view'
    SKILLS_VIEW = 'skills_view'
    REWARDS_VIEW = 'rewards_view'
    INFO_VIEW = 'info_view'
    AFTER_BATTLE_VIEW = 'after_battle_view'
    REWARDS_SELECTION_VIEW = 'rewards_selection_view'
    AWARDS_VIEW = 'awards_view'


class EpicBattleLogButtons(Enum):
    INSTALL = 'install'
    NOT_INSTALL = 'not_install'
    CLOSE = 'close'
    RESERVES = 'reserves'
    CHECKBOX = 'checkbox'
    CANCEL = 'cancel'
    CONFIRM = 'confirm'
    SHOP = 'shop'
    REWARDS = 'rewards_button'
    NEXT = 'next'
    LEVELUP_NOTIFICATION = 'levelup_notification'
    ENTRY_POINT = 'entry_point'
    REWARDS_SELECTION_CONFIRM = 'rewards_selection_confirm'
    REWARDS_SELECTION_CLOSE = 'rewards_selection_close'


class EpicBattleLogTabs(Enum):
    PROGRESS_TAB = 'progress_tab'
    SKILLS_TAB = 'skills_tab'
    REWARDS_TAB = 'rewards_tab'
    INFO_TAB = 'info_tab'


class EpicBattleLogAdditionalInfo(Enum):
    APPLY_TO_VEHICLE = 'apply_to_vehicle'
    APPLY_TO_CLASS = 'apply_to_class'


class EpicBattleLogItemStates(Enum):
    ADVANCED = 'advanced'
