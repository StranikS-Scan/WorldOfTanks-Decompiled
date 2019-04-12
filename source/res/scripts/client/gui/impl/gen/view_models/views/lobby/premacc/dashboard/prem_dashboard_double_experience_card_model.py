# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/prem_dashboard_double_experience_card_model.py
from gui.impl.gen.view_models.views.lobby.premacc.daily_experience_base_model import DailyExperienceBaseModel

class PremDashboardDoubleExperienceCardModel(DailyExperienceBaseModel):
    __slots__ = ('onGoToDoubleExpView',)

    def getIsAvailable(self):
        return self._getBool(4)

    def setIsAvailable(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(PremDashboardDoubleExperienceCardModel, self)._initialize()
        self._addBoolProperty('isAvailable', True)
        self.onGoToDoubleExpView = self._addCommand('onGoToDoubleExpView')
