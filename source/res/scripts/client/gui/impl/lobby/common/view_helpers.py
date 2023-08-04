# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/view_helpers.py
import typing
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
    from gui.server_events.bonuses import SimpleBonus
    from gui.shared.missions.packers.bonus import BonusUIPacker

def packBonusModelAndTooltipData(bonuses, bonusModelsList, tooltipData=None, packer=None, startIndex=0):
    packer = packer or getDefaultBonusPacker()
    tooltipIndex = 0 if tooltipData is None else len(tooltipData)
    for bonus in (b for b in bonuses if b.isShowInGUI()):
        bonusList = packer.pack(bonus)
        withTooltips = bonusList and tooltipData is not None
        bTooltipList = packer.getToolTip(bonus) if withTooltips else []
        bContentIdList = packer.getContentId(bonus) if withTooltips else []
        for bIndex, bModel in enumerate(bonusList):
            bModel.setIndex(bIndex + startIndex)
            tooltipIndex = _packBonusTooltip(bModel, bIndex, bTooltipList, bContentIdList, tooltipData, tooltipIndex)
            bonusModelsList.addViewModel(bModel)

    return


def _packBonusTooltip(bonusModel, bonusIndex, bonusTooltipList, bonusContentIdList, tooltipData, tooltipIndex):
    if tooltipData is None or not bonusTooltipList and not bonusContentIdList:
        return tooltipIndex
    else:
        tooltipIdx = str(tooltipIndex)
        bonusModel.setTooltipId(tooltipIdx)
        if bonusTooltipList:
            tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
        if bonusContentIdList:
            bonusModel.setTooltipContentId(str(bonusContentIdList[bonusIndex]))
        return tooltipIndex + 1
