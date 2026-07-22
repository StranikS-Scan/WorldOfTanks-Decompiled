# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/Scaleform/daapi/view/tooltips/lobby_builders.py
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.shared.tooltips import ToolTipBaseData
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import TooltipWindowBuilder
from mt_birthday.gui.impl.lobby.tooltips.disable_player_tooltip import DisablePlayerTooltip
from mt_birthday.gui.impl.lobby.tooltips.golden_ticket_tooltip import GoldTicketTooltip
from mt_birthday.gui.impl.lobby.tooltips.post_stamp_tooltip import PostStampTooltip
from mt_birthday.gui.impl.lobby.tooltips.entry_point_cgf_tooltip import EntryPointCgfTooltip
from mt_birthday.gui.impl.lobby.tooltips.economy_bonus_tooltip import EconomyBonusTooltip
__all__ = ('getTooltipBuilders', 'BirthdayEconomyBonusTooltipContentWindowData')

def getTooltipBuilders():
    return (TooltipWindowBuilder(TOOLTIPS_CONSTANTS.BIRTHDAY_GIFT_SYSTEM_POSTMARK, None, GiftSystemPostMarkTooltipContentWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.BIRTHDAY_ENTRY_POINT, None, BirthdayEntryPointTooltipContentWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.BIRTHDAY_GOLDEN_TICKET, None, BirthdayGoldenTicketTooltipContentWindowData(contexts.ToolTipContext(None))),
     EconomyBonusContentTooltipBuilder(TOOLTIPS_CONSTANTS.ECONOMY_BONUS_TOOLTIP, None),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.BIRTHDAY_GIFT_SYSTEM_DISABLED_PLAYER, None, BirthdayDisabledPlayerTooltipContentWindowData(contexts.ToolTipContext(None))))


class GiftSystemPostMarkTooltipContentWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(GiftSystemPostMarkTooltipContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.BIRTHDAY_GIFT_SYSTEM_POSTMARK)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(PostStampTooltip(), useDecorator=False)


class BirthdayEntryPointTooltipContentWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(BirthdayEntryPointTooltipContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.BIRTHDAY_ENTRY_POINT)

    def getDisplayableData(self, objectName=None, *args, **kwargs):
        return DecoratedTooltipWindow(EntryPointCgfTooltip(objectName), useDecorator=False)


class BirthdayGoldenTicketTooltipContentWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(BirthdayGoldenTicketTooltipContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.BIRTHDAY_GOLDEN_TICKET)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(GoldTicketTooltip(), useDecorator=False)


class BirthdayEconomyBonusTooltipContentWindowData(ToolTipBaseData):

    def __init__(self, context, tooltipType=TOOLTIPS_CONSTANTS.ECONOMY_BONUS_TOOLTIP):
        super(BirthdayEconomyBonusTooltipContentWindowData, self).__init__(context, tooltipType)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(EconomyBonusTooltip(), useDecorator=False)


class BirthdayDisabledPlayerTooltipContentWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(BirthdayDisabledPlayerTooltipContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.BIRTHDAY_GIFT_SYSTEM_DISABLED_PLAYER)

    def getDisplayableData(self, playerID, *args, **kwargs):
        return DecoratedTooltipWindow(DisablePlayerTooltip(int(playerID)), useDecorator=False)


class EconomyBonusContentTooltipBuilder(TooltipWindowBuilder):
    __tooltipProvider = None

    def __init__(self, tooltipType, linkage):
        provider = self.__tooltipProvider or ToolTipBaseData
        super(EconomyBonusContentTooltipBuilder, self).__init__(tooltipType, linkage, provider(contexts.ToolTipContext(None), tooltipType))
        return

    @classmethod
    def overrideTooltipType(cls, tooltipProvider):
        if not issubclass(tooltipProvider, ToolTipBaseData):
            LOG_ERROR('Parameter is not a subclass of ToolTipBaseData', tooltipProvider)
            return
        cls.__tooltipProvider = tooltipProvider
