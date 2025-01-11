# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/gen/view_models/views/lobby/post_battle/post_battle_mission_model.py
from frameworks.wulf import ViewModel

class PostBattleMissionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(PostBattleMissionModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(0)

    def setDescription(self, value):
        self._setString(0, value)

    def getCurrentProgress(self):
        return self._getNumber(1)

    def setCurrentProgress(self, value):
        self._setNumber(1, value)

    def getTotalProgress(self):
        return self._getNumber(2)

    def setTotalProgress(self, value):
        self._setNumber(2, value)

    def getPrize(self):
        return self._getNumber(3)

    def setPrize(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(PostBattleMissionModel, self)._initialize()
        self._addStringProperty('description', '')
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalProgress', 0)
        self._addNumberProperty('prize', 0)
