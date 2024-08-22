# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/nps_intro_view.py
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from base_crew_view import BaseCrewSubView
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.nps_intro_view_model import NpsIntroViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.crew.tooltips.conversion_tooltip import ConversionTooltip
from gui.impl.lobby.crew.tooltips.directive_conversion_tooltip import DirectiveConversionTooltip
from gui.impl.lobby.crew.utils import packCompensationData, packBoostersCompensationData
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.account_settings_helper import AccountSettingsHelper
from gui.shared.event_dispatcher import showCrewNpsWelcome
from uilogging.crew_nps.loggers import CrewNpsIntroViewLogger
from uilogging.crew_nps.logging_constants import CrewNpsViewKeys, CrewNpsNavigationButtons
MAX_MAIN_REWARDS_AMOUNT = 4

class NpsIntroView(BaseCrewSubView):
    __slots__ = ('__books', '__boosters', '__tooltipData', '__uiLogger')

    def __init__(self, **kwargs):
        settings = ViewSettings(R.views.lobby.crew.NpsIntroView())
        settings.model = NpsIntroViewModel()
        self.__tooltipData = {}
        self.__books = kwargs.get('books')
        self.__boosters = kwargs.get('boosters')
        self.__uiLogger = CrewNpsIntroViewLogger(self, CrewNpsViewKeys.INTRO, hasBooks=bool(self.__books))
        super(NpsIntroView, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.crew.tooltips.ConversionTooltip():
            tooltipId = event.getArgument('tooltipId')
            books = self.__tooltipData[tooltipId] if tooltipId in self.__tooltipData else []
            return ConversionTooltip(books, title=R.strings.tooltips.npsCompensation.header(), description=R.strings.tooltips.npsCompensation.body())
        if contentID == R.views.lobby.crew.tooltips.DirectiveConversionTooltip():
            tooltipId = event.getArgument('tooltipId')
            data = self.__tooltipData[tooltipId] if tooltipId in self.__tooltipData else {}
            return DirectiveConversionTooltip(**data)
        return super(NpsIntroView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(NpsIntroView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NpsIntroView, self)._onLoading(*args, **kwargs)
        self.__uiLogger.initialize()
        self.__updateViewModel()
        AccountSettingsHelper.welcomeScreenShown(GuiSettingsBehavior.CREW_NPS_INTRO_SHOWN)

    def _finalize(self):
        super(NpsIntroView, self)._finalize()
        self.__uiLogger.finalize()

    def _getEvents(self):
        return ((self.viewModel.onViewChanges, self.__onViewChanges), (self.viewModel.onSkipChanges, self.__onSkipChanges), (self.viewModel.onClose, self.__close))

    def __updateViewModel(self):
        with self.viewModel.transaction() as tx:
            rewards = tx.getRewards()
            additionalRewards = tx.getAdditionalRewards()
            booksAmount = 0
            if self.__books:
                booksAmount = packCompensationData(self.__books, rewards, self.__tooltipData)
            if self.__boosters:
                isAdditional = len(self.__boosters) + booksAmount > MAX_MAIN_REWARDS_AMOUNT
                packBoostersCompensationData(self.__boosters, additionalRewards if isAdditional else rewards, self.__tooltipData)

    @args2params(str)
    def __close(self, reason):
        self.__uiLogger.logButtonClick(reason)
        self.__markChangesAsSkipped()
        self.destroyWindow()

    def __onViewChanges(self):
        self.__uiLogger.logButtonClick(CrewNpsNavigationButtons.VIEW_CHANGES.value)
        showCrewNpsWelcome()
        self.destroyWindow()

    @classmethod
    def __markChangesAsSkipped(cls):
        AccountSettingsHelper.welcomeScreenShown(GuiSettingsBehavior.CREW_NPS_WELCOME_SHOWN)

    def __onSkipChanges(self):
        self.__uiLogger.logButtonClick(CrewNpsNavigationButtons.SKIP_CHANGES.value)
        self.__markChangesAsSkipped()
        self.destroyWindow()


class NpsIntroWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, **kwargs):
        super(NpsIntroWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=NpsIntroView(**kwargs), layer=WindowLayer.TOP_WINDOW)
