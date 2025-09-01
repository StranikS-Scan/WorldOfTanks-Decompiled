# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/intro_screen_model.py
from frameworks.wulf import Array, ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.schedule_info_model import ScheduleInfoModel

class IntroScreenModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=3, commands=1):
        super(IntroScreenModel, self).__init__(properties=properties, commands=commands)

    @property
    def scheduleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getScheduleInfoType():
        return ScheduleInfoModel

    def getVehicleLevels(self):
        return self._getArray(1)

    def setVehicleLevels(self, value):
        self._setArray(1, value)

    @staticmethod
    def getVehicleLevelsType():
        return int

    def getQualificationBattlesCount(self):
        return self._getNumber(2)

    def setQualificationBattlesCount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(IntroScreenModel, self)._initialize()
        self._addViewModelProperty('scheduleInfo', ScheduleInfoModel())
        self._addArrayProperty('vehicleLevels', Array())
        self._addNumberProperty('qualificationBattlesCount', 0)
        self.onClose = self._addCommand('onClose')
