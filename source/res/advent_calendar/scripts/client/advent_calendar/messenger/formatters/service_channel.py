# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/messenger/formatters/service_channel.py
from __future__ import absolute_import
from advent_calendar.gui.feature.constants import LOOTBOX_TOKEN_PREFIX
from messenger import g_settings
from messenger.formatters.service_channel import LootBoxAchievesFormatter

class AdventCalendarProgressionAchievesFormatter(LootBoxAchievesFormatter):

    @classmethod
    def _processTokens(cls, data):
        result = []
        tokens = data.get('tokens', {})
        count = 0
        newTokens = {}
        for tokenID, info in tokens.items():
            if tokenID.startswith(LOOTBOX_TOKEN_PREFIX):
                count += info.get('count', 0)
            newTokens[tokenID] = info

        if count > 0:
            result.append(g_settings.htmlTemplates.format('adventLootbox', {'count': count}))
            data['tokens'] = newTokens
        parentResult = super(AdventCalendarProgressionAchievesFormatter, cls)._processTokens(data)
        if parentResult:
            result.append(parentResult)
        return cls._SEPARATOR.join(result)
