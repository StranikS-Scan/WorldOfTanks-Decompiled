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
    def logRerollQuest(self, questSubModel, currency):
        currency = currency if currency else FREE_REROLL
        logInfo = {}
        for quest in questSubModel.getQuests():
            questId = quest.getId().split(':', 1)[1]
            logInfo[questId] = {'current': [],
             'total': []}
            if quest.getTotal():
                self._addQuestProgress(logInfo, questId, quest)
            for condition in chain(quest.bonusCondition.getItems(), quest.postBattleCondition.getItems()):
                if condition.getTotal():
                    self._addQuestProgress(logInfo, questId, condition)

        self.log(action=Actions.CLICK, item=Items.REROLL_BUTTON, info=json.dumps(logInfo), itemState=currency)

    def _addQuestProgress(self, logInfo, questId, condition):
        logInfo[questId]['current'].append(condition.getCurrent())
        logInfo[questId]['total'].append(condition.getTotal())
