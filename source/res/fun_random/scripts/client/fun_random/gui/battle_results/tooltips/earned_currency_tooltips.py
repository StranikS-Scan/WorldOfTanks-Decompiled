# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/tooltips/earned_currency_tooltips.py
import typing
from fun_random.gui.battle_results.economics.fun_tmen_xp_packer import FunTmenXpPacker
from fun_random.gui.battle_results.economics.fun_currency_packers import FunCreditsPacker, FunCrystalsPacker, FunXpPacker, FunGoldPacker
from fun_random.gui.impl.gen.view_models.views.lobby.tooltips.fun_random_economic_tooltip_view_model import CurrencyType
from gui.battle_results.presenters.packers.interfaces import ITooltipPacker
from gui.battle_results.settings import CurrenciesConstants
if typing.TYPE_CHECKING:
    from fun_random.gui.impl.gen.view_models.views.lobby.tooltips.fun_random_economic_tooltip_view_model import FunRandomEconomicTooltipViewModel
    from gui.battle_results.stats_ctrl import BattleResults

class FunEarnedCurrencyTooltipsPacker(ITooltipPacker):
    __slots__ = ()
    _CURRENCY_VALUES_PACKERS = {CurrenciesConstants.CREDITS: FunCreditsPacker,
     CurrenciesConstants.GOLD: FunGoldPacker,
     CurrenciesConstants.CRYSTAL: FunCrystalsPacker,
     CurrenciesConstants.XP_COST: FunXpPacker,
     CurrenciesConstants.FREE_XP: FunXpPacker,
     CurrenciesConstants.TMEN_XP: FunTmenXpPacker}

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
