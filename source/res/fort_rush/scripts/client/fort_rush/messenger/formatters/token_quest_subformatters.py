# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/messenger/formatters/token_quest_subformatters.py
from __future__ import absolute_import
from fort_rush.helpers.utils import isFREventProgressionQuest
from messenger.formatters.service_channel_helpers import MessageData
from messenger.formatters.token_quest_subformatters import SyncTokenQuestsSubFormatter

class FortRushProgressionQuestFormatter(SyncTokenQuestsSubFormatter):

    def format(self, message, *args):
        return [MessageData(None, None)]

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return isFREventProgressionQuest(questID)
