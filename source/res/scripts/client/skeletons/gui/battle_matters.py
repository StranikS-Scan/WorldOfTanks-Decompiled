# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/battle_matters.py
import typing
if typing.TYPE_CHECKING:
    from typing import Callable, List, Optional, Union
    from gui.server_events.event_items import Quest, BattleMattersQuest, BattleMattersTokenQuest
    from gui.game_control.battle_matters_controller import _BattleMattersProgressWatcher
    from gui.shared.gui_items.Vehicle import Vehicle
    from Event import Event

class IBattleMattersController(object):
    __slots__ = ('onStateChanged', 'onFinish')

    def __init__(self):
        super(IBattleMattersController, self).__init__()
        self.onStateChanged = None
        self.onFinish = None
        return

    @staticmethod
    def isBattleMattersQuest(quest):
        raise NotImplementedError

    @staticmethod
    def isBattleMattersQuestID(quest):
        raise NotImplementedError

    @staticmethod
    def isRegularBattleMattersQuestID(questID):
        raise NotImplementedError

    @staticmethod
    def isRegularBattleMattersQuest(quest):
        raise NotImplementedError

    @staticmethod
    def isCompensationBattleMattersQuestID(questID):
        raise NotImplementedError

    @staticmethod
    def isCompensationBattleMattersQuest(quest):
        raise NotImplementedError

    @staticmethod
    def isIntermediateBattleMattersQuest(quest):
        raise NotImplementedError

    @staticmethod
    def isIntermediateBattleMattersQuestID(questID):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isPaused(self):
        raise NotImplementedError

    def isFinished(self):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    @property
    def progressWatcher(self):
        raise NotImplementedError

    def hasDelayedRewards(self):
        raise NotImplementedError

    def hasDelayedRewardsInQuest(self, quest):
        raise NotImplementedError

    def isFinalQuest(self, quest):
        raise NotImplementedError

    def getFinalQuest(self):
        raise NotImplementedError

    def getQuestByIdx(self, questIdx):
        raise NotImplementedError

    def getCompletedBattleMattersQuests(self):
        raise NotImplementedError

    def getCompletedBattleMattersQuestsCount(self):
        raise NotImplementedError

    def getNotCompletedBattleMattersQuests(self):
        raise NotImplementedError

    def getQuestsWithDelayedReward(self):
        raise NotImplementedError

    def getRegularBattleMattersQuests(self, filterFunc=None):
        raise NotImplementedError

    def getCompensationBattleMattersQuests(self, filterFunc=None):
        raise NotImplementedError

    def getBattleMattersQuests(self, filterFunc=None):
        raise NotImplementedError

    def hasLinkedIntermediateQuest(self, quest):
        raise NotImplementedError

    def getIntermediateQuests(self):
        raise NotImplementedError

    def getCountBattleMattersQuests(self):
        raise NotImplementedError

    def showAwardView(self, questsData, clientCtx=None):
        raise NotImplementedError

    def getCurrentQuest(self):
        raise NotImplementedError

    def getQuestProgress(self, quest):
        raise NotImplementedError

    def getSelectedVehicle(self):
        raise NotImplementedError

    def hasAccessToken(self):
        raise NotImplementedError

    def getDelayedRewardCurrencyToken(self):
        raise NotImplementedError

    def getDelayedRewardToken(self):
        raise NotImplementedError
