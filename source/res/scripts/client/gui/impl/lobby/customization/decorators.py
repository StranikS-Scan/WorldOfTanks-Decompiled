# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/decorators.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData
from gui.shared.gui_items.customization import CustomizationTooltipContext

def sharedCustomizationTooltipData(cls):

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltip')
        if not tooltipId:
            return
        else:
            itemTooltipIDs = (TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
             TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_ICON,
             TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD,
             TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_PURCHASE)
            if tooltipId in itemTooltipIDs:
                args = CustomizationTooltipContext(itemCD=int(event.getArgument('intCD')), showInventoryBlock=event.getArgument('showInventoryBlock'), level=int(event.getArgument('progressionLevel')))
            else:
                args = None
            return createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=args)

    cls.getTooltipData = getTooltipData
    return cls
