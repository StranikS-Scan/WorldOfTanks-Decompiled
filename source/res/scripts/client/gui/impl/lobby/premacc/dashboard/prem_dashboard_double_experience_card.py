# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/dashboard/prem_dashboard_double_experience_card.py
from constants import PremiumConfigs
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_double_experience_card_model import PremDashboardDoubleExperienceCardModel
from gui.impl.lobby.premacc.daily_experience_base import DailyExperienceBaseView
from gui.shared.event_dispatcher import showDailyExpPageView

class PremDashboardDoubleExperienceCard(DailyExperienceBaseView):
    __slots__ = ()

    def __init__(self, layoutID=R.views.lobby.premacc.dashboard.prem_dashboard_double_experience_card.PremDashboardDoubleExperienceCard()):
        settings = ViewSettings(layoutID)
        settings.model = PremDashboardDoubleExperienceCardModel()
        super(PremDashboardDoubleExperienceCard, self).__init__(settings)

    def onGoToDoubleExpView(self, args=None):
        showDailyExpPageView()

    def _initialize(self, *args, **kwargs):
        super(PremDashboardDoubleExperienceCard, self)._initialize(*args, **kwargs)
        self.__updateIsAvailable()

    def _addListeners(self):
        super(PremDashboardDoubleExperienceCard, self)._addListeners()
        self.viewModel.onGoToDoubleExpView += self.onGoToDoubleExpView

    def _removeListeners(self):
        self.viewModel.onGoToDoubleExpView -= self.onGoToDoubleExpView
        super(PremDashboardDoubleExperienceCard, self)._removeListeners()

    def _onServerSettingsChange(self, diff):
        diffConfig = diff.get(PremiumConfigs.DAILY_BONUS)
        if diffConfig is None:
            return
        else:
            if 'enabled' in diffConfig:
                self.__updateIsAvailable()
            super(PremDashboardDoubleExperienceCard, self)._onServerSettingsChange(diff)
            return

    def __updateIsAvailable(self):
        isAvailable = self._getConfig().get('enabled', False)
        self.viewModel.setIsAvailable(isAvailable)
