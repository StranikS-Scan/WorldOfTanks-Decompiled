# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/__init__.py
from gui.impl.lobby.common.view_helpers import _packBonusTooltip

def cosmicPackBonusModelAndTooltipData(bonuses, bonusModelsList, tooltipData, packer, startIndex=0, tooltipIndex=0):
    for bonus in (b for b in bonuses if b.isShowInGUI()):
        bonusList = packer.pack(bonus)
        withTooltips = bonusList and tooltipData is not None
        bTooltipList = packer.getToolTip(bonus) if withTooltips else []
        bContentIdList = packer.getContentId(bonus) if withTooltips else []
        for bIndex, bModel in enumerate(bonusList):
            bModel.setIndex(bIndex + startIndex)
            if withTooltips:
                tooltipIndex = _packBonusTooltip(bModel, bIndex, bTooltipList, bContentIdList, tooltipData, tooltipIndex)
            bonusModelsList.addViewModel(bModel)

    return
