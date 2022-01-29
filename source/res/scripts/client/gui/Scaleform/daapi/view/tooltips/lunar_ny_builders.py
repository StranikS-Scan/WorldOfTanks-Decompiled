# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/lunar_ny_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.lobby.lunar_ny.tooltips.buy_loot_box_tooltip import BuyLootBoxTooltip
from gui.impl.lobby.lunar_ny.tooltips.charm_tooltip import CharmTooltip
from gui.impl.lobby.lunar_ny.tooltips.envelope_tooltip import EnvelopeTooltip
from gui.shared.tooltips import ToolTipBaseData
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import TooltipWindowBuilder
from lunar_ny.lunar_ny_constants import ENVELOPE_ENTITLEMENT_CODE_TO_TYPE, EnvelopeTypes
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (TooltipWindowBuilder(TOOLTIPS_CONSTANTS.LUNAR_NY_CHARM, None, CharmTooltipBuilder(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.LUNAR_NY_ENVELOPE, None, EnvelopeTooltipBuilder(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.SHOP_LUNAR_NY_ENVELOPE, None, ShopEnvelopeTooltipBuilder(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.SHOP_LUNAR_NY_PREREQUISITE, None, ShopPrerequisiteTooltipBuilder(contexts.ToolTipContext(None))))


class CharmTooltipBuilder(ToolTipBaseData):

    def __init__(self, context):
        super(CharmTooltipBuilder, self).__init__(context, TOOLTIPS_CONSTANTS.LUNAR_NY_CHARM)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(CharmTooltip(charmID=args[0]), useDecorator=False)


class EnvelopeTooltipBuilder(ToolTipBaseData):

    def __init__(self, context):
        super(EnvelopeTooltipBuilder, self).__init__(context, TOOLTIPS_CONSTANTS.LUNAR_NY_ENVELOPE)

    def getDisplayableData(self, *args, **kwargs):
        envelopeType = ENVELOPE_ENTITLEMENT_CODE_TO_TYPE.get(args[0] if args else None, EnvelopeTypes.FREE)
        return DecoratedTooltipWindow(EnvelopeTooltip(envelopeType=envelopeType, isInShop=False), useDecorator=False)


class ShopEnvelopeTooltipBuilder(ToolTipBaseData):

    def __init__(self, context):
        super(ShopEnvelopeTooltipBuilder, self).__init__(context, TOOLTIPS_CONSTANTS.SHOP_LUNAR_NY_ENVELOPE)

    def getDisplayableData(self, *args, **kwargs):
        envelopeType = ENVELOPE_ENTITLEMENT_CODE_TO_TYPE.get(args[0], EnvelopeTypes.FREE)
        return DecoratedTooltipWindow(EnvelopeTooltip(envelopeType=envelopeType, isInShop=True), useDecorator=False)


class ShopPrerequisiteTooltipBuilder(ToolTipBaseData):

    def __init__(self, context):
        super(ShopPrerequisiteTooltipBuilder, self).__init__(context, TOOLTIPS_CONSTANTS.SHOP_LUNAR_NY_PREREQUISITE)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(BuyLootBoxTooltip(count=args[1]), useDecorator=False)
