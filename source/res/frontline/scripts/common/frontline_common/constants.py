# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/common/frontline_common/constants.py


class AccountSettingsKeys(object):
    EVENT_KEY = 'frontline_keys'
    SKILL_POINTS_SHOWN = 'points_shown'
    WELCOME_SCREEN_VIEWED = 'welcome_screen_viewed'


class CallbackDataNames(object):
    FL_MODIFIER = 'fl_modifier'


ACCOUNT_DEFAULT_SETTINGS = {AccountSettingsKeys.EVENT_KEY: {AccountSettingsKeys.SKILL_POINTS_SHOWN: {},
                                 AccountSettingsKeys.WELCOME_SCREEN_VIEWED: {}}}
