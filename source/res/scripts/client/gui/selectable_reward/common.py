# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/selectable_reward/common.py
import logging
import typing
from adisp import process
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import TooltipData
from gui.selectable_reward.constants import FEATURE_TO_PREFIX, Features
from gui.server_events.bonuses import SelectableBonus
from gui.shared.gui_items.processors import makeError
from gui.shared.gui_items.processors.offers import ReceiveMultipleOfferGiftsProcessor, ReceiveOfferGiftProcessor, BattleMattersOfferProcessor
from helpers import dependency
from shared_utils import first
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, List, Tuple
    from account_helpers.offers.events_data import OfferEventData
    from gui.SystemMessages import ResultMsg
_logger = logging.getLogger(__name__)

class SelectableRewardManager(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __offersDataProvider = dependency.descriptor(IOffersDataProvider)
    _FEATURE = None
    _SINGLE_GIFT_PROCESSOR = ReceiveOfferGiftProcessor
    _MULTIPLE_GIFT_PROCESSOR = ReceiveMultipleOfferGiftsProcessor

    @classmethod
    def isFeatureReward(cls, tokenID):
        return tokenID.startswith(FEATURE_TO_PREFIX.get(cls._FEATURE))

    @classmethod
    @process
    def chooseReward(cls, bonus, giftID, callback):
        offer = cls._getBonusOffer(bonus)
        result = yield cls._SINGLE_GIFT_PROCESSOR(offer.id, giftID, skipConfirm=True).request()
        callback(result)

    @classmethod
    @process
    def chooseRewards(cls, bonusChoices, callback):
        choices = {}
        for bonus, giftIDs in bonusChoices:
            offer = cls._getBonusOffer(bonus)
            if offer is None:
                _logger.error('Offer for %s is None!', bonus)
                callback(makeError())
                return
            choices.setdefault(offer.id, [])
            choices[offer.id].extend(giftIDs)

        result = yield cls._MULTIPLE_GIFT_PROCESSOR(choices).request()
        callback(result)
        return

    @classmethod
    def getBonusOptions(cls, bonus):
        if not isinstance(bonus, SelectableBonus):
            return {}
        offer = cls._getBonusOffer(bonus)
        return {gift.id:{'option': gift.bonus,
         'count': gift.giftCount,
         'limit': gift.limit()} for gift in offer.getAllGifts()}

    @classmethod
    def getBonusReceivedOptions(cls, bonus):
        if not isinstance(bonus, SelectableBonus):
            return []
        else:
            offer = cls._getBonusOffer(bonus)
            result = []
            receivedGifts = cls.__offersDataProvider.getReceivedGifts(offer.id)
            for giftId, count in receivedGifts.iteritems():
                if count > 0:
                    gift = offer.getGift(giftId)
                    if gift is not None:
                        result.append((gift.bonus, count))

            return result

    @classmethod
    def getAvailableSelectableBonuses(cls, condition=None):

        def isAvailableBonus(tokenID):
            offer = SelectableRewardManager.__offersDataProvider.getOfferByToken(tokenID)
            return offer is not None and offer.isOfferAvailable

        return cls.getSelectableBonuses(lambda tokenID: isAvailableBonus(tokenID) and (not callable(condition) or condition(tokenID)))

    @classmethod
    def getSelectableBonuses(cls, condition=None):
        return [ SelectableBonus({tokenID: cls._packTokenData(token)}) for tokenID, token in cls.__itemsCache.items.tokens.getTokens().iteritems() if cls.isFeatureReward(tokenID) and (not callable(condition) or condition(tokenID)) ]

    @classmethod
    def getRemainedChoices(cls, bonus):
        offer = cls._getBonusOffer(bonus)
        return 0 if offer is None else offer.availableTokens

    @classmethod
    def getRemainedChoicesForFeature(cls):
        result = 0
        for token in cls.__getFeatureTokens():
            offer = cls.__offersDataProvider.getOfferByToken(token)
            if offer is not None:
                result += offer.availableTokens

        return result

    @classmethod
    def getTabTooltipData(cls, selectableBonus):
        return None

    @classmethod
    def _getBonusOffer(cls, bonus):
        return cls.__offersDataProvider.getOfferByToken(cls._getBonusOfferToken(bonus))

    @classmethod
    def _getBonusOfferToken(cls, bonus):
        tokenID = first(bonus.getValue().keys())
        return tokenID.replace('_gift', '')

    @classmethod
    def _packTokenData(cls, token):
        expiresAfter, count = token
        return {'count': count,
         'expires': {'after': expiresAfter},
         'limit': 0}

    @classmethod
    def __getFeatureTokens(cls):
        return {tokenID:token for tokenID, token in cls.__itemsCache.items.tokens.getTokens().iteritems() if cls.isFeatureReward(tokenID)}


class BattlePassSelectableRewardManager(SelectableRewardManager):
    _FEATURE = Features.BATTLE_PASS

    @classmethod
    def getTabTooltipData(cls, selectableBonus):
        tokenID = selectableBonus.getValue().keys()[0]
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_PASS_GIFT_TOKEN, specialArgs=[_getGiftTokenFromOffer(tokenID), True]) if cls.isFeatureReward(tokenID) else None


class RankedSelectableRewardManager(SelectableRewardManager):
    _FEATURE = Features.RANKED

    @classmethod
    def getTabTooltipData(cls, selectableBonus):
        tokenID = selectableBonus.getValue().keys()[0]
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.RANKED_BATTLES_SELECTABLE_REWARD, specialArgs=[]) if cls.isFeatureReward(tokenID) else None


class EpicSelectableRewardManager(SelectableRewardManager):
    _FEATURE = Features.EPIC

    @classmethod
    def getTabTooltipData(cls, selectableBonus):
        tokenID = selectableBonus.getValue().keys()[0]
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EPIC_BATTLE_INSTRUCTION_TOOLTIP, specialArgs=[_getGiftTokenFromOffer(tokenID)]) if cls.isFeatureReward(tokenID) else None


class BattleMattersSelectableRewardManager(SelectableRewardManager):
    _battleMattersController = dependency.descriptor(IBattleMattersController)
    _SINGLE_GIFT_PROCESSOR = BattleMattersOfferProcessor

    @classmethod
    def isFeatureReward(cls, tokenID):
        return tokenID == cls._battleMattersController.getDelayedRewardToken()

    @classmethod
    def getTabTooltipData(cls, selectableBonus):
        return None

    @classmethod
    def getBonusOffer(cls, bonus):
        return cls._getBonusOffer(bonus)


def _getGiftTokenFromOffer(offerToken):
    splitToken = offerToken.split(':')
    splitToken[2] += '_gift'
    return ':'.join(splitToken)
