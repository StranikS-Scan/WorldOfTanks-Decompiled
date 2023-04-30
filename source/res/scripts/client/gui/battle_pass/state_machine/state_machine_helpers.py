# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/state_machine/state_machine_helpers.py
import logging
import typing
from battle_pass_common import BATTLE_PASS_OFFER_TOKEN_PREFIX, BATTLE_PASS_TOKEN_3D_STYLE, BattlePassConsts, BattlePassRewardReason, BattlePassState, getBattlePassPassEntitlementName, getBattlePassShopEntitlementName
from gui.battle_pass.battle_pass_helpers import getOfferTokenByGift, getStyleInfoForChapter
from gui.impl.gen import R
from gui.impl.pub.notification_commands import EventNotificationCommand, NotificationEvent
from gui.server_events.events_dispatcher import showMissionsBattlePass
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.offers import IOffersDataProvider
if typing.TYPE_CHECKING:
    from account_helpers.offers.events_data import OfferEventData
    from typing import Any, Callable, Dict, List, Optional
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def isProgressionComplete(_, battlePass=None):
    isCompleteState = battlePass.getState() == BattlePassState.COMPLETED
    isAllChosen = battlePass.getNotChosenRewardCount() == 0
    isAllChaptersBought = all((battlePass.isBought(chapterID=chapter) for chapter, _ in enumerate(battlePass.getChapterConfig(), BattlePassConsts.MINIMAL_CHAPTER_NUMBER)))
    return isCompleteState and isAllChosen and isAllChaptersBought


@dependency.replace_none_kwargs(battlePass=IBattlePassController, offers=IOffersDataProvider)
def separateRewards(rewards, battlePass=None, offers=None):
    rewardsToChoose = []
    styleTokens = []
    chosenStyle = None
    defaultRewards = rewards[:]
    blocksToRemove = []
    hasRareRewardToChoose = False
    if battlePass.isOfferEnabled():
        for reward in defaultRewards:
            for tokenID in reward.get('tokens', {}).iterkeys():
                if _isRewardChoiceToken(tokenID, offers=offers):
                    splitToken = tokenID.split(':')
                    if battlePass.isRareLevel(chapterID=int(splitToken[-2]), level=int(splitToken[-1])):
                        hasRareRewardToChoose = True
                        break

    for index, rewardBlock in enumerate(defaultRewards):
        if 'tokens' in rewardBlock:
            for tokenID in rewardBlock['tokens'].iterkeys():
                if hasRareRewardToChoose and _isRewardChoiceToken(tokenID, offers=offers):
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
def packStartEvent(rewards, data, packageRewards, eventMethod, battlePass=None):
    if rewards is None or data is None:
        return
    else:
        reason = data['reason']
        if reason in (BattlePassRewardReason.STYLE_UPGRADE,):
            return
        if not ('newLevel' in data and 'chapter' in data):
            return
        isPremiumPurchase = reason in BattlePassRewardReason.PURCHASE_REASONS
        newLevel = data['newLevel']
        chapter = data['chapter']
        prevLevel = data['prevLevel']
        isFinalLevel = battlePass.isFinalLevel(chapter, newLevel)
        isRareLevel = False
        if newLevel is not None:
            for level in xrange(prevLevel + 1, newLevel + 1):
                if battlePass.isRareLevel(chapter, level):
                    isRareLevel = True
                    break

        if 'entitlements' in rewards:
            rewards['entitlements'].pop(getBattlePassPassEntitlementName(battlePass.getSeasonID()), None)
            rewards['entitlements'].pop(getBattlePassShopEntitlementName(battlePass.getSeasonID()), None)
            if not rewards['entitlements']:
                rewards.pop('entitlements')
        return None if not isPremiumPurchase and not isRareLevel and not isFinalLevel or not rewards else EventNotificationCommand(NotificationEvent(method=eventMethod, rewards=[rewards], data=data, packageRewards=packageRewards))


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def multipleBattlePassPurchasedEventMethod(rewards, data, packageRewards, battlePass=None):
    if battlePass.isDisabled():
        return
    else:
        chapterID = battlePass.getCurrentChapterID()
        showMissionsBattlePass(R.views.lobby.battle_pass.BattlePassProgressionsView() if chapterID else None, chapterID)
        battlePass.getRewardLogic().startRewardFlow(rewards, data, packageRewards)
        return


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def defaultEventMethod(rewards, data, packageRewards, battlePass=None):
    battlePass.getRewardLogic().startRewardFlow(rewards, data, packageRewards)


def packToken(tokenID):
    return {'tokens': {tokenID: {'count': 1,
                          'expires': {'after': 1}}}}


@dependency.replace_none_kwargs(offers=IOffersDataProvider)
def processRewardsToChoose(rewardsToChoose, offers=None):
    rewards = {}
    for token in rewardsToChoose:
        offer = _getOfferByGiftToken(token, offers=offers)
        if offer is not None:
            rewards[token] = not offer.availableTokens

    return rewards


@dependency.replace_none_kwargs(offers=IOffersDataProvider)
def _getOfferByGiftToken(token, offers=None):
    return offers.getOfferByToken(getOfferTokenByGift(token))


@dependency.replace_none_kwargs(offers=IOffersDataProvider)
def _isRewardChoiceToken(token, offers=None):
    return token.startswith(BATTLE_PASS_OFFER_TOKEN_PREFIX) and _getOfferByGiftToken(token, offers=offers) is not None
