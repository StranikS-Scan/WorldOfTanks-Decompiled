# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_results/tooltips/earned_currency_tooltips.py
import typing
from gui.battle_results.presenters.packers.economics.credits_packer import CreditsPacker
from gui.battle_results.presenters.packers.economics.crystals_packer import CrystalsPacker
from gui.battle_results.presenters.packers.economics.xp_packer import XpPacker
from gui.battle_results.presenters.packers.interfaces import ITooltipPacker
from gui.battle_results.settings import CurrenciesConstants
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.white_tiger_economic_tooltip_view_model import CurrencyType
if typing.TYPE_CHECKING:
    from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.white_tiger_economic_tooltip_view_model import WhiteTigerEconomicTooltipViewModel
    from gui.battle_results.stats_ctrl import BattleResults

class WTEarnedCurrencyTooltips(ITooltipPacker):
    __slots__ = ()
    _CURRENCY_VALUES_PACKERS = {CurrenciesConstants.CREDITS: CreditsPacker,
     CurrenciesConstants.GOLD: CreditsPacker,
     CurrenciesConstants.CRYSTAL: CrystalsPacker,
     CurrenciesConstants.XP_COST: XpPacker,
     CurrenciesConstants.FREE_XP: XpPacker}

    @classmethod
    def packTooltip(cls, model, battleResults, ctx=None):
        currencyType = ctx.get('currencyType')
        if currencyType is None:
            return
        else:
            model.setCurrencyType(CurrencyType(currencyType))
            currencyPacker = cls._CURRENCY_VALUES_PACKERS.get(currencyType)
            if currencyPacker is None:
                return
            currencyPacker.packModel(model, currencyType, battleResults)
            return
