# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/uilogging/armory_yard/loggers.py
import json
from wotdecorators import noexcept
from itertools import chain
from uilogging.base.logger import MetricsLogger
from armory_yard.uilogging.armory_yard.constants import FEATURE, FREE_REROLL, Actions, Items

class ArmoryYardLogger(MetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(ArmoryYardLogger, self).__init__(FEATURE)

    @noexcept
    def logRerollQuest(self, questData, currency):
        currency = currency if currency else FREE_REROLL
        self.log(action=Actions.CLICK, item=Items.REROLL_BUTTON, info=json.dumps(questData), itemState=currency)

    @noexcept
    def getQuestSnapshot(self, questSubModel):
        snapshot = {}
        for quest in questSubModel.getQuests():
            questId = quest.getId().split(':', 1)[1]
            snapshot[questId] = {'current': [],
             'total': []}
            if quest.getTotal():
                self._addQuestProgress(snapshot, questId, quest)
            for condition in chain(quest.bonusCondition.getItems(), quest.postBattleCondition.getItems()):
                if condition.getTotal():
                    self._addQuestProgress(snapshot, questId, quest)

        return snapshot

    def _addQuestProgress(self, snapshot, questId, quest):
        snapshot[questId]['current'].append(quest.getCurrent())
        snapshot[questId]['total'].append(quest.getTotal())
