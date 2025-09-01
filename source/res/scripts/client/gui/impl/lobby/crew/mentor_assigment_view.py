# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/mentor_assigment_view.py
import json
from typing import TYPE_CHECKING, Optional
import SoundGroups
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer, WindowFlags
from goodies import goodie_constants
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.dialogs.dialogs import showMentorAssignmentConfirmDialog
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.info_tip_model import InfoTipModel, TipType
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.mentor_assigment_tankman_model import MentorAssigmentTankmanModel
from gui.impl.gen.view_models.views.lobby.crew.mentor_assigment_view_model import MentorAssigmentViewModel
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanCardState
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.crew.base_crew_view import BaseCrewView
from gui.impl.lobby.crew.base_tankman_list_view import BaseTankmanListView
from gui.impl.lobby.crew.crew_helpers.model_setters import setTankmanModel, setTmanSkillsModel
from gui.impl.lobby.crew.crew_helpers.skill_helpers import quickEarnCrewSkills, quickEarnTmanSkills
from gui.impl.lobby.crew.crew_sounds import SOUNDS
from gui.impl.lobby.crew.filter import getTankmanRoleSettings, getVehicleTypeSettings, getVehicleTierSettings, getTankmanLocationSettings
from gui.impl.lobby.crew.filter.data_providers import MentorDataProvider
from gui.impl.lobby.crew.filter.filter_panel_widget import FilterPanelWidget
from gui.impl.lobby.crew.filter.state import FilterState
from gui.impl.lobby.crew.tooltips.mentoring_license_tooltip import MentoringLicenseTooltip
from gui.impl.lobby.crew.utils import getMetoringLicensesAmount
from gui.impl.pub import WindowImpl
from gui.shared.event_dispatcher import showChangeCrewMember
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import NO_TANKMAN, NO_SLOT
from gui.shared.gui_items.Vehicle import NO_VEHICLE_ID
from gui.shared.gui_items.items_actions import factory
from helpers import dependency, i18n
from nations import NAMES
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.shared import IItemsCache
from wg_async import wg_async, wg_await
if TYPE_CHECKING:
    from gui.impl.lobby.crew.widget.crew_widget import QuickTrainingCrewWidget as CrewWidgetType
_POPOVER_GROUP_SETTINGS = (getTankmanRoleSettings(), getVehicleTypeSettings(customTooltipBody=R.strings.crew.filter.tooltip.crewMemberVehicleType.body()), getVehicleTierSettings())
_DEFAULT_TIP_ID = 0
_LOST_XP_TIP_ID = 1

class MentorAssigmentView(BaseCrewView, BaseTankmanListView):
    restore = dependency.descriptor(IRestoreController)
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__dataProvider', '__filterState', '__filterPanelWidget', '__nation', '__vehicleInvID', '__tankmanInvID', '__tankman', '__hasActiveCard', '__parent', '__isDefaultTipVisible', '__isDefaultTipShown')

    def __init__(self, layoutID=R.views.lobby.crew.MentorAssigmentView(), *args, **kwargs):
        settings = ViewSettings(layoutID, flags=ViewFlags.VIEW, model=MentorAssigmentViewModel(), args=args, kwargs=kwargs)
        self.__parent = kwargs.get('parent')
        self.__tankmanInvID = kwargs.get('tankmanInvID', NO_TANKMAN)
        self.__tankman = None
        self.__vehicleInvID = kwargs.get('vehicleInvID', NO_VEHICLE_ID)
        self.__nation = NAMES[self._tankman.nationID]
        self.__hasActiveCard = False
        self.__activeCardTotalXp = 0
        self.__filterState = FilterState()
        self.__dataProvider = MentorDataProvider(self.__filterState, self.__tankmanInvID, self.__nation)
        self.__filterPanelWidget = None
        self.__isDefaultTipVisible = True
        self.__isDefaultTipShown = False
        self._crewWidget = None
        super(MentorAssigmentView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(MentorAssigmentView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId', None)
            if tooltipId == TOOLTIPS_CONSTANTS.MENTOR_ASSIGNMENT:
                toolTipMgr = self.appLoader.getApp().getToolTipMgr()
                targetTmanID = event.getArgument('targetTmanId')
                args = (self.__tankmanInvID, targetTmanID)
                toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.MENTOR_ASSIGNMENT, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return TOOLTIPS_CONSTANTS.MENTOR_ASSIGNMENT
        return super(MentorAssigmentView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId', None)
            if tooltipId == TooltipConstants.MENTOR_FULLY_TRAINED:
                text = backport.text(R.strings.mentoring_license.mentorAssigment.tooltip.fullyTrainedMentor())
                return ExtendedTextTooltip(text, json.dumps({'name': self._tankman.getFullUserNameWithSkin()}))
        return MentoringLicenseTooltip(getMetoringLicensesAmount()) if contentID == R.views.lobby.crew.tooltips.MentoringLicenseTooltip() else super(MentorAssigmentView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(MentorAssigmentView, self)._onLoading(*args, **kwargs)
        self.__dataProvider.update()
        self.__clearWidgetPossibleSkillsLevel()

    @property
    def _tankman(self):
        if self.__tankman is None:
            self.__tankman = self.itemsCache.items.getTankman(self.__tankmanInvID)
        return self.__tankman

    @property
    def _vehicle(self):
        return self.itemsCache.items.getVehicle(self.__vehicleInvID)

    @property
    def _crew(self):
        vehicle = self._vehicle
        return vehicle.crew if vehicle else [(0, self._tankman)]

    def _getCrewWidgetBaseData(self):
        from gui.impl.lobby.crew.widget.crew_widget import QuickTrainingCrewWidget
        return (QuickTrainingCrewWidget, QuickTrainingCrewWidget.LAYOUT_DYN_ACCESSOR())

    def _finalize(self):
        if self.__parent and callable(getattr(self.__parent, 'setSelectedTman', None)):
            currentSlotIdx = self._crewWidget.getSlotIdxByTankmanID(self.__tankmanInvID) if self._tankman.isInTank else 0
            self.__parent.setSelectedTman(self.__tankmanInvID, currentSlotIdx)
        super(MentorAssigmentView, self)._finalize()
        self.__filterState = None
        self.__dataProvider = None
        self.__filterPanelWidget = None
        return

    def _getEvents(self):
        eventsTuple = super(MentorAssigmentView, self)._getEvents()
        return eventsTuple + ((self.viewModel.onResetFilters, self.__onResetFilters),
         (self.viewModel.onLoadCards, self._onLoadCards),
         (self.viewModel.onTankmanSelected, self._onTankmanSelected),
         (self.viewModel.onCardMouseEnter, self._onCardMouseEnter),
         (self.viewModel.onCardMouseLeave, self._onCardMouseLeave),
         (self.viewModel.onTipClose, self._onTipClose),
         (self.viewModel.onTipsReadyToShow, self._onTipsReadyToShow),
         (self.__dataProvider.onDataChanged, self._updateViewModel),
         (self.__filterState.onStateChanged, self._onFilterStateUpdated),
         (g_playerEvents.onDisconnected, self.__onDisconnected))

    def _getCallbacks(self):
        return (('inventory', self.__onInventoryUpdate), ('goodies', self.__onGoodiesUpdate))

    def _updateTankmanData(self):
        self.__dataProvider.reinit(self.__tankmanInvID)
        self.__dataProvider.update()

    def _setWidgets(self, **kwargs):
        super(MentorAssigmentView, self)._setWidgets(**kwargs)
        self.__filterPanelWidget = FilterPanelWidget(getTankmanLocationSettings(False, R.strings.crew.common.filter.location()), _POPOVER_GROUP_SETTINGS, R.strings.crew.filter.popup.default.title(), self.__filterState, title=R.strings.crew.tankmanList.filter.title(), popoverTooltipHeader=R.strings.crew.tankmanList.tooltip.popover.header(), popoverTooltipBody=R.strings.crew.tankmanList.tooltip.popover.body())
        self.setChildView(FilterPanelWidget.LAYOUT_ID(), self.__filterPanelWidget)
        self._updateTankmanData()

    def _onVehicleLockChanged(self, _, lockReason):
        self._updateTankmanData()
        super(MentorAssigmentView, self)._onVehicleLockChanged(_, lockReason)

    def _onEmptySlotClick(self, tankmanID, slotIdx):
        self._destroyParentView()
        showChangeCrewMember(slotIdx, self.__vehicleInvID)
        self.destroyWindow()

    def _onTankmanSlotClick(self, tankmanInvID, slotIdx):
        self.__tankmanInvID = tankmanInvID
        self.__tankman = None
        if not self.__isDefaultTipVisible:
            self.__isDefaultTipShown = False
        self.__isDefaultTipVisible = True
        self._updateTankmanData()
        return

    def _isCrewWidgetButtonBarVisible(self):
        return False

    @property
    def _tankmenProvider(self):
        return self.__dataProvider

    @property
    def _recruitsProvider(self):
        return None

    @property
    def _filterState(self):
        return self.__filterState

    def _fillTankmanCard(self, cardsList, tankman):
        tm = MentorAssigmentTankmanModel()
        setTankmanModel(tm, tankman, tmanNativeVeh=self.itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr), tmanVeh=self.itemsCache.items.getVehicle(tankman.vehicleInvID))
        needXpForMaxSkills = self._tankman.descriptor.needXpForMaxSkills
        totalXP = tankman.descriptor.totalXP()
        tm.setTotalXP(totalXP)
        if needXpForMaxSkills < totalXP:
            tm.setLostXP(totalXP - needXpForMaxSkills)
        if needXpForMaxSkills == 0:
            tm.setCardState(TankmanCardState.DISABLED)
        setTmanSkillsModel(tm.skills, tankman, fillBonusSkills=False)
        cardsList.addViewModel(tm)

    def _fillRecruits(self, cardsList, limit, offset):
        pass

    def _destroyParentView(self):
        if self.__parent:
            self.__parent.destroyWindow()
            self.__parent = None
        return

    @wg_async
    @args2params(int)
    def _onTankmanSelected(self, tankmanID):
        _, result = yield wg_await(showMentorAssignmentConfirmDialog(tankmanID, self.__tankmanInvID))
        if result:
            factory.doAction(factory.TRANSFER_TANKMAN_XP, tankmanID, self.__tankmanInvID)
            self.destroyWindow()

    @args2params(int)
    def _onCardMouseEnter(self, totalXP):
        tankman = self._tankman
        self.__hasActiveCard = True
        self.__activeCardTotalXp = totalXP
        skillsLevels, skillsEffLevels = quickEarnCrewSkills(self._crew, 0, 0, 0)
        tmanSlotIdx = 0 if tankman.vehicleSlotIdx == NO_SLOT else tankman.vehicleSlotIdx
        skillsLevels[tmanSlotIdx], skillsEffLevels[tmanSlotIdx] = quickEarnTmanSkills(tankman, totalXP, ignoreEfficiency=True)
        self._crewWidget.updatePossibleSkillsLevel(skillsLevels, skillsEffLevels)
        with self.viewModel.transaction():
            self.__fillTips()

    def _onCardMouseLeave(self):
        if self.__hasActiveCard:
            self.__hasActiveCard = False
            self.__activeCardTotalXp = 0
            self.__clearWidgetPossibleSkillsLevel()
            with self.viewModel.transaction():
                self.__fillTips()

    @args2params(int)
    def _onTipClose(self, tipId):
        if tipId == _DEFAULT_TIP_ID:
            self.__isDefaultTipVisible = False
            with self.viewModel.transaction():
                self.__fillTips()

    def _onTipsReadyToShow(self):
        with self.viewModel.transaction():
            self.__fillTips()

    def _onClose(self, params=None):
        self.destroyWindow()

    def _onBack(self):
        self._destroyParentView()
        self._destroySubViews()
        self.destroyWindow()

    def _onFilterStateUpdated(self):
        self.__dataProvider.update()

    def _fillRecruitCard(self, cardsList, recruitInfo):
        pass

    def _fillViewModel(self, vm):
        super(MentorAssigmentView, self)._fillViewModel(vm)
        vm.setNation(self.__nation)
        vm.setLicensesAmount(getMetoringLicensesAmount())
        vm.setHasFilters(self.__filterPanelWidget.hasAppliedFilters())
        vm.setSelectedTankmanID(self.__tankmanInvID)
        self._fillTankmenList(vm)
        if self.__isDefaultTipShown:
            self.__fillTips()

    def _fillTankmenList(self, tx):
        self.__filterPanelWidget.updateAmountInfo(self.__dataProvider.itemsCount, self.__dataProvider.initialItemsCount)
        self.__filterPanelWidget.applyStateToModel()
        tx.setItemsAmount(self.__dataProvider.itemsCount)
        tx.setItemsOffset(self._itemsOffset)
        self._fillVisibleCards(tx.getTankmanList())

    def _setBackButtonLabel(self, vm):
        vm.setBackButtonLabel(R.strings.crew.common.navigation.toBarracks() if not self._isHangar else R.invalid())

    def __fillTips(self):
        tips = self.viewModel.getTips()
        tips.clear()
        if self.__isDefaultTipVisible and self._tankman.descriptor.needXpForMaxSkills > 0 and self.__dataProvider.itemsCount > 0:
            if not self.__isDefaultTipShown:
                SoundGroups.g_instance.playSound2D(SOUNDS.CREW_TIPS_NOTIFICATION)
                self.__isDefaultTipShown = True
            tip = InfoTipModel()
            text = backport.text(R.strings.mentoring_license.mentorAssigment.tips.info())
            tip.setId(_DEFAULT_TIP_ID)
            tip.setText(i18n.makeString(text, name=self._tankman.getFullUserNameWithSkin()))
            tip.setType(TipType.INFO)
            tips.addViewModel(tip)
        if self.__hasActiveCard and self._tankman.descriptor.needXpForVeteran < self.__activeCardTotalXp:
            tip = InfoTipModel()
            tip.setId(_LOST_XP_TIP_ID)
            text = backport.text(R.strings.mentoring_license.mentorAssigment.tips.lostXP())
            tip.setText(i18n.makeString(text, name=self._tankman.getFullUserNameWithSkin()))
            tip.setType(TipType.ERROR)
            tips.addViewModel(tip)
        tips.invalidate()

    def __clearWidgetPossibleSkillsLevel(self):
        skillsLevels, skillsEffLevels = quickEarnCrewSkills(self._crew, 0, 0, 0)
        self._crewWidget.updatePossibleSkillsLevel(skillsLevels, skillsEffLevels)

    def __onGoodiesUpdate(self, diff):
        if goodie_constants.MENTORING_LICENSE_GOODIE_ID in diff:
            with self.viewModel.transaction() as vm:
                vm.setLicensesAmount(getMetoringLicensesAmount())

    def __onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.TANKMAN in invDiff:
            skillsLevels, skillsEffLevels = quickEarnCrewSkills(self._crew, 0, 0, 0)
            self._crewWidget.updatePossibleSkillsLevel(skillsLevels, skillsEffLevels)
            self._updateTankmanData()

    def __onDisconnected(self):
        self.destroyWindow()

    def __onResetFilters(self):
        self.__filterPanelWidget.resetState()
        self.__filterPanelWidget.applyStateToModel()


class MentorAssigmentWindow(WindowImpl):

    def __init__(self, **kwargs):
        super(MentorAssigmentWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=MentorAssigmentView(**kwargs))
