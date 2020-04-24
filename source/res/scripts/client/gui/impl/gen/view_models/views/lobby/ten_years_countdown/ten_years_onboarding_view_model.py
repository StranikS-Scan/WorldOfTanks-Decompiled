# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ten_years_countdown/ten_years_onboarding_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.ten_years_countdown.onboarding_calendar_page_model import OnboardingCalendarPageModel
from gui.impl.gen.view_models.views.lobby.ten_years_countdown.onboarding_reward_page_model import OnboardingRewardPageModel
from gui.impl.gen.view_models.views.lobby.ten_years_countdown.onboarding_stage_info_page_model import OnboardingStageInfoPageModel

class TenYearsOnboardingViewModel(ViewModel):
    __slots__ = ('onForwardBtnClick', 'onBackBtnClick')

    def __init__(self, properties=6, commands=2):
        super(TenYearsOnboardingViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def calendar(self):
        return self._getViewModel(0)

    @property
    def stageInfo(self):
        return self._getViewModel(1)

    @property
    def reward(self):
        return self._getViewModel(2)

    def getChapterNumber(self):
        return self._getNumber(3)

    def setChapterNumber(self, value):
        self._setNumber(3, value)

    def getSelectedPageId(self):
        return self._getNumber(4)

    def setSelectedPageId(self, value):
        self._setNumber(4, value)

    def getPagesCount(self):
        return self._getNumber(5)

    def setPagesCount(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(TenYearsOnboardingViewModel, self)._initialize()
        self._addViewModelProperty('calendar', OnboardingCalendarPageModel())
        self._addViewModelProperty('stageInfo', OnboardingStageInfoPageModel())
        self._addViewModelProperty('reward', OnboardingRewardPageModel())
        self._addNumberProperty('chapterNumber', 0)
        self._addNumberProperty('selectedPageId', 0)
        self._addNumberProperty('pagesCount', 0)
        self.onForwardBtnClick = self._addCommand('onForwardBtnClick')
        self.onBackBtnClick = self._addCommand('onBackBtnClick')
