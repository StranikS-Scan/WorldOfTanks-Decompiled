# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/skeletons/armory_yard_reroll_controller.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from armory_yard.gui.shared.armory_dynamic_quest import ArmoryDynamicQuest
    from typing import List, Optional
    from gui.server_events.event_items import TokenQuest
    from Event import Event

class IArmoryYardRerollController(IGameController):
    onQuestConditionUpdated = None
    onQuestConditionsReset = None
    onPDataUpdated = None
    onFreeRerollTokensUpdated = None
    onRerollQuest = None
    onAcceptReroll = None

    def getConditionQuestsByTokenQuest(self, tokenQuest):
        raise NotImplementedError

    def getArmoryTokenQuestByID(self, questID):
        raise NotImplementedError

    def getConditionQuestsByID(self, reqToken):
        raise NotImplementedError

    def getRerollCurrencies(self):
        raise NotImplementedError

    def getRerollCost(self, currency):
        raise NotImplementedError

    def getFreeRerollsCount(self, groupName):
        raise NotImplementedError

    def getFreeRerollsCountByCycleID(self, cycleID):
        raise NotImplementedError

    def getNextFreeRerollTimestamp(self):
        raise NotImplementedError

    def getFreeRerollCountdown(self):
        raise NotImplementedError

    def getHideBattleTypes(self):
        raise NotImplementedError

    def isRerollEnabled(self):
        raise NotImplementedError

    def getTokenQuestIDByConditionID(self, conditionID):
        raise NotImplementedError

    def getReplacedTokenQuestID(self):
        raise NotImplementedError

    def getConditionIDsForReroll(self, replacedTokenQuestID):
        raise NotImplementedError

    def validateAcceptQuestID(self, questID):
        raise NotImplementedError

    def getRerollContext(self):
        raise NotImplementedError
