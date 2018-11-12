# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/customization_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.customization.tooltips import ElementTooltip
from gui.Scaleform.daapi.view.lobby.customization.tooltips import ElementIconTooltip
from gui.Scaleform.daapi.view.lobby.customization.tooltips import ElementAwardTooltip
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
from gui.Scaleform.daapi.view.lobby.customization.tooltips.element import NonHistoricTooltip
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, ElementTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_HISTORIC_ITEM, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, NonHistoricTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_ICON, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, ElementIconTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, ElementAwardTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, ElementTooltip(contexts.Shop20CustomizationContext())))
