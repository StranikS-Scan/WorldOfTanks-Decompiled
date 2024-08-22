# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/personal_file/controller.py
import typing
from Event import Event
from frameworks.wulf import ViewStatus
from gui.impl.dialogs.dialogs import showPerksDropDialog
from gui.impl.gen import R
from gui.impl.lobby.crew.container_vews.common.base_personal_case_controller import BasePersonalCaseController
from gui.impl.lobby.crew.container_vews.personal_file.events import PersonalFileComponentViewEvents
from gui.impl.lobby.crew.quick_training_view import QuickTrainingView
from gui.shared.event_dispatcher import showQuickTraining, showSkillsTraining, showCrewPostProgressionView
from gui.shared.gui_items.Vehicle import NO_VEHICLE_ID
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Callable, List, Tuple
    from gui.impl.lobby.container_views.base.events import ComponentEventsBase

class PersonalFileInteractionController(BasePersonalCaseController):
    __guiLoader = dependency.descriptor(IGuiLoader)
    __isPerksResetDialogLoading = False

    def _getEventsProvider(self):
        return PersonalFileComponentViewEvents()

    def _getEvents(self):
        return super(PersonalFileInteractionController, self)._getEvents() + [(self.__guiLoader.windowsManager.onViewStatusChanged, self._onViewStatusChanged),
         (self.itemsCache.onSyncCompleted, self._onCacheResync),
         (self.eventsProvider.onSkillClick, self._onSkillClick),
         (self.eventsProvider.onSetAnimationInProgress, self._onSetAnimationInProgress),
         (self.eventsProvider.onIncreaseClick, self._onIncreaseClick),
         (self.eventsProvider.onResetClick, self._onResetClick),
         (self.eventsProvider.onWidgetClick, self._onWidgetClick)]

    def _onSkillClick(self, tankmanInvID, role):
        self.view.hideContent()
        showSkillsTraining(tankmanInvID, role, self._onSkillsTrained)

    def _onSkillsTrained(self, tankmanID):
        self.view.showContent()
        self.view.getParentView().updateTankmanId(tankmanID)

    def _onSetAnimationInProgress(self, isEnabled):
        self.view.setAnimationInProgress(isEnabled)

    def _onIncreaseClick(self):
        tankman = self.context.tankman
        vehicleInvID = tankman.vehicleInvID if tankman and tankman.isInTank else NO_VEHICLE_ID
        showQuickTraining(tankmanInvID=tankman.invID, vehicleInvID=vehicleInvID, previousViewID=R.views.lobby.crew.TankmanContainerView())

    @wg_async
    def _onResetClick(self, tankmanID):
        if self.__isPerksResetDialogLoading:
            return
        self.__isPerksResetDialogLoading = True
        yield wg_await(showPerksDropDialog(tankmanID))
        self.__isPerksResetDialogLoading = False

    def _onWidgetClick(self):
        showCrewPostProgressionView()

    def _onViewStatusChanged(self, uniqueID, newState):
        view = self.__guiLoader.windowsManager.getView(uniqueID)
        if isinstance(view, QuickTrainingView):
            if newState == ViewStatus.CREATED:
                self.view.updateAnimationShowing(False)
            elif newState == ViewStatus.DESTROYING:
                self.view.updateAnimationShowing(True)

    def _onCacheResync(self, reason, _):
        if reason in (CACHE_SYNC_REASON.STATS_RESYNC, CACHE_SYNC_REASON.SHOW_GUI):
            return
        else:
            tankman = self.itemsCache.items.getTankman(self.view.context.tankman.invID)
            if tankman is None:
                return
            self.onChangeTankman(tankman.invID)
            return

    def onChangeTankman(self, tankmanID):
        self.context.update(tankmanID, skillAnimationsSkipped=False)
        self.refresh()

    def onStopAnimations(self):
        self.context.update(skillAnimationsSkipped=True)
        self.refresh()
