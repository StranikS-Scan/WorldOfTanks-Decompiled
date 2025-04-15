# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/selectable_reward/common.py
import logging
import typing
from comp7.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_TOOLTIPS
from comp7.gui.selectable_reward.constants import Features
from gui.impl.backport import TooltipData
from gui.selectable_reward.common import SelectableRewardManager
from helpers import dependency
from skeletons.gui.offers import IOffersDataProvider
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SelectableBonus
    from typing import Dict
_logger = logging.getLogger(__name__)

class Comp7SelectableRewardManager(SelectableRewardManager):
    _FEATURE = Features.COMP7
    _offersDataProvider = dependency.descriptor(IOffersDataProvider)

    @classmethod
    def getTabTooltipData(cls, selectableBonus):
        tokenID = selectableBonus.getValue().keys()[0]
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=COMP7_TOOLTIPS.COMP7_SELECTABLE_REWARD, specialArgs=(tokenID,)) if cls.isFeatureReward(tokenID) else None

    @classmethod
    def getGiftCount(cls, bonus):
        return sum(cls.getGiftCountPerToken(bonus).itervalues())

    @classmethod
    def getGiftCountPerToken(cls, bonus):
        isComp7OfferToken = cls.isFeatureReward
        tokens = ((token, v.get('count', 0)) for token, v in bonus.getValue().iteritems() if isComp7OfferToken(token))
        return {token:cls.__getTokenGiftCount(token, count) for token, count in tokens}

    @classmethod
    def getBonusOfferToken(cls, bonus):
        return cls._getBonusOfferToken(bonus)

    @classmethod
    def __getTokenGiftCount(cls, token, count):
        token = cls._offersDataProvider.getOfferByToken(token)
        return token.giftTokenCount * count if token is not None else count
