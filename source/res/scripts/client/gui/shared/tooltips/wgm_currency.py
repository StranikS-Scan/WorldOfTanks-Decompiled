# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/wgm_currency.py
import BigWorld
from debug_utils import LOG_ERROR
from gui.shared.money import Currency
from gui.shared.tooltips.common import DynamicBlocksTooltipData
from gui.shared.utils.requesters import wgm_balance_info_requester
from gui.shared.tooltips import formatters
from gui.shared.formatters import text_styles
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_WAITING_FOR_DATA = ''
_UNKNOWN_VALUE = '-'

class WGMCurrencyTooltip(DynamicBlocksTooltipData):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx):
        super(WGMCurrencyTooltip, self).__init__(ctx, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI)
        self._setContentMargin(top=17, left=20, bottom=18, right=13)
        self._setMargins(afterBlock=0)
        self._setWidth(290)
        self.__requester = wgm_balance_info_requester.WGMBalanceInfoRequester()
        self.__data = None
        self._btnType = None
        return

    def getWGMCurrencyValue(self, key):
        if not self.isWGMAvailable():
            return _UNKNOWN_VALUE
        elif self.__data is None:
            return _WAITING_FOR_DATA
        else:
            return BigWorld.wg_getIntegralFormat(int(self.__data[key])) if key in self.__data else _UNKNOWN_VALUE

    def stopUpdates(self):
        self.__requester.clearCallbacks()
        super(WGMCurrencyTooltip, self).stopUpdates()

    def changeVisibility(self, isVisible):
        super(WGMCurrencyTooltip, self).changeVisibility(isVisible)
        if isVisible and self.isWGMAvailable():
            self.__requester.requestInfo(lambda result: self.__onDataResponse(result))

    @classmethod
    def isWGMAvailable(cls):
        return cls.itemsCache.items.stats.mayConsumeWalletResources

    def _packBlocks(self, *args, **kwargs):
        tooltipBlocks = super(WGMCurrencyTooltip, self)._packBlocks(*args, **kwargs)
        btnType = kwargs.get('btnType', None)
        if btnType and btnType != self._btnType:
            self._btnType = btnType
        if self._btnType is None:
            LOG_ERROR('WGMGoldCurrencyTooltip empty btnType!')
            return tooltipBlocks
        else:
            return formatters.packMoneyAndXpBlocks(tooltipBlocks, btnType=self._btnType, valueBlocks=self.__getValueBlocks())

    def __onDataResponse(self, data):
        if self.__data is None or self.__checkDiff(self.__data, data):
            self.__data = data
            self.updateData()
        return

    @staticmethod
    def __checkDiff(d1, d2):
        s1 = frozenset(d1.itervalues())
        s2 = frozenset(d2.itervalues())
        return s1 ^ s2

    def __getValueBlocks(self):
        valueBlocks = list()
        if self._btnType == Currency.GOLD:
            valueBlocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.HANGAR_HEADER_WGMONEYTOOLTIP_PURCHASEDVALUE), value=self.__getGoldString(wgm_balance_info_requester.GOLD_PURCHASED), icon=Currency.GOLD, valueWidth=84, iconYOffset=2))
            valueBlocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.HANGAR_HEADER_WGMONEYTOOLTIP_EARNEDVALUE), value=self.__getGoldString(wgm_balance_info_requester.GOLD_EARNED), icon=Currency.GOLD, padding=formatters.packPadding(bottom=10), valueWidth=84, iconYOffset=2))
            valueBlocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.HANGAR_HEADER_WGMONEYTOOLTIP_TOTALVALUE), value=text_styles.gold(self.__getGoldTotal()), icon=Currency.GOLD, padding=formatters.packPadding(bottom=15), valueWidth=84, iconYOffset=2))
        else:
            valueBlocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.HANGAR_HEADER_WGMONEYTOOLTIP_PURCHASEDVALUE), value=self.__getCreditsString(wgm_balance_info_requester.CREDITS_PURCHASED), icon=Currency.CREDITS, valueWidth=84, iconYOffset=2))
            valueBlocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.HANGAR_HEADER_WGMONEYTOOLTIP_EARNEDVALUE), value=self.__getCreditsString(wgm_balance_info_requester.CREDITS_EARNED), icon=Currency.CREDITS, padding=formatters.packPadding(bottom=10), valueWidth=84, iconYOffset=2))
            valueBlocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.HANGAR_HEADER_WGMONEYTOOLTIP_TOTALVALUE), value=text_styles.credits(self.__getCreditsTotal()), icon=Currency.CREDITS, padding=formatters.packPadding(bottom=15), valueWidth=84, iconYOffset=2))
        return valueBlocks

    def __getGoldString(self, goldType):
        result = self.getWGMCurrencyValue(goldType)
        return text_styles.gold(result) if result != _WAITING_FOR_DATA else result

    def __getGoldTotal(self):
        return BigWorld.wg_getIntegralFormat(self.itemsCache.items.stats.gold) if self.isWGMAvailable() else _UNKNOWN_VALUE

    def __getCreditsString(self, creditsType):
        result = self.getWGMCurrencyValue(creditsType)
        return text_styles.credits(result) if result != _WAITING_FOR_DATA else result

    def __getCreditsTotal(self):
        return BigWorld.wg_getIntegralFormat(self.itemsCache.items.stats.credits) if self.isWGMAvailable() else _UNKNOWN_VALUE
