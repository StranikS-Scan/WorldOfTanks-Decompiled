# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/battle_info_model.py
from frameworks.wulf import ViewModel

class BattleInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BattleInfoModel, self).__init__(properties=properties, commands=commands)

    def getMapName(self):
        return self._getString(0)

    def setMapName(self, value):
        self._setString(0, value)

    def getStartDate(self):
        return self._getString(1)

    def setStartDate(self, value):
        self._setString(1, value)

    def getDuration(self):
        return self._getString(2)

    def setDuration(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(BattleInfoModel, self)._initialize()
        self._addStringProperty('mapName', '')
        self._addStringProperty('startDate', '')
        self._addStringProperty('duration', '')
