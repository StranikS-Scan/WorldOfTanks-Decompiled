# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/messenger/formatters/service_channel.py
from collections import defaultdict
from advent_calendar.gui.feature.constants import LOOTBOX_TOKEN_PREFIX
from messenger import g_settings
from messenger.formatters.service_channel import LootBoxAchievesFormatter
from new_year.gift_machine_helper import getCoinToken

class AdventCalendarProgressionAchievesFormatter(LootBoxAchievesFormatter):

    @classmethod
    def _processTokens(cls, data):
        result = []
        tokens = data.get('tokens', {})
        adventTokens = defaultdict(int)
        newTokens = {}
        for tokenID, info in tokens.iteritems():
            if tokenID == getCoinToken():
                adventTokens['adventNyTerminalToken'] += info.get('count', 0)
            if tokenID.startswith(LOOTBOX_TOKEN_PREFIX):
                adventTokens['adventLootbox'] += info.get('count', 0)
            if tokenID.startswith('ny_gp'):
                adventTokens['adventNYGP'] += info.get('count', 0)
            newTokens[tokenID] = info

        for template, count in adventTokens.items():
            result.append(g_settings.htmlTemplates.format(template, {'count': count}))

        data['tokens'] = newTokens
        parentResult = super(AdventCalendarProgressionAchievesFormatter, cls)._processTokens(data)
        if parentResult:
            result.append(parentResult)
        return cls._SEPARATOR.join(result)
