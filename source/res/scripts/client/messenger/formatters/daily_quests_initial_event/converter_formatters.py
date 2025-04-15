# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/daily_quests_initial_event/converter_formatters.py
from constants import PREMIUM_ENTITLEMENTS
from gui.shared.formatters import text_styles
from gui.shared.notifications import NotificationPriorityLevel
from gui.impl import backport
from gui.impl.gen import R
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData

class DailyQuestsEpicCompensationFormatter(ServiceChannelFormatter):
    _MSG_TEMPLATE = 'DailyQuestsEpicCompensation'

    def format(self, message, *args):
        data = message.data['extData']['dailyQuests']
        crystal = data.get('crystal', 0)
        entitlements = data.get('entitlements', {})
        if data:
            formattedRewards = self.__formatRewards(crystal, entitlements)
            formatter = g_settings.msgTemplates.format(self._MSG_TEMPLATE, {'rewards': formattedRewards})
            return [MessageData(formatter, self._getGuiSettings(message, self._MSG_TEMPLATE, priorityLevel=NotificationPriorityLevel.MEDIUM))]
        return []

    def __formatRewards(self, crystal, entitlements):
        resourceStrings = []
        msg = R.strings.messenger.serviceChannelMessages.resourceWell
        if crystal:
            resourceStrings.append(backport.text(msg.crystal(), count=text_styles.crystal(crystal)))
        if entitlements.get(PREMIUM_ENTITLEMENTS.PLUS):
            daysStr = backport.getIntegralFormat(entitlements[PREMIUM_ENTITLEMENTS.PLUS].get('count', 0))
            resourceStrings.append(backport.text(msg.premium_plus(), count=text_styles.crystal(daysStr)))
        return backport.text(msg.breakLine()).join(resourceStrings)
