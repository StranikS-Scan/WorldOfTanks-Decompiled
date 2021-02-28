# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/state_machine/state_machine_helpers.py
import logging
import typing
from battle_pass_common import BattlePassState, BATTLE_PASS_OFFER_TOKEN_PREFIX, BATTLE_PASS_TOKEN_3D_STYLE, BattlePassRewardReason, BattlePassConsts
from gui.battle_pass.battle_pass_helpers import getNotChosen3DStylesCount, getStyleInfoForChapter, getOfferTokenByGift
from gui.impl.pub.notification_commands import NotificationEvent, EventNotificationCommand
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def isProgressionComplete(_, battlePass=None):
    isCompleteState = battlePass.getState() == BattlePassState.COMPLETED
    isAllChosen = battlePass.getNotChosenRewardCount() == 0
    isAllStyles = getNotChosen3DStylesCount(battlePass=battlePass) == 0
    return isCompleteState and isAllChosen and isAllStyles


@dependency.replace_none_kwargs(battlePass=IBattlePassController, offers=IOffersDataProvider)
def separateRewards(rewards, battlePass=None, offers=None):
    rewardsToChoose = []
    styleTokens = []
    chosenStyle = None
    defaultRewards = rewards[:]
    blocksToRemove = []
    for index, rewardBlock in enumerate(defaultRewards):
        if 'tokens' in rewardBlock:
            for tokenID in rewardBlock['tokens'].iterkeys():
                if tokenID.startswith(BATTLE_PASS_OFFER_TOKEN_PREFIX) and battlePass.isOfferEnabled() and offers.getOfferByToken(getOfferTokenByGift(tokenID)) is not None:
                    level = int(tokenID.split(':')[-1])
                    if battlePass.isRareLevel(level):
                        rewardsToChoose.append(tokenID)
                if tokenID.startswith(BATTLE_PASS_TOKEN_3D_STYLE):
                    styleTokens.append(tokenID)
                    chapter = int(tokenID.split(':')[3])
                    intCD, _ = getStyleInfoForChapter(chapter)
                    if intCD is not None:
                        chosenStyle = chapter

        for tokenID in rewardsToChoose:
            rewardBlock.get('tokens', {}).pop(tokenID, None)

        for tokenID in styleTokens:
            rewardBlock.get('tokens', {}).pop(tokenID, None)

        if not rewardBlock.get('tokens', {}):
            rewardBlock.pop('tokens', None)
        if not rewardBlock:
            blocksToRemove.append(index)
        styleTokens = []

    for index in sorted(blocksToRemove, reverse=True):
        defaultRewards.pop(index)

    rewardsToChoose.sort(key=lambda x: (int(x.split(':')[-1]), x.split(':')[-2]))
    return (rewardsToChoose, defaultRewards, chosenStyle)


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def packStartEvent(rewards, data, battlePass=None):
    if rewards is None or data is None:
        return
    else:
        reason = data['reason']
        if reason in (BattlePassRewardReason.SELECT_STYLE,):
            return
        if 'newLevel' not in data:
            return
        isPremiumPurchase = reason in BattlePassRewardReason.PURCHASE_REASONS
        newLevel = data['newLevel']
        isRareLevel = battlePass.isRareLevel(newLevel)
        isFinalLevel = battlePass.isFinalLevel(newLevel)
        rewards.pop('entitlements', None)
        return None if not isPremiumPurchase and not isRareLevel and not isFinalLevel or not rewards else EventNotificationCommand(NotificationEvent(method=battlePass.getRewardLogic().startRewardFlow, rewards=[rewards], data=data))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getStylesToChooseUntilChapter(chapter, itemsCache=None):
    chosenItems = itemsCache.items.battlePass.getChosenItems()
    fromChapter = max(chosenItems) + 1 if chosenItems else BattlePassConsts.MINIMAL_CHAPTER_NUMBER
    return range(fromChapter, chapter)


def packToken(tokenID):
    return {'tokens': {tokenID: {'count': 1,
                          'expires': {'after': 1}}}}
