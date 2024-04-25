# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/prb_control/prb_config.py
from constants_utils import ConstInjector
from gui.prb_control import settings

class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    HISTORICAL_BATTLES = 'historicalBattles'
    HISTORICAL_BATTLES_SQUAD = 'historicalBattlesSquad'


class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    HISTORICAL_BATTLES = 1073741824


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    HISTORICAL_BATTLES = 'historicalBattles'
