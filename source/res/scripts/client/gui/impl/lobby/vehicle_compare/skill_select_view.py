# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/skill_select_view.py
from copy import deepcopy
import typing
from constants import NEW_PERK_SYSTEM as NPS
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer, WindowFlags, Array
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_view import CrewSkillsManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.vehicle_compare.skill_select_item_model import SkillSelectItemModel, SkillState, SkillType
from gui.impl.gen.view_models.views.lobby.vehicle_compare.skill_select_row_model import SkillSelectRowModel
from gui.impl.gen.view_models.views.lobby.vehicle_compare.skill_select_view_model import SkillSelectViewModel
from gui.impl.lobby.hangar.sub_views.vehicle_params_view import VehicleCompareParamsView
from gui.impl.lobby.vehicle_compare.crew_roles_tooltip_view import CrewRolesTooltipView
from gui.impl.pub import ViewImpl
from gui.impl.pub import WindowImpl
from gui.shared.gui_items.Tankman import crewMemberRealSkillLevel
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from items.components.skills_constants import COMMON_ROLE, SKILLS_BY_ROLES, COMMON_SKILLS
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from PlayerEvents import g_playerEvents
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_view import VehicleCompareConfiguratorMain
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.gui_items.Tankman import TankmanSkill
    from typing import List

def _fillRowModel(vm, role, maxCount, currentCount, tankmanIdx):
    vm.setRole(role)
    vm.setPossibleMaxSelected(maxCount)
    vm.setSelectedAmount(currentCount)
    vm.setTankmanIdx(tankmanIdx)


def _fillSkills(skillsList, skillsVL, selectedSkills, isMaxSelected):
    for skill in skillsList:
        skillVM = SkillSelectItemModel()
        skillName = skill.name
        skillVM.setName(skillName)
        defaultState = SkillState.DISABLED if isMaxSelected else SkillState.DEFAULT
        skillVM.setState(SkillState.SELECTED if skillName in selectedSkills else defaultState)
        skillsVL.addViewModel(skillVM)


def _updateRow(vm, selectedSkills, skillType):
    role = str(vm.getRole())
    count, isMaxSelected = _getSkillsCountByRole(role, selectedSkills, skillType)
    defaultState = SkillState.DISABLED if isMaxSelected else SkillState.DEFAULT
    vm.setSelectedAmount(count)
    skillsVl = vm.getSkills()
    _updateSkills(skillsVl, selectedSkills, defaultState)
    if skillType != SkillType.BONUS.value:
        skillsVl = vm.getCommonSkills()
        _updateSkills(skillsVl, selectedSkills, defaultState)


def _updateSkills(skillsVl, selectedSkills, defaultState):
    for skill in skillsVl:
        skill.setState(SkillState.SELECTED if skill.getName() in selectedSkills else defaultState)

    skillsVl.invalidate()


def _getRowModel(vm, rowIndex, skillType):
    return vm.getBonusSkillRows().getValue(rowIndex) if skillType == SkillType.BONUS.value else vm.getMajorSkillRows().getValue(rowIndex)


def _getSkillModel(rowVM, skillIndex, skillType):
    if skillType == SkillType.MAJOR.value:
        return rowVM.getSkills().getValue(skillIndex)
    return rowVM.getCommonSkills().getValue(skillIndex) if skillType == SkillType.COMMON.value else rowVM.getSkills().getValue(skillIndex)


def _getSkillsCountByRole(role, selectedSkills, skillType):
    skills = SKILLS_BY_ROLES.get(role).intersection(selectedSkills)
    if skillType != SkillType.BONUS.value:
        count = len(skills)
        return (count, count >= NPS.MAX_MAJOR_PERKS)
    count = len(skills.difference(COMMON_SKILLS))
    return (count, count >= NPS.MAX_BONUS_SKILLS_PER_ROLE)


class SkillSelectView(ViewImpl):
    __slots__ = ('__paramsView', '__toolTipMgr', '__cmpConf', '__skillsManager', '__selectedSkills', '__vehicle')
    itemsCache = dependency.descriptor(IItemsCache)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, layoutID=R.views.lobby.vehicle_compare.SkillSelectView(), *args, **kwargs):
        settings = ViewSettings(layoutID, flags=ViewFlags.VIEW, model=SkillSelectViewModel(), args=args, kwargs=kwargs)
        self.__cmpConf = cmp_helpers.getCmpConfiguratorMainView()
        lvl = self.__cmpConf.getCurrentCrewSkillLevel()
        skills = self.__cmpConf.getCurrentCrewSkills()
        self.__vehicle = self.__cmpConf.getCurrentVehicleCopy()
        self.__selectedSkills = deepcopy(skills)
        self.__skillsManager = CrewSkillsManager(self.__vehicle, lvl, skills)
        self.__paramsView = None
        self.__toolTipMgr = self.__appLoader.getApp().getToolTipMgr()
        super(SkillSelectView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(SkillSelectView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TooltipConstants.SKILL:
                skillName = str(event.getArgument('skillName'))
                level = round(crewMemberRealSkillLevel(self.__skillsManager.getVehicle(), skillName), 2)
                args = [skillName, None, level]
                self.__toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_PERK_GF, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return TOOLTIPS_CONSTANTS.CREW_PERK_GF
        return super(SkillSelectView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return CrewRolesTooltipView(self.__vehicle) if contentID == R.views.lobby.vehicle_compare.tooltips.CrewRolesTooltip() else super(SkillSelectView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(SkillSelectView, self)._onLoading(*args, **kwargs)
        initVehicle, _ = self.__cmpConf.getInitialVehicleData()
        changedVehicle = self.__skillsManager.getVehicle()
        self.__paramsView = VehicleCompareParamsView(initVehicle, changedVehicle)
        self.setChildView(R.views.lobby.hangar.subViews.VehicleParams(), self.__paramsView)
        self._fillModel()

    def _fillModel(self):
        vehicle = self.__skillsManager.getVehicle()
        with self.viewModel.transaction() as vm:
            fillVehicleInfo(vm.vehicleInfo, vehicle, separateIGRTag=True)
            majorRows = vm.getMajorSkillRows()
            bonusRows = vm.getBonusSkillRows()
            majorRows.clear()
            bonusRows.clear()
            for slotIdx, tankman in vehicle.crew:
                _, selectedSkills = self.__selectedSkills.get(slotIdx, (None, []))
                possibleSkills = tankman.getPossibleSkillsByRole()
                bonusRoles = list(tankman.roles())
                mainRole = bonusRoles.pop(0)
                selectedCount, isMaxSelected = _getSkillsCountByRole(mainRole, selectedSkills, SkillType.MAJOR.value)
                majorSkillsVM = SkillSelectRowModel()
                _fillRowModel(majorSkillsVM, mainRole, NPS.MAX_MAJOR_PERKS, selectedCount, slotIdx)
                skills = possibleSkills.get(mainRole, [])
                commonSkills = possibleSkills.get(COMMON_ROLE, [])
                skillsVL = majorSkillsVM.getSkills()
                commonSkillsVL = majorSkillsVM.getCommonSkills()
                skillsVL.clear()
                commonSkillsVL.clear()
                _fillSkills(skills, skillsVL, selectedSkills, isMaxSelected)
                _fillSkills(commonSkills, commonSkillsVL, selectedSkills, isMaxSelected)
                for bonusRole in bonusRoles:
                    selectedCount, isMaxSelected = _getSkillsCountByRole(bonusRole, selectedSkills, SkillType.BONUS.value)
                    bonusSkillsVM = SkillSelectRowModel()
                    _fillRowModel(bonusSkillsVM, bonusRole, NPS.MAX_BONUS_SKILLS_PER_ROLE, selectedCount, slotIdx)
                    bonusSkills = possibleSkills.get(bonusRole, [])
                    bonusSkillsVL = bonusSkillsVM.getSkills()
                    bonusSkillsVL.clear()
                    _fillSkills(bonusSkills, bonusSkillsVL, selectedSkills, isMaxSelected)
                    bonusRows.addViewModel(bonusSkillsVM)

                majorRows.addViewModel(majorSkillsVM)

            majorRows.invalidate()
            bonusRows.invalidate()
            self.__updateActionButtons(vm)
        return

    def _getEvents(self):
        return ((self.viewModel.onRestore, self._onRestore),
         (self.viewModel.onCancel, self._onCancel),
         (self.viewModel.onClose, self._onClose),
         (self.viewModel.onConfirm, self._onConfirm),
         (self.viewModel.onClick, self._onClick),
         (g_playerEvents.onDisconnected, self._onClose))

    def _finalize(self):
        self.__paramsView = None
        self.__toolTipMgr = None
        self.__cmpConf = None
        self.__skillsManager = None
        self.__selectedSkills = None
        super(SkillSelectView, self)._finalize()
        return

    def _onClose(self):
        self.destroyWindow()

    def _onConfirm(self):
        self.__cmpConf.selectCrewSkills(self.__selectedSkills)
        self.destroyWindow()

    def _onCancel(self):
        self.destroyWindow()

    def _onRestore(self):
        self.__selectedSkills = self.__cmpConf.getCurrentCrewSkills()
        self._fillModel()

    def _onClick(self, event):
        self.__updateSkills(int(event.get('rowIndex')), int(event.get('skillIndex')), event.get('skillType'))

    def __updateSkills(self, rowIndex, skillIndex, skillType):
        with self.viewModel.transaction() as vm:
            rowVM = _getRowModel(vm, rowIndex, skillType)
            skillVM = _getSkillModel(rowVM, skillIndex, skillType)
            skillState = skillVM.getState()
            skillName = skillVM.getName()
            tmanSlotIdx = int(rowVM.getTankmanIdx())
            _, selectedSkills = self.__selectedSkills[tmanSlotIdx]
            if skillState == SkillState.SELECTED:
                selectedSkills.remove(skillName)
            elif skillState == SkillState.DEFAULT:
                selectedSkills.append(skillName)
            self.__skillsManager.updateSkills(self.__selectedSkills)
            self.__paramsView.update()
            _updateRow(rowVM, selectedSkills, skillType)
            self.__updateActionButtons(vm)

    def __updateActionButtons(self, vm):
        isSame = True
        defaultSkills = self.__cmpConf.getCurrentCrewSkills()
        for idx, (_, skills) in defaultSkills.items():
            _, selectedSkills = self.__selectedSkills.get(idx, ('', []))
            selectedSet = set(selectedSkills)
            defaultSet = set(skills)
            isSame = selectedSet == defaultSet
            if not isSame:
                break

        vm.setIsActionsDisable(isSame)


class SkillSelectWindow(WindowImpl):
    __slots__ = ('__blur',)

    def __init__(self):
        super(SkillSelectWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW, content=SkillSelectView())
        self.__blur = None
        return

    def load(self):
        if self.__blur is None:
            self.__blur = CachedBlur(enabled=True, ownLayer=self.layer - 1, uiBlurRadius=35)
        super(SkillSelectWindow, self).load()
        return

    def _finalize(self):
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        super(SkillSelectWindow, self)._finalize()
        return
