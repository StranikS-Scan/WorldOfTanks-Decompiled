# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/yha/yha_bonus_packers.py
import typing
from gui.battle_pass.battle_pass_award import awardsFactory
from gui.impl.gen.view_models.views.lobby.yha.reward_model import RewardModel
from gui.server_events.bonuses import mergeBonuses, splitBonuses
from gui.shared.missions.packers.bonus import CustomizationBonusUIPacker, BonusUIPacker, SimpleBonusUIPacker
from gui.shared.money import Currency
if typing.TYPE_CHECKING:
    from gui.impl.backport import TooltipData
    from gui.server_events.bonuses import SimpleBonus
_CUSTOMIZATION_BONUS = 'customizations'
_BONUSES_ORDER = (_CUSTOMIZATION_BONUS, Currency.CREDITS)

def getBonuses(rewards):
    bonuses = awardsFactory(rewards)
    bonuses = mergeBonuses(bonuses)
    bonuses = splitBonuses(bonuses)
    bonuses.sort(key=_getBonusOrderKey)
    return bonuses


class YHACustomizationsBonusPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, data):
        model = RewardModel()
        model.setName(bonus.getC11nItem(item).itemTypeName)
        model.setCount(item.get('value', 0))
        return model


class YHASimpleBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = RewardModel()
        model.setName(bonus.getName())
        model.setCount(bonus.getValue())
        return model


def getYearHareAffairBonusPacker():
    mapping = {_CUSTOMIZATION_BONUS: YHACustomizationsBonusPacker(),
     Currency.CREDITS: YHASimpleBonusPacker()}
    return BonusUIPacker(mapping)


def packBonusModelAndTooltips(bonuses):
    models = []
    tooltips = []
    packer = getYearHareAffairBonusPacker()
    for bonus in bonuses:
        if not bonus.isShowInGUI():
            continue
        bModels = packer.pack(bonus)
        if not bModels:
            continue
        bTooltips = packer.getToolTip(bonus)
        bContentIds = packer.getContentId(bonus)
        for model, tooltip, contentId in zip(bModels, bTooltips, bContentIds):
            tooltipIdx = len(tooltips)
            model.setTooltipId(tooltipIdx)
            model.setTooltipContentId(contentId)
            models.append(model)
            tooltips.append(tooltip)

    return (models, tooltips)


def _getBonusOrderKey(bonus):
    bonusName = bonus.getName()
    return _BONUSES_ORDER.index(bonusName) if bonusName in _BONUSES_ORDER else len(_BONUSES_ORDER)
