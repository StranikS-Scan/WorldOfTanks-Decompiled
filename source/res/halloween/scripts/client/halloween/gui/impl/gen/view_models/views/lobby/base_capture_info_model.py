# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/base_capture_info_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from halloween.gui.impl.gen.view_models.views.lobby.base_info_model import BaseInfoModel

class BaseCaptureInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(BaseCaptureInfoModel, self).__init__(properties=properties, commands=commands)

    def getTotalPlayerTeamDamage(self):
        return self._getNumber(0)

    def setTotalPlayerTeamDamage(self, value):
        self._setNumber(0, value)

    def getTotalEnemyTeamDamage(self):
        return self._getNumber(1)

    def setTotalEnemyTeamDamage(self, value):
        self._setNumber(1, value)

    def getDuration(self):
        return self._getString(2)

    def setDuration(self, value):
        self._setString(2, value)

    def getIsColorBlind(self):
        return self._getBool(3)

    def setIsColorBlind(self, value):
        self._setBool(3, value)

    def getBases(self):
        return self._getArray(4)

    def setBases(self, value):
        self._setArray(4, value)

    @staticmethod
    def getBasesType():
        return BaseInfoModel

    def _initialize(self):
        super(BaseCaptureInfoModel, self)._initialize()
        self._addNumberProperty('totalPlayerTeamDamage', 0)
        self._addNumberProperty('totalEnemyTeamDamage', 0)
        self._addStringProperty('duration', '')
        self._addBoolProperty('isColorBlind', False)
        self._addArrayProperty('bases', Array())
