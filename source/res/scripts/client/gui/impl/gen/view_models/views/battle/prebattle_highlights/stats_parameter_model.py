# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/prebattle_highlights/stats_parameter_model.py
from frameworks.wulf import ViewModel

class StatsParameterModel(ViewModel):
    __slots__ = ()
    CURRENT_TANK_SESSION_BATTLES_COUNT = 'currentTankSessionBattlesCount'
    CURRENT_TANK_SESSION_MAX_FRAGS = 'currentTankSessionMaxFrags'
    CURRENT_TANK_SESSION_MAX_DAMAGE_BLOCKED_BY_ARMOR = 'currentTankSessionMaxDamageBlockedByArmor'
    CURRENT_TANK_SESSION_MAX_DAMAGE_DEALT = 'currentTankSessionMaxDamageDealt'
    CURRENT_TANK_SESSION_MAX_ASSISTED = 'currentTankSessionMaxAssisted'
    CURRENT_TANK_SESSION_MAX_SPOTTED = 'currentTankSessionMaxSpotted'
    CURRENT_TANK_SESSION_MAX_SURVIVED = 'currentTankSessionMaxSurvived'
    CURRENT_TANK_SESSION_WIN_STREAK = 'currentTankSessionWinStreak'
    ACCOUNT_SESSION_BATTLES_COUNT = 'accountSessionBattlesCount'
    ACCOUNT_SESSION_TOTAL_TANKS_USED = 'accountSessionTotalTanksUsed'
    ACCOUNT_SESSION_TOTAL_FRAGS = 'accountSessionTotalFrags'
    ACCOUNT_SESSION_TOTAL_WINS = 'accountSessionTotalWins'
    ACCOUNT_SESSION_TOTAL_DAMAGE_BLOCKED_BY_ARMOR = 'accountSessionTotalDamageBlockedByArmor'
    ACCOUNT_SESSION_TOTAL_DAMAGE_DEALT = 'accountSessionTotalDamageDealt'
    ACCOUNT_SESSION_TOTAL_ASSISTED = 'accountSessionTotalAssisted'
    ACCOUNT_SESSION_TOTAL_SPOTTED = 'accountSessionTotalSpotted'
    ACCOUNT_SESSION_WIN_STREAK = 'accountSessionWinStreak'
    CURRENT_TANK_BATTLES_COUNT = 'currentTankBattlesCount'
    CURRENT_TANK_FRAGS = 'currentTankFrags'
    CURRENT_TANK_SPOTTED = 'currentTankSpotted'
    CURRENT_TANK_DAMAGE_DEALT = 'currentTankDamageDealt'
    CURRENT_TANK_DAMAGE_BLOCKED_BY_ARMOR = 'currentTankDamageBlockedByArmor'
    CURRENT_TANK_ASSISTED = 'currentTankAssisted'
    CURRENT_TANK_WINS = 'currentTankWins'
    ACCOUNT_TOTAL_DAMAGE_DEALT = 'accountTotalDamageDealt'
    ACCOUNT_TOTAL_WINS = 'accountTotalWins'
    ACCOUNT_TOTAL_SPOTTED = 'accountTotalSpotted'
    ACCOUNT_BATTLES_COUNT = 'accountBattlesCount'
    ACCOUNT_FUN_AGE = 'accountFunAge'
    ACCOUNT_FUN_TREES_DESTROYED = 'accountFunTreesDestroyed'
    ACCOUNT_TOTAL_MILEAGE = 'accountTotalMileage'

    def __init__(self, properties=2, commands=0):
        super(StatsParameterModel, self).__init__(properties=properties, commands=commands)

    def getParameter(self):
        return self._getString(0)

    def setParameter(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getNumber(1)

    def setValue(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(StatsParameterModel, self)._initialize()
        self._addStringProperty('parameter', '')
        self._addNumberProperty('value', 0)
