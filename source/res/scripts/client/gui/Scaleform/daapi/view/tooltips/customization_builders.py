# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/customization_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.customization.tooltips import ElementTooltip
from gui.Scaleform.daapi.view.lobby.customization.tooltips import ElementIconTooltip
from gui.Scaleform.daapi.view.lobby.customization.tooltips import ElementAwardTooltip
from gui.Scaleform.daapi.view.lobby.customization.tooltips import ElementPurchaseTooltip
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
from gui.Scaleform.daapi.view.lobby.customization.tooltips.element import NonHistoricTooltip, PopoverTooltip, MultiElementAwardTooltip, FantasticalTooltip, ChainedTooltip, ShortMultiElementAwardTooltip
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, ElementTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_NONHISTORIC_ITEM, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, NonHistoricTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_FANTASTICAL_ITEM, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, FantasticalTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_CHAINED_ITEM, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, ChainedTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_POPOVER_ITEM, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, PopoverTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_ICON, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, ElementIconTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, ElementAwardTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.COLLAPSE_CUSTOMIZATION_ITEM_AWARD, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, MultiElementAwardTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SHORT_COLLAPSE_CUSTOMIZATION_ITEM_AWARD, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, ShortMultiElementAwardTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_PURCHASE, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, ElementPurchaseTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SHOP_CUSTOMIZATION_ITEM, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, ElementTooltip(contexts.ShopCustomizationContext())))
