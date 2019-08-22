# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/battle_royale_rewards.py
from gui.Scaleform.daapi.view.meta.BattleRoyaleAwardsWrapperMeta import BattleRoyaleAwardsWrapperMeta
from gui.battle_royale.constants import DEFAULT_REWARDS_COUNT
from gui.battle_royale.royale_builders import rewards_vos
from gui.battle_royale.royale_formatters import getTitleColumnRewardsFormatter
from gui.server_events.awards_formatters import AWARDS_SIZES
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class BattleRoyaleAwardsWrapper(BattleRoyaleAwardsWrapperMeta):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self):
        super(BattleRoyaleAwardsWrapper, self).__init__()
        self.__iconSize = AWARDS_SIZES.SMALL
        self.__bonusFormatter = getTitleColumnRewardsFormatter(DEFAULT_REWARDS_COUNT)

    def onRequestData(self, iconSizeID, rewardsCount):
        self.__iconSize = iconSizeID
        self.__bonusFormatter.setMaxRewardsCount(int(rewardsCount))
        self.__onUpdate()

    def _populate(self):
        super(BattleRoyaleAwardsWrapper, self)._populate()
        self.__battleRoyaleController.onUpdated += self.__onUpdate

    def _dispose(self):
        self.__bonusFormatter = None
        self.__battleRoyaleController.onUpdated -= self.__onUpdate
        super(BattleRoyaleAwardsWrapper, self)._dispose()
        return

    def __getRewardsData(self):
        rewards = []
        maxTitleID = self.__battleRoyaleController.getMaxTitle().title
        minPossibleTitleID = self.__battleRoyaleController.getMinPossibleTitle()
        maxPossibleTitleID = self.__battleRoyaleController.getMaxPossibleTitle()
        for titleID in range(minPossibleTitleID + 1, maxPossibleTitleID + 1):
            title = self.__battleRoyaleController.getTitle(titleID)
            rewards.append(rewards_vos.getTitleRewardsVO(title, self.__getTitleRewards(title), maxTitleID))

        return rewards

    def __getTitleRewards(self, title):
        quest = title.getQuest()
        return self.__bonusFormatter.getFormattedBonuses(quest.getBonuses(), self.__iconSize) if quest else []

    def __onUpdate(self):
        self.as_setRewardsS(self.__getRewardsData())
