# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/skills_training/skills_training_view.py
import typing
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.game_control.wot_plus_crew_assist import CrewAssistantCtrl
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.skills_training_view_model import SkillsTrainingViewModel
from gui.impl.gen.view_models.views.lobby.crew.sort_dropdown_item_model import SortingTypeEnum, SortDropdownItemModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.container_views.base.components import ContainerBase
from gui.impl.lobby.container_views.base.controllers import InteractionController
from gui.impl.lobby.crew.container_vews.skills_training import loadSortingOrderType, saveSortingOrderType
from gui.impl.lobby.crew.container_vews.skills_training.components.skills_list_component import SkillsListComponent
from gui.impl.lobby.crew.container_vews.skills_training.context import SkillsTrainingViewContext
from gui.impl.lobby.crew.container_vews.skills_training.controller import SkillsTrainingInteractionController
from gui.impl.lobby.crew.crew_helpers import tankmanHasCrewAssistOrderSets
from gui.impl.lobby.crew.tooltips.sorting_dropdown_tooltip import SortingDropdownTooltip
from gui.impl.lobby.crew.widget.crew_widget import CrewWidget, SkillsTrainingCrewWidget
from gui.impl.lobby.hangar.sub_views.vehicle_params_view import VehicleSkillPreviewParamsPresenter
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_bus import SharedEvent
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController, IWotPlusController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import List, Type
    from gui.impl.lobby.container_views.base.components import ComponentBase

class SkillsTrainingView(ContainerBase, ViewImpl):
    __slots__ = ('_crewWidget', '_paramsView')
    platoonCtrl = dependency.descriptor(IPlatoonController)
    itemsCache = dependency.descriptor(IItemsCache)
    wotPlus = dependency.descriptor(IWotPlusController)
    _SKILLS_COMPONENT_NAME = 'skills_list'

    def __init__(self, **kwargs):
        self._crewWidget = None
        self._paramsView = None
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

    def createToolTipContent(self, event, contentID):
        sortingDDlayoutId = R.views.lobby.crew.tooltips.SortingDropdownTooltip()
        return SortingDropdownTooltip(sortingDDlayoutId, event.getArgument('isWarningShown', False), event.getArgument('isSortingDisabled', False)) if contentID == sortingDDlayoutId else super(SkillsTrainingView, self).createToolTipContent(event, contentID)

    def _getComponents(self):
        return [SkillsListComponent(key=self._SKILLS_COMPONENT_NAME, parent=self)]

    def _getContext(self, *args, **kwargs):
        return SkillsTrainingViewContext(kwargs.get('tankmanID'), kwargs.get('role'))

    def _getInteractionControllerCls(self):
        return SkillsTrainingInteractionController

    def _getEvents(self):
        return ((self._crewWidget.onSlotClick, self._onWidgetSlotClick),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onSortingSelectionChange, self.__onSortSelectionChanged),
         (g_playerEvents.onDisconnected, self.__onDisconnected),
         (self.platoonCtrl.onMembersUpdate, self.__onMembersUpdate),
         (self.wotPlus.onEnabledStatusChanged, self.__onEnabledStatusChanged))

    def _onLoading(self, *args, **kwargs):
        self._crewWidget = SkillsTrainingCrewWidget(tankmanID=self.context.tankmanID, currentViewID=R.views.lobby.crew.SkillsTrainingView(), previousViewID=R.views.lobby.crew.TankmanContainerView(), isButtonBarVisible=False)
        slotIdx, _, __ = self._crewWidget.getWidgetData()
        self.setChildView(CrewWidget.LAYOUT_DYN_ACCESSOR(), self._crewWidget)
        self._crewWidget.updateSlotIdx(slotIdx)
        self._paramsView = VehicleSkillPreviewParamsPresenter()
        self.setChildView(R.views.lobby.hangar.subViews.VehicleParams(), self._paramsView)
        super(SkillsTrainingView, self)._onLoading(**kwargs)

    def _subscribe(self):
        super(SkillsTrainingView, self)._subscribe()
        g_eventBus.addListener(CrewAssistantCtrl.CREW_ASSIST_DATA_CHANGED, self.__onCrewAssistDataChanged, scope=EVENT_BUS_SCOPE.LOBBY)

    def _unsubscribe(self):
        g_eventBus.removeListener(CrewAssistantCtrl.CREW_ASSIST_DATA_CHANGED, self.__onCrewAssistDataChanged, scope=EVENT_BUS_SCOPE.LOBBY)
        super(SkillsTrainingView, self)._unsubscribe()

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
        if self.context.tankman.vehicleDescr:
            vehicle = self.itemsCache.items.getVehicle(self.context.tankman.vehicleInvID)
            fillVehicleInfo(vm.vehicleInfo, vehicle, separateIGRTag=True)
            vm.setIsTankmanInVehicle(True)
        else:
            vm.setIsTankmanInVehicle(False)
        self.__fillSortingDropDown(vm, loadSortingOrderType())

    def _finalize(self):
        super(SkillsTrainingView, self)._finalize()
        self._crewWidget = None
        self._paramsView = None
        return

    def _onWidgetSlotClick(self, tankmanInvID, slotIdx):
        self.interactionCtrl.onChangeTankman(tankmanInvID, slotIdx)

    def __onClose(self):
        self.interactionCtrl.eventsProvider.onClose()

    @args2params(int)
    def __onSortSelectionChanged(self, sortingType):
        saveSortingOrderType(sortingType)
        self.__refreshSorting(sortingType)

    def __refreshSorting(self, sortingType):
        with self.viewModel.transaction() as vm:
            self.__fillSortingDropDown(vm, sortingType)
            self.__refreshSkillsComponent(vm)

    def __onDisconnected(self):
        self.destroyWindow()

    def __onMembersUpdate(self):
        self.destroyWindow()

    def __onEnabledStatusChanged(self, _):
        self.__refreshSorting(loadSortingOrderType())

    def __refreshSkillsComponent(self, vm=None):
        skillsCmp = self.components[self._SKILLS_COMPONENT_NAME]
        skillsCmp.refreshView(vm)

    def __createDropDownViewModel(self, mType, isSelected, isEnabled):
        vm = SortDropdownItemModel()
        vm.setIsSelected(isSelected)
        vm.setIsEnabled(isEnabled)
        vm.setMType(mType)
        return vm

    def __fillSortingDropDown(self, vm, storedPresetVal):
        dropdownItems = vm.getSortingDropDownItems()
        dropdownItems.clear()
        if self.wotPlus.isCrewAssistEnabled():
            hasCommonSet, hasLegendarySet = tankmanHasCrewAssistOrderSets(self.context.tankman, self.context.role)
            showWarning = False
            dropdownItems.reserve(3)
            if storedPresetVal == SortingTypeEnum.COMMON.value:
                if not hasCommonSet:
                    storedPresetVal = SortingTypeEnum.DEFAULT.value
                    showWarning = True
            elif storedPresetVal == SortingTypeEnum.LEGENDARY.value:
                if not hasLegendarySet:
                    storedPresetVal = SortingTypeEnum.DEFAULT.value
                    showWarning = True
            vm.setShowSortingSelectionWarning(showWarning)
            dropdownItems.addViewModel(self.__createDropDownViewModel(SortingTypeEnum.DEFAULT, isSelected=storedPresetVal == SortingTypeEnum.DEFAULT.value, isEnabled=hasCommonSet or hasLegendarySet))
            dropdownItems.addViewModel(self.__createDropDownViewModel(SortingTypeEnum.COMMON, isSelected=storedPresetVal == SortingTypeEnum.COMMON.value, isEnabled=hasCommonSet))
            dropdownItems.addViewModel(self.__createDropDownViewModel(SortingTypeEnum.LEGENDARY, isSelected=storedPresetVal == SortingTypeEnum.LEGENDARY.value, isEnabled=hasLegendarySet))
        dropdownItems.invalidate()

    def __onCrewAssistDataChanged(self, _):
        self.__refreshSorting(loadSortingOrderType())


class SkillsTrainingWindow(WindowImpl):
    __slots__ = ('_blur', '_callback')

    def __init__(self, **kwargs):
        self._blur = None
        self._callback = kwargs.get('callback')
        super(SkillsTrainingWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=SkillsTrainingView(**kwargs), layer=WindowLayer.FULLSCREEN_WINDOW)
        return

    def _initialize(self):
        super(SkillsTrainingWindow, self)._initialize()
        self._blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)

    def _finalize(self):
        self._blur.fini()
        self._blur = None
        try:
            try:
                self._callback(self.content.context.tankmanID)
                self._callback = None
            except AttributeError:
                pass

        finally:
            super(SkillsTrainingWindow, self)._finalize()

        return
