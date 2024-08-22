# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/crew_nps/logging_constants.py
from enum import Enum
FEATURE = 'crew_nps'

class CrewBannerWidgetKeys(Enum):
    CREW_BANNER_WIDGET = 'crew_banner_widget'


class CrewBannerWidgetButton(Enum):
    FILL = 'fill'
    RESET = 'reset'


class CrewNpsViewKeys(Enum):
    WELCOME = 'welcome_view'
    INTRO = 'intro_view'
    BARRACKS = 'barracks_view'


class CrewNpsDialogKeys(Enum):
    FILL_ALL_PERKS = 'fill_all_perks_dialog'
    RESET_ALL_CONFIRM = 'reset_all_confirm_dialog'


class CrewNpsNavigationButtons(Enum):
    ESC = 'esc'
    CLOSE = 'close'
    AFFIRMATIVE = 'affirmative'
    VIEW_CHANGES = 'view_changes'
    SKIP_CHANGES = 'skip_changes'


class CrewNpsIntroAdditionalInfo(Enum):
    WITH_BOOKS = '1'
    NO_BOOK = '0'
