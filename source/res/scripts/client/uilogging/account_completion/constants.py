# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/account_completion/constants.py
from enum import Enum

class LogGroup(str, Enum):
    NICKNAME = 'nickname'
    CREDENTIALS = 'credentials'
    COMPLETE = 'complete'
    CONFIRM = 'confirm'
    MENU = 'menu'
    SKIP_NICKNAME_DIALOG = 'skip_nickname_dialog'
    ACCOUNT_DASHBOARD = 'account_dashboard'
    PLAYER_NAME = 'player_name'


class LogActions(Enum):
    CLOSE_CLICKED = 'close_clicked'
    CONFIRM_CLICKED = 'confirm_clicked'
    CLOSED = 'closed'
    CANCEL_CLICKED = 'cancel_clicked'
    RENAME_CLICKED = 'rename_clicked'
    ESCAPE_PRESSED = 'escape_pressed'
    CONTINUE_CLICKED = 'continue_clicked'
    SETTINGS_CLICKED = 'settings_clicked'
    QUIT_CLICKED = 'quit_clicked'
    RETURN_CLICKED = 'return_clicked'
    CLICKED = 'clicked'


class ViewClosingResult(str, Enum):
    CLOSED = 'closed'
    SUCCESS = 'success'
    BACK_TO_CREDENTIALS = 'back_to_credentials'


FEATURE = 'in_game_registration'
