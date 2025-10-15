# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/bonus_packer.py
from gui.shared.missions.packers.bonus import BaseBonusUIPacker
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData as packBonusModelAndTooltipDataBase, getBattlePassBonusPacker as getBaseBonusPacker

def getPortalBonusPacker():
    packer = getBaseBonusPacker()
    packer.getPackers().update({'credits': PortalCreditsBonusUIPacker()})
    return packer


def packBonusModelAndTooltipData(bonuses, bonusModelsList, tooltipData=None, packer=None):
    if packer is None:
        packer = getPortalBonusPacker()
    packBonusModelAndTooltipDataBase(bonuses, bonusModelsList, tooltipData, packer)
    return


class PortalCreditsBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = RewardItemModel()
        cls._packCommon(bonus, model)
        model.setIcon(bonus.getName())
        model.setValue(str(bonus.getValue()))
        model.setBigIcon(bonus.getName())
        return model
