# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/notification/__init__.py
from fun_random.messenger.formatters.service_channel import FunRandomNotificationsFormatter
from fun_random.messenger.formatters.token_quest_subformatters import FunProgressionRewardsAsyncFormatter, FunProgressionRewardsSyncFormatter
from fun_random.notification.actions_handlers import SelectFunRandomMode, ShowFunRandomProgression
from gui.shared.system_factory import registerNotificationsActionsHandlers, registerMessengerClientFormatter, registerTokenQuestsSubFormatter
from messenger.m_constants import SCH_CLIENT_MSG_TYPE

def registerFunRandomNotifications():
    registerNotificationsActionsHandlers((SelectFunRandomMode, ShowFunRandomProgression))
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.FUN_RANDOM_NOTIFICATIONS, FunRandomNotificationsFormatter())
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.FUN_RANDOM_PROGRESSION, FunProgressionRewardsSyncFormatter())
    registerTokenQuestsSubFormatter(FunProgressionRewardsAsyncFormatter())
