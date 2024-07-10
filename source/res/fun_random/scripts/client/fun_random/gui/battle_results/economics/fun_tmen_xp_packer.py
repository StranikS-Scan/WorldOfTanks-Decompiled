# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/economics/fun_tmen_xp_packer.py
from functools import partial
from itertools import chain
import typing
from fun_random.gui.battle_results.pbs_helpers import isPremiumAdvertisingShown, getTotalTMenXPToShow
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_results.presenters.packers.economics.base_currency_packer import CurrencyRecord
from gui.battle_results.presenters.packers.economics.base_currency_packer import BaseCurrencyPacker, CurrencyGroup
from gui.battle_results.presenters.packers.economics.common_records import DESERTER_VIOLATION, SUICIDE_VIOLATION, AFK_VIOLATION
from gui.battle_results.settings import CurrenciesConstants
from shared_utils import first
if typing.TYPE_CHECKING:
    from gui.battle_results.stats_ctrl import BattleResults
_STR_PATH = R.strings.battle_results.details.calculations

def _getTmenXpValue(records, _, __, tID, xpList):
    for invID, xp in xpList:
        if invID == tID:
            return xp


TOTAL_TMEN_XP = CurrencyRecord(recordNames=(), subtractRecords=(), valueExtractor=getTotalTMenXPToShow, capsToBeChecked=None, label=_STR_PATH.title.total, modifiers=(), showZeroValue=True, currencyType=CurrenciesConstants.TMEN_XP)

class FunTmenXpPacker(BaseCurrencyPacker):
    __slots__ = ()
    _EARNED = CurrencyGroup(label=None, records=(DESERTER_VIOLATION, SUICIDE_VIOLATION, AFK_VIOLATION))
    _TOTAL = CurrencyGroup(label=None, records=(TOTAL_TMEN_XP,))

    @classmethod
    def packModel(cls, model, currencyType, battleResults):
        super(FunTmenXpPacker, cls).packModel(model, currencyType, battleResults)
        if isPremiumAdvertisingShown(currencyType, battleResults):
            _, premRecords = first(battleResults.reusable.personal.getTmenXPRecords())
            premFactor = premRecords.getFactor('appliedPremiumTmenXPFactor100')
            text = backport.text(R.strings.fun_battle_results.economy.double.tmen_xp(), value=int((premFactor - 1.0) * 100))
            model.setPremiumAdvertising(text)

    @classmethod
    def _getExtractors(cls, currencyType, battleResults):
        return ((lambda battleResults: battleResults,), zip)

    @classmethod
    def _getEarnedConfig(cls, battleResults):
        reusable = battleResults.reusable
        if reusable.personal.avatar.hasPenalties():
            return cls._EARNED
        else:
            personalResults = reusable.personal
            intCD, vehicle = first(personalResults.getVehicleItemsIterator())
            tmenXps = personalResults.xpProgress.get(intCD, {}).get('xpByTmen', [])
            if not tmenXps:
                return cls._EARNED
            records = []
            for _, tman in vehicle.crew:
                if tman is None:
                    continue
                records.append(CurrencyRecord(recordNames=(), subtractRecords=(), valueExtractor=partial(_getTmenXpValue, tID=tman.invID, xpList=tmenXps), capsToBeChecked=None, label=R.strings.ingame_gui.tankmen.dyn(tman.role), modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.TMEN_XP))

            return CurrencyGroup(label=None, records=list(chain(cls._EARNED.records, records))) if records else cls._EARNED
