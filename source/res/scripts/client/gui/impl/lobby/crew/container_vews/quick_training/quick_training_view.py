# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/quick_training/quick_training_view.py
import typing
import SoundGroups
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.quick_training.quick_training_view_model import QuickTrainingViewModel
from gui.impl.lobby.container_views.base.components import ContainerBase
from gui.impl.lobby.crew.base_crew_view import BaseCrewWidgetView
from gui.impl.lobby.crew.container_vews.quick_training.components.freexp_book_component import FreeXpBookComponent
from gui.impl.lobby.crew.container_vews.quick_training.components.books_list_component import BooksListComponent
from gui.impl.lobby.crew.container_vews.quick_training.components.learning_results_component import LearningResultsComponent
from gui.impl.lobby.crew.container_vews.quick_training.components.mentoring_license_component import MentoringLicenseComponent
from gui.impl.lobby.crew.container_vews.quick_training.components.tips_list_component import TipsListComponent
from gui.impl.lobby.crew.container_vews.quick_training.context import QuickTrainingViewContext
from gui.impl.lobby.crew.container_vews.quick_training.controller import QuickTrainingInteractionController
from gui.impl.lobby.crew.crew_sounds import SOUNDS
from gui.impl.lobby.crew.widget.crew_widget import QuickTrainingCrewWidget
from gui.shared import event_dispatcher
from gui.shared.gui_items.Tankman import NO_TANKMAN
from gui.shared.gui_items.Vehicle import NO_VEHICLE_ID
if typing.TYPE_CHECKING:
    from typing import List, Type
    from gui.impl.lobby.container_views.base.components import ComponentBase
    from gui.impl.lobby.container_views.base.controllers import InteractionController

class QuickTrainingView(ContainerBase, BaseCrewWidgetView):

    def __init__(self, layoutID=R.views.lobby.crew.QuickTrainingView(), **kwargs):
        settings = ViewSettings(layoutID=layoutID, flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=QuickTrainingViewModel(), kwargs=kwargs)
        super(QuickTrainingView, self).__init__(settings, **kwargs)

    def _getComponents(self):
        return [FreeXpBookComponent(key='freeXp', parent=self),
         BooksListComponent(key='books_list', parent=self),
         LearningResultsComponent(key='learning_results', parent=self),
         MentoringLicenseComponent(key='mentoring_entry', parent=self),
         TipsListComponent(key='tips_list', parent=self)]

    def _getContext(self, *args, **kwargs):
        return QuickTrainingViewContext(kwargs.get('vehicleInvID', NO_VEHICLE_ID), kwargs.get('tankmanInvID', NO_TANKMAN))

    def _getInteractionControllerCls(self):
        return QuickTrainingInteractionController

    def _getEvents(self):
        return super(QuickTrainingView, self)._getEvents() + ((self.viewModel.mouseLeave, self._onCardMouseLeave), (self.viewModel.goToProfile, self._goToProfile))

    def _getCallbacks(self):
        return (('inventory', self._onInventoryChange),
         ('goodies', self._onGoodiesUpdate),
         ('stats.freeXP', self._onFreeXpChange),
         ('stats.XPpp', self._onFreeXpChange))

    def _onLoading(self, *args, **kwargs):
        super(QuickTrainingView, self)._onLoading(*args, **kwargs)
        crewBooksViewedCache().addViewedItems(self.context.vehicle.nationID)

    def _onLoaded(self, *args, **kwargs):
        super(QuickTrainingView, self)._onLoaded(*args, **kwargs)
        SoundGroups.g_instance.playSound2D(SOUNDS.CREW_BOOKS_ENTRANCE)
        self.crewWidget.updateSlotIdx(self.context.slotIdx)

    def _fillViewModel(self, vm):
        if self.context.tankman is not None:
            vm.setTankmanName(self.context.tankman.getFullUserNameWithSkin())
        if bool(self.gui.windowsManager.findViews(lambda view: view.layoutID == R.views.lobby.crew.personal_case.PersonalFileView())):
            vm.setBackButtonLabel(R.strings.crew.common.navigation.toPersonalFile())
        if self.context.vehicle:
            vm.setNationName(self.context.vehicle.nationName)
            vm.setVehicleName(self.context.vehicle.shortUserName)
        vm.setIsAnyTankmanHasPerkLimit(self.context.hasCrewMaxedTman)
        vm.setIsWholeCrewHasPerkLimit(self.context.isAllCrewMaxTrained)
        vm.setIsCurrentTankmanHasPerkLimit(self.context.isCurrTmanMaxTrained)
        vm.setIsCurrentTankmanHasLowEfficiency(not self.context.hasCurrTmanMaxSkillsEfficiency)
        return

    @property
    def viewModel(self):
        return super(QuickTrainingView, self).getViewModel()

    def onBringToFront(self, parentWindow):
        super(QuickTrainingView, self).onBringToFront(parentWindow)
        if parentWindow != self.getWindow():
            self.destroyWindow()

    def _getCrewWidgetBaseData(self):
        return (QuickTrainingCrewWidget, QuickTrainingCrewWidget.LAYOUT_DYN_ACCESSOR())

    def _onTankmanSlotClick(self, tankmanID, slotIdx):
        self.interactionCtrl.onChangeTankman(tankmanID, slotIdx)

    def _onEmptySlotClick(self, tankmanID, slotIdx):
        self.interactionCtrl.onEmptyWidgetSlotClick(tankmanID, slotIdx)

    def _onTankmanSlotAutoSelect(self, tankmanID, slotIdx):
        self.interactionCtrl.onChangeTankman(tankmanID, slotIdx)

    def _onInventoryChange(self, invDiff):
        self.interactionCtrl.onInventoryUpdate(invDiff)

    def _onGoodiesUpdate(self, diff):
        self.interactionCtrl.onGoodiesUpdate(diff)

    def _onFreeXpChange(self, *_):
        self.interactionCtrl.onGlobalFreeXpChange()

    def _onAbout(self):
        self.interactionCtrl.onAbout()

    def _onCardMouseLeave(self):
        self.interactionCtrl.onCardMouseLeave()

    def _goToProfile(self):
        _, _, currentTankman = self.crewWidget.getWidgetData()
        if currentTankman:
            currentViewID = self.crewWidget.currentViewID
            event_dispatcher.showPersonalCase(currentTankman.invID, previousViewID=currentViewID)

    def setSelectedTman(self, tankmanID, slotIdx):
        self.interactionCtrl.onChangeTankman(tankmanID, slotIdx)
