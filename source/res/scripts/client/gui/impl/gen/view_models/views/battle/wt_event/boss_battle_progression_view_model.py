# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/wt_event/boss_battle_progression_view_model.py
from frameworks.wulf import ViewModel

class BossBattleProgressionViewModel(ViewModel):
    __slots__ = ()
    HP_RATIO = 0.1

    def __init__(self, properties=7, commands=0):
        super(BossBattleProgressionViewModel, self).__init__(properties=properties, commands=commands)

    def getPlayerName(self):
        return self._getString(0)

    def setPlayerName(self, value):
        self._setString(0, value)

    def getClanTag(self):
        return self._getString(1)

    def setClanTag(self, value):
        self._setString(1, value)

    def getCurrentHp(self):
        return self._getNumber(2)

    def setCurrentHp(self, value):
        self._setNumber(2, value)

    def getMaxHp(self):
        return self._getNumber(3)

    def setMaxHp(self, value):
        self._setNumber(3, value)

    def getIsSpecial(self):
        return self._getBool(4)

    def setIsSpecial(self, value):
        self._setBool(4, value)

    def getIsPlayer(self):
        return self._getBool(5)

    def setIsPlayer(self, value):
        self._setBool(5, value)

    def getKills(self):
        return self._getNumber(6)

    def setKills(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(BossBattleProgressionViewModel, self)._initialize()
        self._addStringProperty('playerName', '')
        self._addStringProperty('clanTag', '')
        self._addNumberProperty('currentHp', 0)
        self._addNumberProperty('maxHp', 10)
        self._addBoolProperty('isSpecial', False)
        self._addBoolProperty('isPlayer', False)
        self._addNumberProperty('kills', 0)
