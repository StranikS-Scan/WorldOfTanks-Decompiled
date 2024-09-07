# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/selectable_reward/selectable_reward_manager.py
import typing
from helpers import dependency
from gui.selectable_reward.common import SelectableRewardManager
from gui.server_events.bonuses import SelectableBonus
from shared_utils import first
from skeletons.gui.game_control import IWinbackController
from skeletons.gui.server_events import IEventsCache
from winback.gui.shared.gui_items.processors.offer import WinbackMultipleOfferProcessor
from winback.gui.impl.lobby.views.winback_bonuses import WinbackSelectableBonus
from winback.gui.impl.lobby.winback_helpers import RewardName, TOKEN_TO_REWARD_MAPPING, getLevelFromSelectableToken
if typing.TYPE_CHECKING:
    from typing import Optional, Any, Dict
    from gui.server_events.event_items import Quest
    from gui.server_events.bonuses import SimpleBonus
    from account_helpers.offers.events_data import OfferGift

class WinbackSelectableRewardManager(SelectableRewardManager):
    _eventsCache = dependency.descriptor(IEventsCache)
    _winbackController = dependency.descriptor(IWinbackController)
    _MULTIPLE_GIFT_PROCESSOR = WinbackMultipleOfferProcessor

    @classmethod
    def isFeatureReward(cls, tokenID):
        return cls._winbackController.isWinbackOfferToken(tokenID)

    @classmethod
    def getRawBonusOptions(cls, bonus):
        if not isinstance(bonus, SelectableBonus):
            return {}
        offer = cls._getBonusOffer(bonus)
        return {gift.id:{'option': gift.rawBonuses,
         'count': gift.giftCount,
         'limit': gift.limit()} for gift in offer.getAllGifts()}

    @classmethod
    def getFirstOfferGift(cls, bonus):
        if not isinstance(bonus, SelectableBonus):
            return None
        else:
            offer = cls._getBonusOffer(bonus)
            return offer.getFirstGift() if offer is not None else None

    @classmethod
    def getBonusOffer(cls, bonus):
        return cls._getBonusOffer(bonus)

    @classmethod
    def isAvailableSelectableBonus(cls, bonus):
        if not isinstance(bonus, SelectableBonus):
            return False
        else:
            offer = cls._getBonusOffer(bonus)
            return False if offer is None else offer.isOfferAvailable

    @classmethod
    def createBonusFromId(cls, tokenID):
        token = cls._itemsCache.items.tokens.getToken(tokenID)
        if token is None:
            return
        else:
            return cls.createCompensationBonusFromOffer(tokenID) if cls.isOfferCompensated(tokenID) else cls._createSelectableBonus(tokenID, token)

    @staticmethod
    def getSelectableBonusName(tokenID):
        offerType = tokenID.split(':')[2]
        return TOKEN_TO_REWARD_MAPPING.get(offerType)

    @classmethod
    def _createSelectableBonus(cls, tokenID, token):
        bonusName = cls.getSelectableBonusName(tokenID)
        if bonusName is None:
            return
        else:
            data = cls._packTokenData(token)
            level = int(getLevelFromSelectableToken(tokenID))
            data.update({'level': level})
            return WinbackSelectableBonus(bonusName, {tokenID: data})

    @classmethod
    def isOfferCompensated(cls, tokenID):
        compensationTokenID = tokenID + '_compensation'
        return cls._itemsCache.items.tokens.getTokenCount(compensationTokenID) > 0

    @classmethod
    def createCompensationBonusFromOffer(cls, tokenID):
        questId = tokenID.replace('offer:', '').replace(':', '_') + '_compensation'
        quest = first(cls._eventsCache.getAllQuests(lambda q: q.getID() == questId).values())
        supportedBonus = 'credits'
        ctx = {'level': getLevelFromSelectableToken(tokenID),
         'isDiscount': cls.getSelectableBonusName(tokenID) == RewardName.SELECTABLE_VEHICLE_DISCOUNT.value}
        return first(quest.getBonuses(isCompensation=True, bonusName=supportedBonus, ctx=ctx)) if quest else None
