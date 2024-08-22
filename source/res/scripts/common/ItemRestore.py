# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ItemRestore.py


class RESTORE_VEHICLE_TYPE:
    PREMIUM = 0
    ACTION = 1


def getVehicleRestorePrice(defaultBuyPrice, exchangeRate, sellPriceFactor, sellToRestoreFactor):
    credits = defaultBuyPrice[0] + defaultBuyPrice[1] * exchangeRate
    return (int(credits * sellPriceFactor * sellToRestoreFactor), 0)
