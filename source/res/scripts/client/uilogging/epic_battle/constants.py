# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/epic_battle/constants.py
from enum import Enum
FEATURE = 'epic_battle'
METRICS = 'metrics'

class EpicBattleLogActions(Enum):
    OPEN = 'open'
    CLOSE = 'close'
    CLICK = 'click'
    TOOLTIP_WATCHED = 'tooltip_watched'


class EpicBattleLogKeys(Enum):
    ABILITIES_CONFIRM = 'abilities_confirm'
    SETUP_VIEW = 'setup_view'
    DROP_SKILL_DIALOG_CONFIRM = 'drop_skill_dialog_confirm'
    BUTTON = 'button'
    HANGAR = 'hangar'


class EpicBattleLogButtons(Enum):
    INSTALL = 'install'
    NOT_INSTALL = 'not_install'
    CLOSE = 'close'
    RESERVES = 'reserves'
    CHECKBOX = 'checkbox'
    CANCEL = 'cancel'
    CONFIRM = 'confirm'


class EpicBattleLogAdditionalInfo(Enum):
    APPLY_TO_VEHICLE = 'apply_to_vehicle'
    APPLY_TO_CLASS = 'apply_to_class'
