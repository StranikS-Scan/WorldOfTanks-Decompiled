# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/wt_event_helpers.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from white_tiger.gui.impl.lobby.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from white_tiger.gui.impl.lobby.tooltips.main_prize_discount_tooltip_view import MainPrizeDiscountTooltipView
from white_tiger.gui.impl.lobby.tooltips.wt_event_ticket_tooltip_view import WtEventTicketTooltipView
_COMP_TOOLTIP = R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent()

def backportTooltipDecorator(tooltipItemsName='_tooltipItems'):

    def decorator(func):

        def wrapper(self, event):
            if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
                tooltipData = _getTooltipDataByEvent(event, getattr(self, tooltipItemsName, {}))
                if tooltipData is None:
                    return
                if tooltipData.specialAlias == TOOLTIPS_CONSTANTS.EVENT_LOOTBOX:
                    window = DecoratedTooltipWindow(WtEventLootBoxTooltipView(isHunterLootBox=tooltipData.isHunterLootBox), parent=self.getParentWindow(), useDecorator=False)
                    window.move(event.mouse.positionX, event.mouse.positionY)
                elif tooltipData.specialAlias == TOOLTIPS_CONSTANTS.EVENT_VEHICLE_COMPENSATION:
                    window = DecoratedTooltipWindow(VehicleCompensationTooltipContent(_COMP_TOOLTIP, viewModelClazz=LootBoxVehicleCompensationTooltipModel, **tooltipData.specialArgs))
                    window.move(event.mouse.positionX, event.mouse.positionY)
                elif tooltipData.specialAlias == TOOLTIPS_CONSTANTS.EVENT_BATTLES_TICKET:
                    window = DecoratedTooltipWindow(WtEventTicketTooltipView(), parent=self.getParentWindow(), useDecorator=False)
                    window.move(event.mouse.positionX, event.mouse.positionY)
                elif tooltipData.specialAlias == TOOLTIPS_CONSTANTS.EVENT_MAIN_PRIZE_DISCOUNT:
                    window = DecoratedTooltipWindow(MainPrizeDiscountTooltipView(), parent=self.getParentWindow(), useDecorator=False)
                    window.move(event.mouse.positionX, event.mouse.positionY)
                else:
                    window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
            else:
                return func(self, event)

        return wrapper

    return decorator


def _getTooltipDataByEvent(event, tooltipItems):
    tooltipId = event.getArgument('tooltipId')
    if tooltipId is None:
        return
    else:
        tooltipData = tooltipItems.get(tooltipId)
        return None if tooltipData is None else tooltipData
