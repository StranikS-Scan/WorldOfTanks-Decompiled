# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/personal_case/service_record_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.tankman_info_model import TankmanInfoModel
from gui.impl.gen.view_models.views.lobby.crew.personal_case.achievement_model import AchievementModel

class ServiceRecordViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(ServiceRecordViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def tankmanInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getTankmanInfoType():
        return TankmanInfoModel

    def getIsTankmanInVehicle(self):
        return self._getBool(1)

    def setIsTankmanInVehicle(self, value):
        self._setBool(1, value)

    def getRankName(self):
        return self._getString(2)

    def setRankName(self, value):
        self._setString(2, value)

    def getRankIcon(self):
        return self._getString(3)

    def setRankIcon(self, value):
        self._setString(3, value)

    def getBattlesCount(self):
        return self._getNumber(4)

    def setBattlesCount(self, value):
        self._setNumber(4, value)

    def getAverageXP(self):
        return self._getNumber(5)

    def setAverageXP(self, value):
        self._setNumber(5, value)

    def getAchievementsList(self):
        return self._getArray(6)

    def setAchievementsList(self, value):
        self._setArray(6, value)

    @staticmethod
    def getAchievementsListType():
        return AchievementModel

    def _initialize(self):
        super(ServiceRecordViewModel, self)._initialize()
        self._addViewModelProperty('tankmanInfo', TankmanInfoModel())
        self._addBoolProperty('isTankmanInVehicle', False)
        self._addStringProperty('rankName', '')
        self._addStringProperty('rankIcon', '')
        self._addNumberProperty('battlesCount', 0)
        self._addNumberProperty('averageXP', 0)
        self._addArrayProperty('achievementsList', Array())
