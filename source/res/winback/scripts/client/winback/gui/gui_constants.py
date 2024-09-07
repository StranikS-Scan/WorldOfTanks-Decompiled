# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/gui_constants.py
from constants_utils import ConstInjector
from messenger import m_constants
SM_TYPE_WINBACK_PROGRESSION = 'WinbackProgressionNotification'

class SCH_CLIENT_MSG_TYPE(m_constants.SCH_CLIENT_MSG_TYPE, ConstInjector):
    WINBACK_PROGRESSION_NOTIFICATIONS = 500
    WINBACK_SELECTABLE_REWARD = 501
