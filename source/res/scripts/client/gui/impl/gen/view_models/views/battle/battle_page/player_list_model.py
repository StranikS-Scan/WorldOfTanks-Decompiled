# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/battle_page/player_list_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.battle_player import BattlePlayer

class PlayerListModel(ViewModel):
    __slots__ = ('onPlatoonInvite', 'onPlayerCommend')

    def __init__(self, properties=9, commands=2):
        super(PlayerListModel, self).__init__(properties=properties, commands=commands)

    def getIsColorblind(self):
        return self._getBool(0)

    def setIsColorblind(self, value):
        self._setBool(0, value)

    def getIsFogOfWarEnabled(self):
        return self._getBool(1)

    def setIsFogOfWarEnabled(self, value):
        self._setBool(1, value)

    def getIsCommendationEnabled(self):
        return self._getBool(2)

    def setIsCommendationEnabled(self, value):
        self._setBool(2, value)

    def getIsLiveTagsEnabled(self):
        return self._getBool(3)

    def setIsLiveTagsEnabled(self, value):
        self._setBool(3, value)

    def getIsAnonymized(self):
        return self._getBool(4)

    def setIsAnonymized(self, value):
        self._setBool(4, value)

    def getHasClan(self):
        return self._getBool(5)

    def setHasClan(self, value):
        self._setBool(5, value)

    def getPlatoonsEnabled(self):
        return self._getBool(6)

    def setPlatoonsEnabled(self, value):
        self._setBool(6, value)

    def getAllies(self):
        return self._getArray(7)

    def setAllies(self, value):
        self._setArray(7, value)

    @staticmethod
    def getAlliesType():
        return BattlePlayer

    def getEnemies(self):
        return self._getArray(8)

    def setEnemies(self, value):
        self._setArray(8, value)

    @staticmethod
    def getEnemiesType():
        return BattlePlayer

    def _initialize(self):
        super(PlayerListModel, self)._initialize()
        self._addBoolProperty('isColorblind', False)
        self._addBoolProperty('isFogOfWarEnabled', False)
        self._addBoolProperty('isCommendationEnabled', False)
        self._addBoolProperty('isLiveTagsEnabled', False)
        self._addBoolProperty('isAnonymized', False)
        self._addBoolProperty('hasClan', False)
        self._addBoolProperty('platoonsEnabled', False)
        self._addArrayProperty('allies', Array())
        self._addArrayProperty('enemies', Array())
        self.onPlatoonInvite = self._addCommand('onPlatoonInvite')
        self.onPlayerCommend = self._addCommand('onPlayerCommend')
