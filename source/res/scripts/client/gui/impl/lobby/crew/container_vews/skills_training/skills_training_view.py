# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/skills_training/skills_training_view.py
import typing
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.skills_training_view_model import SkillsTrainingViewModel
from gui.impl.lobby.container_views.base.components import ContainerBase
from gui.impl.lobby.container_views.base.controllers import InteractionController
from gui.impl.lobby.crew.container_vews.skills_training.components.skills_list_component import SkillsListComponent
from gui.impl.lobby.crew.container_vews.skills_training.context import SkillsTrainingViewContext
from gui.impl.lobby.crew.container_vews.skills_training.controller import SkillsTrainingInteractionController
from gui.impl.lobby.crew.widget.crew_widget import CrewWidget, SkillsTrainingCrewWidget
from gui.impl.lobby.hangar.sub_views.vehicle_params_view import VehicleSkillPreviewParamsView
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.view_helpers.blur_manager import CachedBlur
if typing.TYPE_CHECKING:
    from typing import List, Type
    from gui.impl.lobby.container_views.base.components import ComponentBase

class SkillsTrainingView(ContainerBase, ViewImpl):
    __slots__ = ('_crewWidget', '_paramsView', '_callback')

    def __init__(self, **kwargs):
        self._crewWidget = None
        self._paramsView = None
        self._callback = kwargs.get('callback')
        settings = ViewSettings(R.views.lobby.crew.SkillsTrainingView())
        settings.model = SkillsTrainingViewModel()
        super(SkillsTrainingView, self).__init__(settings, **kwargs)
        return

    @property
    def crewWidget(self):
        return self._crewWidget

    @property
    def paramsView(self):
        return self._paramsView

    @property
    def viewModel(self):
        return super(SkillsTrainingView, self).getViewModel()

    def destroyWindow(self):
        self._callback(self.context.tankmanID)
        super(SkillsTrainingView, self).destroyWindow()

    def _getComponents(self):
        return [SkillsListComponent(key='skills_list', parent=self)]

    def _getContext(self, *args, **kwargs):
        return SkillsTrainingViewContext(kwargs.get('tankmanID'), kwargs.get('role'))

    def _getInteractionControllerCls(self):
        return SkillsTrainingInteractionController

    def _getEvents(self):
        return ((self._crewWidget.onSlotClick, self._onWidgetSlotClick), (self.viewModel.onClose, self.__onClose), (g_playerEvents.onDisconnected, self.__onDisconnected))

    def _onLoading(self, *args, **kwargs):
        self._crewWidget = SkillsTrainingCrewWidget(tankmanID=self.context.tankmanID, currentViewID=R.views.lobby.crew.SkillsTrainingView(), previousViewID=R.views.lobby.crew.TankmanContainerView(), isButtonBarVisible=False)
        slotIdx, _, __ = self._crewWidget.getWidgetData()
        self.setChildView(CrewWidget.LAYOUT_DYN_ACCESSOR(), self._crewWidget)
        self._crewWidget.updateSlotIdx(slotIdx)
        self._paramsView = VehicleSkillPreviewParamsView()
        self.setChildView(R.views.lobby.hangar.subViews.VehicleParams(), self._paramsView)
        super(SkillsTrainingView, self)._onLoading(**kwargs)

    def _fillViewModel(self, vm):
        currSkillsAmount, availableSkillsAmount = self.context.skillsAmount
        vm.setCurrentSkillsAmount(currSkillsAmount)
        vm.setAvailableSkillsAmount(availableSkillsAmount)
        vm.setIsFemale(self.context.tankman.isFemale)
        vm.setIsMajorQualification(self.context.isMajorQualification)
        vm.setRole(self.context.role)
        vm.setTotalSkillsAmount(self.context.totalSkillsAmount)
        vm.setAreAllSkillsLearned(self.context.areAllSkillsLearned)
        vm.setSkillsEfficiency(self.context.tankman.currentVehicleSkillsEfficiency)
        vm.setIsAnySkillSelected(self.context.isAnySkillSelected)
        if self.context.tankmanCurrentVehicle:
            fillVehicleInfo(vm.vehicleInfo, self.context.tankmanCurrentVehicle, separateIGRTag=True)

    def _finalize(self):
        super(SkillsTrainingView, self)._finalize()
        self._crewWidget = None
        self._paramsView = None
        self._callback = None
        return

    def _onWidgetSlotClick(self, tankmanInvID, slotIdx):
        if tankmanInvID != self.context.tankmanID:
            self.interactionCtrl.onChangeTankman(tankmanInvID, slotIdx)

    def __onClose(self):
        self.interactionCtrl.eventsProvider.onClose()

    def __onDisconnected(self):
        self.destroyWindow()


class SkillsTrainingWindow(WindowImpl):
    __slots__ = ('_blur',)

    def __init__(self, **kwargs):
        self._blur = None
        super(SkillsTrainingWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=SkillsTrainingView(**kwargs), layer=WindowLayer.FULLSCREEN_WINDOW)
        return

    def _initialize(self):
        super(SkillsTrainingWindow, self)._initialize()
        self._blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)

    def _finalize(self):
        self._blur.fini()
        self._blur = None
        super(SkillsTrainingWindow, self)._finalize()
        return
