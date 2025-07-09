# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/Scaleform/daapi/view/tooltips/lobby_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.shared.tooltips import ToolTipBaseData
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import TooltipWindowBuilder
from mt_birthday.gui.impl.lobby.tooltips.golden_ticket_tooltip import GoldTicketTooltip
from mt_birthday.gui.impl.lobby.tooltips.post_stamp_tooltip import PostStampTooltip
from mt_birthday.gui.impl.lobby.tooltips.economy_bonus_tooltip import EconomyBonusTooltip
__all__ = ('getTooltipBuilders', 'BirthdayEconomyBonusTooltipContentWindowData')

def getTooltipBuilders():
    return (TooltipWindowBuilder(TOOLTIPS_CONSTANTS.BIRTHDAY_GIFT_SYSTEM_POSTMARK, None, GiftSystemPostMarkTooltipContentWindowData(contexts.ToolTipContext(None))), TooltipWindowBuilder(TOOLTIPS_CONSTANTS.BIRTHDAY_GOLDEN_TICKET, None, BirthdayGoldenTicketTooltipContentWindowData(contexts.ToolTipContext(None))))


class GiftSystemPostMarkTooltipContentWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(GiftSystemPostMarkTooltipContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.BIRTHDAY_GIFT_SYSTEM_POSTMARK)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(PostStampTooltip(), useDecorator=False)


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
