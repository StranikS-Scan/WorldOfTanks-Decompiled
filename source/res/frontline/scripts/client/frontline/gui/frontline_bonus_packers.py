# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/frontline_bonus_packers.py
import typing
from epic_constants import FRONTLINE_BONUSES_ORDER, EPIC_SKILL_TOKEN_NAME
from frontline.gui.bonus import FrontlineSkillBonus
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_reward_model import FrontlineRewardModel, ClaimState
from gui.impl.backport import createTooltipData, TooltipData
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, SimpleBonusUIPacker, BonusUIPacker, GoodiesBonusUIPacker, CrewBookBonusUIPacker, BattlePassPointsBonusPacker
from gui.shared.money import Currency
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus, EpicSelectTokensBonus, GoodiesBonus

def getFrontlineBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'battlePassPoints': FrontlineBattlePassPointsBonusPacker(),
     'epicSelectToken': FrontlineTokenBonusPacker(),
     'goodies': FrontlineGoodiesBonusPacker(),
     'crewBooks': FrontlineCrewBookBonusPacker(),
     Currency.CRYSTAL: FrontlineCrystalBonusPacker(),
     EPIC_SKILL_TOKEN_NAME: FrontlineAbilityTokenPacker()})
    return BonusUIPacker(mapping)


def _keySortOrder(bonus):
    name = bonus.getName()
    return FRONTLINE_BONUSES_ORDER.index(name) if name in FRONTLINE_BONUSES_ORDER else len(FRONTLINE_BONUSES_ORDER)


def packBonusModelAndTooltipData(bonuses, listVM, tooltipData=None):
    packer = getFrontlineBonusPacker()
    listVM.clear()
    bonuses.sort(key=_keySortOrder)
    for bonus in bonuses:
        if bonus.isShowInGUI():
            rewardsVM = packer.pack(bonus)
            rewardsTooltips = packer.getToolTip(bonus)
            rewardsContentIds = packer.getContentId(bonus)
            for idx, rewardModel in enumerate(rewardsVM):
                rewardTooltipData = rewardsTooltips[idx]
                tooltipID = rewardTooltipData.specialAlias if rewardTooltipData.isSpecial else rewardModel.getName()
                rewardModel.setTooltipId(tooltipID)
                rewardModel.setTooltipContentId(str(rewardsContentIds[idx]))
                if tooltipData is not None and tooltipID not in tooltipData:
                    tooltipData[tooltipID] = rewardsTooltips[idx]
                listVM.addViewModel(rewardModel)

    listVM.invalidate()
    return


class FrontlineCrystalBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return FrontlineRewardModel()

    @classmethod
    def _packSingleBonus(cls, bonus, *args):
        model = FrontlineRewardModel()
        cls._packCommon(bonus, model)
        model.setIcon(bonus.getName())
        model.setValue(str(bonus.getValue()))
        model.setClaimState(ClaimState.STATIC)
        return model

    @classmethod
    def getToolTip(cls, bonus):
        return cls._getToolTip(bonus)

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData(bonus.getTooltip())]


class FrontlineTokenBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return FrontlineRewardModel()

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus, **kwargs):
        model = cls._getBonusModel()
        name = bonus.getName()
        model.setName(name)
        model.setType(name)
        claimState = ClaimState.CLAIMABLE if bonus.canClaim() else ClaimState.STATIC
        model.setClaimState(claimState)
        model.setValue(str(bonus.firstOfferCount()))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return [bonus.getTooltip()]


class FrontlineBattlePassPointsBonusPacker(BattlePassPointsBonusPacker):

    @classmethod
    def _getBonusModel(cls):
        return FrontlineRewardModel()

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(FrontlineBattlePassPointsBonusPacker, cls)._packSingleBonus(bonus, label)
        model.setClaimState(ClaimState.STATIC)
        return model


class FrontlineGoodiesBonusPacker(GoodiesBonusUIPacker):

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count, label):
        model = FrontlineRewardModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        model.setIcon(icon)
        model.setLabel(label)
        model.setClaimState(ClaimState.STATIC)
        return model


class FrontlineCrewBookBonusPacker(CrewBookBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return FrontlineRewardModel()

    @classmethod
    def _packSingleBonus(cls, bonus, book, count):
        model = super(FrontlineCrewBookBonusPacker, cls)._packSingleBonus(bonus, book, count)
        model.setClaimState(ClaimState.STATIC)
        return model


class FrontlineAbilityTokenPacker(SimpleBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return FrontlineRewardModel()

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus, *args):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        value = bonus.getValue()
        model.setValue(str(value) if value > 1 else '')
        model.setType(bonus.getName())
        model.setClaimState(ClaimState.STATIC)
        return model
