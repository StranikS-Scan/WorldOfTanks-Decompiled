# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/new_year_post_event/converter_formatters.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData

class NewYearMandarinsConverterFormatter(ServiceChannelFormatter):
    _MSG_TEMPLATE = 'NewYearMandarinsConverts'

    def format(self, message, *args):
        data = message.data['extData']['newYear25']
        mandarins = data.get('ny25_mandarin', 0) * -1
        machineCount = data.get('machine_coin', 0)
        msgR = R.strings.messenger.serviceChannelMessages.newYearMandarinsConvert
        if machineCount:
            msg = backport.text(msgR.text(), mandarinsCount=mandarins, machineCount=machineCount)
            header = backport.text(msgR.header())
            formatter = g_settings.msgTemplates.format(self._MSG_TEMPLATE, {'text': msg,
             'header': header})
            return [MessageData(formatter, self._getGuiSettings(message, self._MSG_TEMPLATE, priorityLevel=NotificationPriorityLevel.MEDIUM))]
        return []
