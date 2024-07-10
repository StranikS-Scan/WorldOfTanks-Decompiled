# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/economics/fun_currency_packers.py
import typing
from fun_random.gui.battle_results.pbs_helpers import isPremiumAdvertisingShown, getAdvertising
from gui.battle_results.pbs_helpers.economics import getCreditsRecords
from gui.battle_results.presenters.packers.economics.crystals_packer import CrystalsPacker
from gui.battle_results.presenters.packers.economics.credits_packer import CreditsPacker
from gui.battle_results.presenters.packers.economics.gold_records import GOLD_EVENT_PAYMENTS
from gui.battle_results.presenters.packers.economics.xp_packer import XpPacker
from gui.impl.gen import R
from gui.battle_results.settings import CurrenciesConstants
from gui.battle_results.presenters.packers.economics.base_currency_packer import BaseCurrencyPacker, CurrencyGroup
from shared_utils import first
if typing.TYPE_CHECKING:
    from gui.battle_results.stats_ctrl import BattleResults
    from fun_random.gui.impl.gen.view_models.views.lobby.tooltips.fun_random_economic_tooltip_view_model import FunRandomEconomicTooltipViewModel
_STR_PATH = R.strings.fun_battle_results.economy.double

class FunCreditsPacker(CreditsPacker):
    __slots__ = ()

    @classmethod
    def packModel(cls, model, currencyType, battleResults):
        super(FunCreditsPacker, cls).packModel(model, currencyType, battleResults)
        if isPremiumAdvertisingShown(currencyType, battleResults):
            text = getAdvertising(getCreditsRecords, 'appliedPremiumCreditsFactor100', _STR_PATH.credits, battleResults)
            model.setPremiumAdvertising(text)


class FunXpPacker(XpPacker):
    __slots__ = ()

    @classmethod
    def packModel(cls, model, currencyType, battleResults):
        super(FunXpPacker, cls).packModel(model, currencyType, battleResults)
        if not isPremiumAdvertisingShown(currencyType, battleResults):
            return
        else:
            extractors, _ = cls._getExtractors(currencyType, battleResults)
            if extractors is None:
                return
            extractor = first(extractors)
            if currencyType == CurrenciesConstants.FREE_XP:
                label = _STR_PATH.free_xp
            elif currencyType == CurrenciesConstants.XP_COST and len(extractors) > 1:
                label = _STR_PATH.xp_and_free_xp
            else:
                label = _STR_PATH.xp
            text = getAdvertising(extractor, 'appliedPremiumXPFactor100', label, battleResults)
            model.setPremiumAdvertising(text)
            return


class FunCrystalsPacker(CrystalsPacker):
    __slots__ = ()

    @classmethod
    def packModel(cls, model, currencyType, battleResults):
        super(FunCrystalsPacker, cls).packModel(model, currencyType, battleResults)
        model.setPremiumAdvertising('')


class FunGoldPacker(BaseCurrencyPacker):
    __slots__ = ()
    _EARNED = CurrencyGroup(label=None, records=(GOLD_EVENT_PAYMENTS,))

    @classmethod
    def packModel(cls, model, currencyType, battleResults):
        super(FunGoldPacker, cls).packModel(model, currencyType, battleResults)
        model.setPremiumAdvertising('')

    @classmethod
    def _getExtractors(cls, currencyType, battleResults):
        return ((getCreditsRecords,), zip)
