# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/messenger/formatters/__init__.py
from historical_battles.gui import gui_constants
from historical_battles.messenger.formatters.service_channel import HBArenaBanSystemMessageFormatter, HBArenaWarningSystemMessageFormatter, HBStateMessageFormatter
from gui.shared.system_factory import registerMessengerClientFormatter
from historical_battles.messenger.formatters.service_channel import HBProgressionSystemMessageFormatter
clientFormatters = {gui_constants.SCH_CLIENT_MSG_TYPE.HB_ARENA_BAN_NOTIFICATIONS: HBArenaBanSystemMessageFormatter(),
 gui_constants.SCH_CLIENT_MSG_TYPE.HB_ARENA_WARNING_NOTIFICATIONS: HBArenaWarningSystemMessageFormatter(),
 gui_constants.SCH_CLIENT_MSG_TYPE.HB_STARTED_NOTIFICATION: HBStateMessageFormatter(),
 gui_constants.SCH_CLIENT_MSG_TYPE.HB_PROGRESSION_NOTIFICATIONS: HBProgressionSystemMessageFormatter()}

def registerMessengerClientFormatters():
    for sysMsgType, formatter in clientFormatters.iteritems():
        registerMessengerClientFormatter(sysMsgType, formatter)
