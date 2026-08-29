# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/wt_event_helpers.py
import copy
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.server_events.bonuses import CustomizationsBonus, CreditsBonus
from white_tiger.gui.impl.lobby.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from white_tiger.gui.impl.lobby.tooltips.wt_event_ticket_tooltip_view import WtEventTicketTooltipView
from white_tiger.gui.impl.lobby.tooltips.main_prize_discount_tooltip_view import MainPrizeDiscountTooltipView
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


def _getCustomDataForVehicle(bonus, customBonusData):
    vehicles = customBonusData.get('vehicles', {})
    if not vehicles:
        return {}
    for vehicle, _ in bonus.getVehicles():
        if vehicle.intCD in vehicles:
            return vehicles[vehicle.intCD]

    return {}


_CUSTOM_DATA_READER = {'vehicles': _getCustomDataForVehicle}
_DEFAULT_WEIGHT_BY_TYPE = {'vehicles': 8,
 'customizations': 7,
 'gold': 6,
 'credits': 5,
 'items': 4,
 'goodies': 3,
 'freeXP': 2,
 'crewBooks': 1}

def extendBonusesByLootboxCustomSettings(bonuses, customBonusData, isSortByWeight=True):
    extendedBonuses = []
    for bonus in (b for b in bonuses if b.isShowInGUI()):
        extendedBonus = copy.copy(bonus)
        extendData = getCustomData(extendedBonus, customBonusData)
        setattr(extendedBonus, 'wtExtendData', extendData)
        extendedBonuses.append(extendedBonus)

    return sorted(extendedBonuses, key=lambda x: x.wtExtendData['weight'], reverse=True) if isSortByWeight else extendedBonuses


def getCustomData(bonus, customBonusData):
    name = bonus.getName()
    reader = _CUSTOM_DATA_READER.get(name)
    groupId, bonusGroupData = getGroupIdData(bonus, customBonusData.get('bonusGroupes', {}))
    res = {}
    if reader:
        res[name] = reader(bonus, customBonusData)
    if groupId:
        res['group'] = (groupId, bonusGroupData)
    weightsConfig = customBonusData.get('weights', {}).get(name)
    res['weight'] = 0
    if weightsConfig:
        bonusId = getBonusIdForWeight(name, bonus)
        if not bonusId:
            return res
        for key, value in weightsConfig.items():
            if bonusId in value:
                res['weight'] = key
                break

    if res['weight'] == 0:
        res['weight'] = _DEFAULT_WEIGHT_BY_TYPE.get(name, 0)
    return res


def getBonusIdForWeight(name, bonus):
    if name == 'vehicles':
        vehicles = bonus.getVehicles()
        if vehicles:
            return vehicles[0][0].intCD
        return 0
    elif name == 'customizations':
        item = bonus.getCustomizations()[0]
        return bonus.getC11nItem(item).id
    else:
        if name in ('lootBoxToken', 'ticket'):
            for tokenID, _ in bonus.getTokens().iteritems():
                return tokenID

        return None


def getGroupIdData(bonus, bonusGroupes):
    value = bonus.getValue()
    if isinstance(value, dict):
        keys = value.keys()
        intCD = keys[0]
        for key, data in bonusGroupes.items():
            if intCD in data.get('itemIDs'):
                return (key, data)

    elif isinstance(bonus, CustomizationsBonus):
        item = bonus.getCustomizations()[0]
        styleId = bonus.getC11nItem(item).id
        for key, data in bonusGroupes.items():
            if styleId in data.get('itemIDs'):
                return (key, data)

    elif isinstance(bonus, CreditsBonus):
        for key, data in bonusGroupes.items():
            if bonus.getName() == data.get('type'):
                return (key, data)

    return (None, None)
