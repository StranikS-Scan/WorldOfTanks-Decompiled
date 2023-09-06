# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/intro_screen_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.schedule_info_model import ScheduleInfoModel

class IntroScreenModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(IntroScreenModel, self).__init__(properties=properties, commands=commands)

    @property
    def scheduleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getScheduleInfoType():
        return ScheduleInfoModel

    def getQualificationBattlesCount(self):
        return self._getNumber(1)

    def setQualificationBattlesCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(IntroScreenModel, self)._initialize()
        self._addViewModelProperty('scheduleInfo', ScheduleInfoModel())
        self._addNumberProperty('qualificationBattlesCount', 0)
        self.onClose = self._addCommand('onClose')
