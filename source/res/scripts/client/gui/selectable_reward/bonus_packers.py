# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/selectable_reward/bonus_packers.py
import typing
from gui.battle_pass.battle_pass_helpers import getOfferTokenByGift
from gui.impl.backport import TooltipData
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID, BaseBonusUIPacker
from helpers import dependency
from shared_utils import first
from skeletons.gui.offers import IOffersDataProvider
if typing.TYPE_CHECKING:
    from typing import List, Union
    from account_helpers.offers.events_data import OfferEventData
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
    from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
    from gui.server_events.bonuses import SelectableBonus

class SelectableBonusPacker(BaseBonusUIPacker):
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    @classmethod
    def getValue(cls, bonus):
        offer = cls.__getBonusOffer(bonus)
        if offer is None:
            return bonus.getCount()
        else:
            gift = first(offer.getAllGifts())
            return bonus.getCount() if gift is None else gift.giftCount * bonus.getCount()

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = cls._makeRewardItemModel()
        model.setName(bonus.getName())
        model.setValue(str(cls.getValue(bonus)))
        model.setIcon(bonus.getType())
        model.setBigIcon(bonus.getType())
        return model

    @classmethod
    def _makeRewardItemModel(cls):
        raise NotImplementedError

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getValue().iterkeys():
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=cls._getTooltipSpecialAlias(), specialArgs=[tokenID]))

        return tooltipData

    @classmethod
    def _getTooltipSpecialAlias(cls):
        raise NotImplementedError

    @classmethod
    def _getContentId(cls, bonus):
        return [BACKPORT_TOOLTIP_CONTENT_ID] * len(bonus.getValue().keys())

    @classmethod
    def __getBonusOffer(cls, bonus):
        giftTokenName = first(bonus.getValue().keys())
        return cls.__offersProvider.getOfferByToken(getOfferTokenByGift(giftTokenName))
