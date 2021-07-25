# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_progression/models/ext_money.py
from gui.shared.gui_items import formatMoneyError, GUI_ITEM_ECONOMY_CODE
from gui.shared.money import Currency, Money
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from soft_exception import SoftException
_XP = CURRENCIES_CONSTANTS.XP_COST
_VEH_XP = 'vehXP'
_FREE_XP = CURRENCIES_CONSTANTS.FREE_XP
_ALL_EXT = (_XP, _VEH_XP, _FREE_XP)

class ExtendedCurrency(Currency):
    XP = _XP
    VEH_XP = _VEH_XP
    FREE_XP = _FREE_XP
    ALL = Currency.ALL + _ALL_EXT
    BY_WEIGHT = Currency.BY_WEIGHT + _ALL_EXT


class ExtendedGuiItemEconomyCode(GUI_ITEM_ECONOMY_CODE):
    NOT_ENOUGH_XP = formatMoneyError(ExtendedCurrency.XP)
    NOT_ENOUGH_VEH_XP = formatMoneyError(ExtendedCurrency.VEH_XP)
    NOT_ENOUGH_FREE_XP = formatMoneyError(ExtendedCurrency.FREE_XP)
    NOT_ENOUGH_CURRENCIES = GUI_ITEM_ECONOMY_CODE.NOT_ENOUGH_CURRENCIES + (NOT_ENOUGH_XP, NOT_ENOUGH_VEH_XP, NOT_ENOUGH_FREE_XP)
    COMPOUND_PRICE = 'price_is_compound'
    XP_COMPOUND_PRICE = 'price_is_xp_compound'
    STEP_LOCKED = 'step_locked'
    STEP_RECIEVED = 'step_received'
    STEP_RESTRICTED = 'step_restricted'
    MOD_PERSISTENT = 'mod_persistent'
    MULTI_NOT_EXISTS = 'multi_not_exists'
    MULTI_NOT_EMPTY = 'multi_not_empty'
    MULTI_NOT_PURCHASED = 'multi_not_purchased'


class ExtendedMoney(Money):
    ALL = ExtendedCurrency.ALL
    WEIGHT = ExtendedCurrency.BY_WEIGHT

    def __init__(self, xp=None, vehXP=None, freeXP=None, *args, **kwargs):
        super(ExtendedMoney, self).__init__(*args, **kwargs)
        if xp is not None:
            self._values[_XP] = xp
        if vehXP is not None:
            self._values[_VEH_XP] = vehXP
        if freeXP is not None:
            self._values[_FREE_XP] = freeXP
        return

    @property
    def xp(self):
        return self._values.get(_XP)

    @property
    def vehXP(self):
        return self._values.get(_VEH_XP)

    @property
    def freeXP(self):
        return self._values.get(_FREE_XP)

    def isXPCompound(self):
        return self.isCompound() and self.isSet(_XP) and self.isSet(_FREE_XP)

    def toMoneyTuple(self):
        raise SoftException('Conversion of ExtendedMoney to old style _Money is not supported')


ExtendedMoney.UNDEFINED = EXT_MONEY_UNDEFINED = ExtendedMoney()
EXT_MONEY_ZERO_CREDITS = ExtendedMoney(credits=0)
EXT_MONEY_ZERO = ExtendedMoney(**{currency:0 for currency in ExtendedCurrency.ALL})

def getFullXPFromXPPrice(balance, price):
    vehicleXPPrice = ExtendedMoney(vehXP=price.xp)
    shortage = balance.getShortage(vehicleXPPrice)
    if shortage.vehXP is not None and shortage.vehXP > 0:
        price = price.replaceAll({ExtendedCurrency.VEH_XP: balance.vehXP,
         ExtendedCurrency.FREE_XP: shortage.vehXP})
    else:
        price = price.replace(ExtendedCurrency.VEH_XP, price.xp)
    return price
