# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/crew_nps/loggers.py
from uilogging.crew.loggers import CrewMetricsLogger, CrewViewLogger, CrewDialogLogger
from uilogging.crew_nps.logging_constants import FEATURE, CrewNpsNavigationButtons, CrewNpsIntroAdditionalInfo, CrewBannerWidgetKeys, CrewBannerWidgetButton
from gui.impl.gen.view_models.views.lobby.crew.crew_intro_view_model import CloseReason as WelcomeScreenCloseReason
from gui.impl.gen.view_models.views.lobby.crew.nps_intro_view_model import CloseReason as CrewNpsIntroViewCloseReason

class CrewNpsViewLogger(CrewViewLogger):
    _FEATURE = FEATURE


class CrewNpsDialogLogger(CrewDialogLogger):
    _FEATURE = FEATURE


class CrewNpsWelcomeViewLogger(CrewNpsViewLogger):
    _REASONS = {WelcomeScreenCloseReason.CLOSE.value: CrewNpsNavigationButtons.CLOSE,
     WelcomeScreenCloseReason.ESC.value: CrewNpsNavigationButtons.ESC,
     WelcomeScreenCloseReason.AFFIRMATIVE.value: CrewNpsNavigationButtons.AFFIRMATIVE}

    def logButtonClick(self, closeReason):
        return super(CrewNpsWelcomeViewLogger, self).logNavigationButtonClick(self._REASONS.get(closeReason, CrewNpsNavigationButtons.CLOSE))


class CrewNpsIntroViewLogger(CrewNpsViewLogger):
    _REASONS = {CrewNpsIntroViewCloseReason.CLOSE.value: CrewNpsNavigationButtons.CLOSE,
     CrewNpsIntroViewCloseReason.ESC.value: CrewNpsNavigationButtons.ESC,
     CrewNpsIntroViewCloseReason.SKIPCHANGES.value: CrewNpsNavigationButtons.SKIP_CHANGES,
     CrewNpsIntroViewCloseReason.VIEWCHANGES.value: CrewNpsNavigationButtons.VIEW_CHANGES}
    __slots__ = ('__info',)

    def __init__(self, currentView, currentViewKey=None, parentViewKey=None, hasBooks=False):
        super(CrewNpsIntroViewLogger, self).__init__(currentView, currentViewKey, parentViewKey)
        self.__info = CrewNpsIntroAdditionalInfo.WITH_BOOKS if hasBooks else CrewNpsIntroAdditionalInfo.NO_BOOK

    def logButtonClick(self, closeReason):
        return super(CrewNpsIntroViewLogger, self).logNavigationButtonClick(self._REASONS.get(closeReason, CrewNpsNavigationButtons.CLOSE), info=self.__info)

    def _viewOpened(self, info=None):
        super(CrewNpsIntroViewLogger, self)._viewOpened(info=self.__info)

    def _viewClosed(self, info=None):
        return super(CrewNpsIntroViewLogger, self)._viewClosed(info=self.__info)


class CrewBannerWidgetLogger(CrewMetricsLogger):
    _FEATURE = FEATURE

    def logFillButtonClick(self):
        return super(CrewBannerWidgetLogger, self).logNavigationButtonClick(CrewBannerWidgetButton.FILL, parentScreen=CrewBannerWidgetKeys.CREW_BANNER_WIDGET)

    def logResetButtonClick(self):
        return super(CrewBannerWidgetLogger, self).logNavigationButtonClick(CrewBannerWidgetButton.RESET, parentScreen=CrewBannerWidgetKeys.CREW_BANNER_WIDGET)
