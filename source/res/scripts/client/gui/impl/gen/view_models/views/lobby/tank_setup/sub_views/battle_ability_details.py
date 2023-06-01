# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/battle_ability_details.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_ability_level_model import BattleAbilityLevelModel

class BattleAbilityDetails(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(BattleAbilityDetails, self).__init__(properties=properties, commands=commands)

    def getIntCD(self):
        return self._getNumber(0)

    def setIntCD(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getCategory(self):
        return self._getString(2)

    def setCategory(self, value):
        self._setString(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getSelectedLevel(self):
        return self._getNumber(4)

    def setSelectedLevel(self, value):
        self._setNumber(4, value)

    def getIsActivated(self):
        return self._getBool(5)

    def setIsActivated(self, value):
        self._setBool(5, value)

    def getLevelInfos(self):
        return self._getArray(6)

    def setLevelInfos(self, value):
        self._setArray(6, value)

    @staticmethod
    def getLevelInfosType():
        return BattleAbilityLevelModel

    def _initialize(self):
        super(BattleAbilityDetails, self)._initialize()
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('category', '')
        self._addStringProperty('description', '')
        self._addNumberProperty('selectedLevel', 0)
        self._addBoolProperty('isActivated', False)
        self._addArrayProperty('levelInfos', Array())
