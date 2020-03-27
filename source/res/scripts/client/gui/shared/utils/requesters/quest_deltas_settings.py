# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/quest_deltas_settings.py
from UserDict import IterableUserDict
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import QUEST_DELTAS, QUESTS
if typing.TYPE_CHECKING:
    from typing import Hashable, Any

class QuestDeltasSettings(IterableUserDict):

    def __init__(self, subKey=''):
        IterableUserDict.__init__(self)
        self._subKey = subKey
        savedSettings = AccountSettings.getSettings(QUESTS).get(QUEST_DELTAS, dict()).get(self._subKey)
        if savedSettings is None:
            return
        else:
            for k, v in savedSettings.iteritems():
                self.data[k] = v

            return

    def __setitem__(self, key, item):
        IterableUserDict.__setitem__(self, key, item)
        self._saveToSettings()

    def __delitem__(self, key):
        IterableUserDict.__delitem__(self, key)
        self._saveToSettings()

    def _saveToSettings(self):
        savedDict = {k:v for k, v in self.data.iteritems()}
        questSettings = AccountSettings.getSettings(QUESTS)
        questSettings.get(QUEST_DELTAS)[self._subKey] = savedDict
        AccountSettings.setSettings(QUESTS, questSettings)
