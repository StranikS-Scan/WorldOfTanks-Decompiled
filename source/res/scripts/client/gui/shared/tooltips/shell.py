# Embedded file name: scripts/client/gui/shared/tooltips/shell.py
from debug_utils import LOG_ERROR
from gui.shared import g_itemsCache
from gui.shared.gui_items.vehicle_modules import VehicleGun
from gui.shared.tooltips import ToolTipDataField, getComplexStatus, ToolTipParameterField, ToolTipData, ToolTipAttrField, TOOLTIP_TYPE
from gui.shared.utils import ItemsParameters
from gui.shared.gui_items.Vehicle import Vehicle
from shared_utils import findFirst

class ShellStatusField(ToolTipDataField):

    def _getValue(self):
        status = None
        statusLvl = Vehicle.VEHICLE_STATE_LEVEL.WARNING
        shell = self._tooltip.item
        configuration = self._tooltip.context.getStatusConfiguration(shell)
        checkBuying = configuration.checkBuying
        if checkBuying:
            couldBeBought, reason = shell.mayPurchase(g_itemsCache.items.stats.money)
            if not couldBeBought:
                status = '#tooltips:moduleFits/%s' % reason
                statusLvl = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
        statusHeader, statusText = getComplexStatus(status)
        return {'header': statusHeader,
         'text': statusText,
         'level': statusLvl}


class ShellStatsField(ToolTipDataField):

    def _getValue(self):
        result = []
        shell = self._tooltip.item
        configuration = self._tooltip.context.getStatsConfiguration(shell)
        buyPrice = configuration.buyPrice
        sellPrice = configuration.sellPrice
        if buyPrice and sellPrice:
            LOG_ERROR('You are not allowed to use buyPrice and sellPrice at the same time')
            return None
        else:
            if buyPrice:
                items = g_itemsCache.items
                credits, gold = items.stats.money
                price = shell.altPrice
                creditsNeeded = price[0] - credits if price[0] else 0
                goldNeeded = price[1] - gold if price[1] else 0
                need = (max(0, creditsNeeded), max(0, goldNeeded))
                result.append(('buy_price', (price, need)))
                result.append(('def_buy_price', shell.defaultAltPrice))
                result.append(('action_prc', shell.actionPrc))
            if sellPrice:
                result.append(('sell_price', shell.sellPrice))
                result.append(('def_sell_price', shell.defaultSellPrice))
                result.append(('action_prc', shell.sellActionPrc))
            inventoryCount = shell.inventoryCount
            if inventoryCount:
                result.append(('inventoryCount', inventoryCount))
            return result


class ShellParamsField(ToolTipParameterField):

    def _getValue(self):
        result = list()
        shell = self._tooltip.item
        configuration = self._tooltip.context.getParamsConfiguration(shell)
        vehicle = configuration.vehicle
        params = configuration.params
        vDescr = vehicle.descriptor if vehicle is not None else None
        vCompDescr = vehicle.intCD if vehicle is not None else None
        result.append([])
        if params:
            result = [ItemsParameters.g_instance.getParameters(shell.descriptor, vDescr)]
        result.append([])
        if vehicle is not None:
            gun = VehicleGun(intCompactDescr=vDescr.gun['compactDescr'], descriptor=vDescr.gun)
            vehicleShell = findFirst(lambda s: s.intCD == shell.intCD, vehicle.shells)
            shellCount = vehicleShell.count if vehicleShell else getattr(shell, 'count', 0)
            result[-1].append({'label': 'ammo',
             'current': shellCount,
             'total': gun.descriptor['maxAmmo']})
        return result


class ShellIsGoldField(ToolTipDataField):

    def _getValue(self):
        shell = self._tooltip.item
        configuration = self._tooltip.context.getStatsConfiguration(shell)
        buyPrice = configuration.buyPrice
        sellPrice = configuration.sellPrice
        if buyPrice and sellPrice:
            LOG_ERROR('You are not allowed to use buyPrice and sellPrice at the same time')
            return None
        elif buyPrice:
            return shell.buyPrice[1] > 0
        elif sellPrice:
            return shell.sellPrice[1] > 0
        else:
            return super(ShellIsGoldField, self)._getValue()


class ShellToolTipData(ToolTipData):

    def __init__(self, context):
        super(ShellToolTipData, self).__init__(context, TOOLTIP_TYPE.SHELL)
        self.fields = (ToolTipAttrField(self, 'name', 'userName'),
         ToolTipAttrField(self, 'type'),
         ToolTipAttrField(self, 'icon'),
         ShellStatsField(self, 'stats'),
         ShellParamsField(self, 'params'),
         ShellIsGoldField(self, 'gold'),
         ShellStatusField(self, 'status'))
