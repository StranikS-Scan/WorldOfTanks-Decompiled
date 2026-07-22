# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/lobby/tank_academy/tank_academy_entry_point_view.py
import typing
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.hangar.entry_points.gf_header_widget import GFHeaderWidget, GFHeaderWidgetView
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import ITankAcademyController
from skeletons.gui.server_events import IEventsCache
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.tank_academy_entry_point_view_model import TankAcademyEntryPointViewModel
from tank_academy.gui.impl.lobby.tank_academy.tooltips.tank_academy_entry_point_tooltip_view import TankAcademyEntryPointTooltipView
from tank_academy.gui.shared.event_dispatcher import showTankAcademy
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewEvent, View
    from typing import Sequence, Tuple, Callable, Optional
    from Event import Event

class TankAcademyEntryPointView(GFHeaderWidgetView):
    __slots__ = ()
    __tankAcademyController = dependency.descriptor(ITankAcademyController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(TankAcademyEntryPointView, self).__init__(R.views.tank_academy.lobby.tank_academy.TankAcademyEntryPointView(), TankAcademyEntryPointViewModel())

    @property
    def viewModel(self):
        return super(TankAcademyEntryPointView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return TankAcademyEntryPointTooltipView() if contentID == R.views.tank_academy.lobby.tank_academy.tooltips.TankAcademyEntryPointTooltipView() else super(TankAcademyEntryPointView, self).createToolTipContent(event, contentID)

    def _onLoading(self):
        super(TankAcademyEntryPointView, self)._onLoading()
        self.__update()

    def _getEvents(self):
        events = super(TankAcademyEntryPointView, self)._getEvents()
        events += ((self.viewModel.onClick, self.__onClick), (self.__tankAcademyController.onStateChanged, self.__update), (self.__eventsCache.onSyncCompleted, self.__update))
        return events

    def __update(self, *_):
        with self.viewModel.transaction() as model:
            currentQuest = self.__tankAcademyController.getCurrentQuest()
            completedQuestsCount = self.__tankAcademyController.getCompletedTankAcademyQuestsCount()
            model.setIsCompleted(currentQuest is None)
            model.setIsMainViewVisited(completedQuestsCount == self.__getLastSeenQuestIdx())
            model.setUnobtainedVehiclesCount(len(self.__tankAcademyController.getDelayedRewardCurrencyTokens()))
            if currentQuest is not None:
                currentProgress, maxProgress = self.__tankAcademyController.getQuestProgress(currentQuest)
                model.setQuestNumber(currentQuest.getOrder())
                model.setCurrentProgress(currentProgress)
                model.setMaxProgress(maxProgress)
            if self.__tankAcademyController.isFinished() and self.__tankAcademyController.hasUnobtainedDelayedRewards():
                model.setEndDate(self.__tankAcademyController.getDelayedRewardExpirationTime())
        return

    def __getLastSeenQuestIdx(self):
        return self.__settingsCore.serverSettings.getBattleMattersQuestWasShowed()

    def __onClick(self):
        self.__checkHint()
        showTankAcademy()

    def __checkHint(self):
        entryPointHint = OnceOnlyHints.TANK_ACADEMY_ENTRY_POINT_HINT
        hintShowed = self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(entryPointHint, default=False)
        if not hintShowed:
            self.__settingsCore.serverSettings.setOnceOnlyHintsSettings({entryPointHint: True})


class TankAcademyEntryPointWidget(GFHeaderWidget):
    __slots__ = ()

    def _makeInjectView(self):
        return TankAcademyEntryPointView()
