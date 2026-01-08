# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/battle_context_hints/loggers.py
from uilogging.base.logger import MetricsLogger, createPartnerID
from uilogging.battle_context_hints.constants import FEATURE, BattleContextHintsLogActions

class BattleContextHintsLogger(MetricsLogger):
    __slots__ = ('__partnerId', '__hintId')

    def __init__(self, hintId):
        super(BattleContextHintsLogger, self).__init__(FEATURE)
        self.__partnerId = createPartnerID()
        self.__hintId = hintId

    def logHintActivated(self):
        self.log(action=BattleContextHintsLogActions.HINT_ACTIVATED, item=self.__hintId, partnerID=self.__partnerId)

    def logHintShowed(self):
        self.log(action=BattleContextHintsLogActions.HINT_SHOWED, item=self.__hintId, partnerID=self.__partnerId)

    def logHintApplied(self):
        self.log(action=BattleContextHintsLogActions.HINT_APPLIED, item=self.__hintId, partnerID=self.__partnerId)

    def logHintMaxViewsReached(self):
        self.log(action=BattleContextHintsLogActions.HINT_MAX_VIEWS_REACHED, item=self.__hintId, partnerID=self.__partnerId)
