# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/bonuses.py
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.server_events.bonuses import _initFromTree
from gui.shared.missions.packers.bonus import BaseBonusUIPacker
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from shared_utils import first
from skeletons.gui.offers import IOffersDataProvider
BACKPORT_TOOLTIP_CONTENT_ID = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class SelectBonusPacker(BaseBonusUIPacker):
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    @classmethod
    def _pack(cls, bonus):
        return [ cls._packSingleBonus(bonus) for _ in range(bonus.getCount()) ]

    @classmethod
    def _packSingleBonus(cls, bonus):
        from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
        model = RewardItemModel()
        bonusType = bonus.getType()
        model.setName(bonus.getName())
        model.setValue(str(cls.getValue(bonus)))
        model.setIcon(bonusType)
        model.setBigIcon(bonusType)
        model.setUserName(backport.text(R.strings.seniority_awards.selectBonus.dyn(bonusType)()))
        model.setLabel(backport.text(R.strings.seniority_awards.selectBonus.dyn(bonusType)()))
        return model

    @classmethod
    def getValue(cls, bonus):
        pass

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        bonusType = bonus.getType()
        userName = backport.text(R.strings.seniority_awards.offer.tooltip.title.dyn(bonusType)())
        description = backport.text(R.strings.seniority_awards.offer.tooltip.description.dyn(bonusType)())
        for _ in range(bonus.getCount()):
            for _ in bonus.getTokens().iterkeys():
                tooltipData.append(createTooltipData(makeTooltip(userName, description)))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for _ in range(bonus.getCount()):
            for _ in bonus.getTokens().iterkeys():
                result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result


class SACompensationBonusPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [ cls._packSingleBonus(bonus) for _ in range(bonus.getCount()) ]

    @classmethod
    def _packSingleBonus(cls, bonus):
        from gui.impl.gen.view_models.views.lobby.seniority_awards.main_reward_bonus_model import MainRewardBonusModel
        model = MainRewardBonusModel()
        bonusType = bonus.getType()
        model.setName(Currency.CREDITS)
        model.setValue(str(bonus.getAmount()))
        model.setIsCompensation(True)
        model.setCompensatedBonus('vehicles')
        model.setIcon(bonusType)
        model.setBigIcon(bonusType)
        model.setTooltipContentId(str(R.views.lobby.seniority_awards.tooltips.SeniorityAwardsCompensationTooltip()))
        model.setLabel(backport.text(R.strings.seniority_awards.compensationToken.dyn(bonusType)()))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        prevBonus = first(_initFromTree(('tokens', 'default'), 'tokens', {'offer:seniority:vehicle_10_gift:1': {'count': bonus.getCount()}}))
        newBonus = first(_initFromTree(('credits',), 'credits', bonus.getAmount()))
        return [ createTooltipData(isSpecial=True, specialArgs=[prevBonus, newBonus]) for _ in range(bonus.getCount()) ]

    @classmethod
    def _getContentId(cls, bonus):
        return [ R.views.lobby.seniority_awards.tooltips.SeniorityAwardsCompensationTooltip() for _ in range(bonus.getCount()) ]
