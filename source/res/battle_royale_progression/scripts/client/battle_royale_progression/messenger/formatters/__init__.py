# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/messenger/formatters/__init__.py
from chat_shared import SYS_MESSAGE_TYPE
from gui.shared.system_factory import registerMessengerServerFormatter
from battle_royale_progression.messenger.formatters.service_channel import BRProgressionSystemMessageFormatter
serverFormatters = {SYS_MESSAGE_TYPE.BRProgressionNotification.index(): BRProgressionSystemMessageFormatter()}

def registerMessengerServerFormatters():
    for sysMsgType, formatter in serverFormatters.iteritems():
        registerMessengerServerFormatter(sysMsgType, formatter)
