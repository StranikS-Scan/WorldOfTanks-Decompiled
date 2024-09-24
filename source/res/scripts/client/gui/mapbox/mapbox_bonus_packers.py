# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/mapbox/mapbox_bonus_packers.py
import typing
from gui.impl.auxiliary.rewards_helper import BlueprintBonusTypes
from gui.shared.missions.packers.bonus import BonusUIPacker, BlueprintBonusUIPacker, getDefaultBonusPackersMap
from shared_utils import first
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array

def getMapboxBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({BlueprintBonusTypes.BLUEPRINTS: _MapboxBlueprintBonusUIPacker,
     BlueprintBonusTypes.FINAL_BLUEPRINTS: _MapboxBlueprintBonusUIPacker,
     BlueprintBonusTypes.BLUEPRINTS_ANY: _MapboxBlueprintBonusUIPacker})
    return BonusUIPacker(mapping)


def packMapboxRewardModelAndTooltip(rewardsList, bonusList, packer, numBattles, tooltipsList=None):
    groupStartIdx = len(tooltipsList)
    groupIdx = 0
    for bonusItem in bonusList:
        totalIdx = groupStartIdx + groupIdx
        tooltipsData = packer.getToolTip(bonusItem)
        for bonusIdx, bonusModel in enumerate(packer.pack(bonusItem)):
            bonusModel.setTooltipId(str(totalIdx + bonusIdx))
            bonusModel.setIndex(groupIdx)
            if tooltipsList is not None:
                tooltipsList.append(tooltipsData[bonusIdx])
            groupIdx += 1
            rewardsList.addViewModel(bonusModel)

    return


class _MapboxBlueprintBonusUIPacker(BlueprintBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        models = super(_MapboxBlueprintBonusUIPacker, cls)._pack(bonus)
        model = first(models)
        if model:
            model.setLabel(bonus.getLabel())
        return models
