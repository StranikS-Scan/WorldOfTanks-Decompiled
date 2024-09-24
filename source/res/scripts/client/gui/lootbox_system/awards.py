# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lootbox_system/awards.py
from gui.shared.money import Currency, Money, ZERO_MONEY
from helpers import dependency
from messenger.formatters.service_channel_helpers import getCustomizationItem
from skeletons.gui.shared import IItemsCache

def preformatRewardsInfo(rewards):
    vehiclesList = rewards.get('vehicles', [])
    customizationsList = rewards.get('customizations', [])
    compValue = _getCompensationValue(vehiclesList)
    _addLockedStyleForVehicle(customizationsList, vehiclesList)
    for currency in Currency.ALL:
        if compValue.get(currency, 0) > 0:
            currencyValue = rewards.pop(currency, None)
            if currency is not None:
                newCurrencyValue = currencyValue - compValue.get(currency, 0)
                if newCurrencyValue:
                    rewards[currency] = newCurrencyValue

    return


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _addLockedStyleForVehicle(customizations, vehicles, itemsCache=None):
    if customizations and vehicles:
        for customization in customizations:
            customizationType = customization['custType']
            if customizationType == 'style':
                customizationID = customization['id']
                style = getCustomizationItem(customizationID, customizationType)
                if style is not None and style.isLockedOnVehicle:
                    vehCD = customization.get('vehTypeCompDescr')
                    for vehicleDict in vehicles:
                        cd = next(iter(vehicleDict))
                        if vehCD == cd or vehCD is None and style.mayInstall(itemsCache.items.getItemByCD(cd)):
                            vehicleDict[cd].update({'customization': {'styleId': customizationID}})
                            break

    return


def _getCompensationValue(vehicles):
    compensation = ZERO_MONEY
    for vehicleDict in vehicles:
        for vehData in vehicleDict.itervalues():
            if 'rentCompensation' in vehData:
                compensation += Money.makeFromMoneyTuple(vehData['rentCompensation'])
            if 'customCompensation' in vehData:
                compensation += Money.makeFromMoneyTuple(vehData['customCompensation'])

    return compensation
