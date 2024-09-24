# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/widget/crew_widget.py
from collections import OrderedDict
from itertools import chain
from typing import TYPE_CHECKING, NamedTuple
import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CREW_BOOKS_VIEWED
from constants import RENEWABLE_SUBSCRIPTION_CONFIG, JUNK_TANKMAN_NOVELTY
from frameworks.wulf import ViewFlags, ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from gui.impl.auxiliary.junk_tankman_helper import JunkTankmanHelper
from gui.impl.backport import BackportContextMenuWindow, createContextMenuData
from gui.impl.backport.backport_pop_over import BackportPopOverContent, createPopOverData
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.button_model import ButtonType
from gui.impl.gen.view_models.views.lobby.crew.common.crew_widget_model import CrewWidgetModel
from gui.impl.gen.view_models.views.lobby.crew.common.crew_widget_slot_model import CrewWidgetSlotModel
from gui.impl.gen.view_models.views.lobby.crew.common.toggle_button_model import ToggleState
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.crew_constants import CrewConstants
from gui.impl.gen.view_models.views.lobby.crew.idle_crew_bonus import IdleCrewBonusEnum
from gui.impl.gen_utils import DynAccessor
from gui.impl.lobby.crew.crew_header_tooltip_view import CrewHeaderTooltipView
from gui.impl.lobby.crew.crew_helpers.model_setters import setTmanSkillsModel, setTmanMajorSkillsModel, setTmanBonusSkillsModel
from gui.impl.lobby.crew.crew_helpers.skill_formatters import SkillLvlFormatter
from gui.impl.lobby.crew.crew_helpers.skill_helpers import getTmanNewSkillCount
from gui.impl.lobby.crew.tooltips.empty_skill_tooltip import EmptySkillTooltip
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import NO_TANKMAN, NO_SLOT, SKILL_EFFICIENCY_UNTRAINED, getTankmanSkill, Tankman
from gui.shared.gui_items.Vehicle import getIconResourceName, getLowEfficiencyCrew, NO_VEHICLE_ID
from gui.shared.gui_items.processors.vehicle import VehicleTmenXPAccelerator
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils import decorators
from helpers import dependency, int2roman
from helpers.dependency import descriptor
from items.tankmen import MAX_SKILL_LEVEL, getLessMasteredIDX, sortTankmanRoles
from renewable_subscription_common.passive_xp import isTagsSetOk
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.crew.loggers import CrewWidgetLogger
from uilogging.crew.logging_constants import CrewWidgetKeys
from wg_async import wg_async, wg_await
if TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.crew.common.crew_widget_tankman_model import CrewWidgetTankmanModel
    from gui.impl.gen.view_models.views.lobby.crew.common.crew_skill_model import CrewSkillModel
    from gui.impl.lobby.crew.quick_training_view import QuickTrainingView
    from typing import Union
BuildedMessage = NamedTuple('BuildedMessage', [('text', str),
 ('iconFrom', DynAccessor),
 ('iconTo', DynAccessor),
 ('vehFromCD', DynAccessor),
 ('vehToCD', DynAccessor)])
DOG = 'dog'

class CrewWidget(ViewImpl):
    __slots__ = ('__toolTipMgr', '__currentViewID', '__previousViewID', '__currentTankman', '__currentVehicle', 'onSlotClick', '__currentSlotIdx', 'onChangeCrewClick', 'onSlotTrySelect', '__isButtonBarVisible', '__uiLogger')
    LAYOUT_DYN_ACCESSOR = R.views.lobby.crew.widgets.CrewWidget
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    wotPlusCtrl = dependency.descriptor(IWotPlusController)
    appLoader = descriptor(IAppLoader)

    def __init__(self, tankmanID=NO_TANKMAN, vehicleInvID=NO_VEHICLE_ID, slotIdx=NO_SLOT, currentViewID=None, previousViewID=None, isButtonBarVisible=True):
        settings = ViewSettings(self.LAYOUT_DYN_ACCESSOR())
        settings.flags = ViewFlags.VIEW
        settings.model = CrewWidgetModel()
        self.onSlotTrySelect = Event.Event()
        self.onSlotClick = Event.Event()
        self.onChangeCrewClick = Event.Event()
        self.__uiLogger = CrewWidgetLogger(currentViewID)
        super(CrewWidget, self).__init__(settings)
        self.__toolTipMgr = self.appLoader.getApp().getToolTipMgr()
        self.__currentViewID = currentViewID
        self.__previousViewID = previousViewID
        self.__isButtonBarVisible = isButtonBarVisible
        self.__currentTankman = None
        self.__currentVehicle = None
        self.__currentSlotIdx = slotIdx
        if tankmanID != NO_TANKMAN:
            self.__currentTankman = self.itemsCache.items.getTankman(tankmanID)
            currentVehicleInvID = int(self.__currentTankman.vehicleInvID)
            if currentVehicleInvID != NO_VEHICLE_ID:
                self.__currentVehicle = self.itemsCache.items.getVehicle(currentVehicleInvID)
                self.__currentSlotIdx = self.__getSlotIdxByTankmanID(tankmanID)
            else:
                self.__currentSlotIdx = 0
        elif vehicleInvID != NO_VEHICLE_ID:
            self.__currentSlotIdx = self.__getSlotIdxByTankmanID(tankmanID)
            self.__currentVehicle = self.itemsCache.items.getVehicle(vehicleInvID)
            currentTankmanID = self.__currentVehicle.getTankmanIDBySlotIdx(slotIdx)
            if currentTankmanID != NO_TANKMAN:
                self.__currentTankman = self.itemsCache.items.getTankman(currentTankmanID)
        return

    def getWidgetData(self):
        return (self.__currentSlotIdx, self.__currentVehicle, self.__currentTankman)

    def updateTankmanId(self, tankmanID):
        if self.__currentTankman is None or tankmanID != self.__currentTankman.invID:
            self.__currentTankman = self.itemsCache.items.getTankman(tankmanID)
            currentVehID = self.__currentVehicle.invID if self.__currentVehicle else NO_VEHICLE_ID
            isNewTankmanFromOtherVehicle = self.__currentTankman.isInTank and self.__currentTankman.vehicleInvID != currentVehID
            if isNewTankmanFromOtherVehicle:
                self.__currentVehicle = self.itemsCache.items.getVehicle(self.__currentTankman.vehicleInvID)
            self.__currentSlotIdx = self.__getSlotIdxByTankmanID(tankmanID)
            self.viewModel.setSelectedSlotIdx(self.__currentSlotIdx)
            if isNewTankmanFromOtherVehicle:
                self.__updateWidgetModel()
                self.onSlotTrySelect(slotIDX=self.__currentSlotIdx, tankman=self.__currentTankman)
        return

    def updateVehicleInvID(self, vehicleInvID):
        if self.__currentVehicle is None or vehicleInvID != self.__currentVehicle.invID:
            self.__currentVehicle = self.itemsCache.items.getVehicle(vehicleInvID)
            self.__updateWidgetModel()
        return

    def updateSlotIdx(self, slotIdx):
        if self.__currentVehicle:
            tankmanID = self.__currentVehicle.getTankmanIDBySlotIdx(slotIdx)
            self.__currentTankman = self.itemsCache.items.getTankman(tankmanID) if tankmanID != NO_TANKMAN else None
        self.__currentSlotIdx = slotIdx
        self.viewModel.setSelectedSlotIdx(self.__currentSlotIdx)
        return

    def updateDisableState(self, isDisabled):
        self.viewModel.setIsDisabled(isDisabled)

    def updateInteractiveTankmen(self):
        pass

    def updateVmSlotsData(self, vmSlotsList):
        pass

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def currentViewID(self):
        return self.__currentViewID

    def setCurrentViewID(self, value):
        self.__currentViewID = value
        self.__uiLogger.updateParentViewKey(value)
        with self.viewModel.transaction() as vm:
            vm.setCurrentLayoutID(self.__currentViewID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            self.__uiLogger.onBeforeTooltipOpened(tooltipId)
            if tooltipId == TooltipConstants.SKILL:
                args = [event.getArgument('skillName'),
                 int(event.getArgument('tankmanID')),
                 None,
                 True,
                 None,
                 event.getArgument('isBonus')]
                self.__toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_PERK_GF, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return TOOLTIPS_CONSTANTS.CREW_PERK_GF
            if tooltipId == TooltipConstants.TANKMAN:
                isCalledFromCrewWidget = True
                args = (event.getArgument('tankmanID'), isCalledFromCrewWidget)
                self.__toolTipMgr.onCreateWulfTooltip(TooltipConstants.TANKMAN, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return TooltipConstants.TANKMAN
            if tooltipId == TooltipConstants.SKILLS_EFFICIENCY:
                args = (event.getArgument('tankmanID'),)
                self.__toolTipMgr.onCreateWulfTooltip(tooltipId, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return tooltipId
            if tooltipId == TooltipConstants.CREW_SKILL_UNTRAINED:
                args = ()
                self.__toolTipMgr.onCreateWulfTooltip(tooltipId, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return tooltipId
        return super(CrewWidget, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipId = event.getArgument('tooltipId')
        if contentID == R.views.lobby.crew.CrewHeaderTooltipView():
            return CrewHeaderTooltipView(self.__getIdleCrewState())
        elif tooltipId == TooltipConstants.VEHICLE_CREW_MEMBER_IN_HANGAR:
            slotIdx = int(event.getArgument('slotIdx'))
            tankmanID = int(event.getArgument('tankmanID'))
            if tankmanID == NO_TANKMAN:
                role = self.__currentVehicle.descriptor.type.crewRoles[slotIdx][0]
            else:
                tankman = self.itemsCache.items.getTankman(tankmanID)
                role = tankman.role
                for idx, roles in enumerate(tankman.vehicleNativeDescr.type.crewRoles):
                    if roles and role == roles[0]:
                        slotIdx = idx
                        break

            args = [role,
             tankmanID,
             slotIdx,
             None,
             None,
             None,
             None,
             None]
            return createBackportTooltipContent(specialAlias=TOOLTIPS_CONSTANTS.VEHICLE_CREW_MEMBER_IN_HANGAR, specialArgs=args)
        elif contentID == R.views.lobby.crew.tooltips.EmptySkillTooltip():
            tman = self.itemsCache.items.getTankman(int(event.getArgument('tankmanID')))
            return EmptySkillTooltip(tman, int(event.getArgument('skillIndex')))
        else:
            return super(CrewWidget, self).createToolTipContent(event, contentID)

    def createContextMenu(self, event):
        if event.contentID != R.views.common.BackportContextMenu():
            return None
        else:
            tankmanID = event.getArgument('tankmanID')
            if tankmanID == NO_TANKMAN:
                return None
            contextMenuArgs = {'tankmanID': tankmanID,
             'slotIdx': event.getArgument('slotIdx'),
             'previousViewID': self.__currentViewID}
            contextMenuData = createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.CREW_MEMBER, contextMenuArgs)
            window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
            window.load()
            return window

    def createPopOverContent(self, event):
        args = {'crewIds': getLowEfficiencyCrew(self.__currentVehicle),
         'vehicleCD': self.__currentVehicle.intCD}
        return BackportPopOverContent(createPopOverData(VIEW_ALIAS.CREW_OPERATIONS_POPOVER, args))

    def getSlotIdxByTankmanID(self, tankmanID):
        return self.__getSlotIdxByTankmanID(tankmanID)

    def _onLoading(self, *args, **kwargs):
        super(CrewWidget, self)._onLoading(*args, **kwargs)
        self.__uiLogger.initialize()
        with self.viewModel.transaction() as vm:
            vm.setCurrentLayoutID(self.__currentViewID)
            if self.__previousViewID is not None:
                vm.setPreviousLayoutID(self.__previousViewID)
        self.__updateWidgetModel()
        return

    def _getCallbacks(self):
        return (('inventory.13.2', self.__updateTankmen),
         ('inventory.8.compDescr', self.__updateTankmen),
         ('idleCrewXP', self.__idleCrewXPUpdated),
         ('inventory.1', self.__onVehicleDossierUpdate))

    def _getEvents(self):
        return ((self.viewModel.onSlotClick, self.__onSlotClick),
         (self.viewModel.onChangeCrewClick, self.__onChangeCrewClick),
         (self.viewModel.onDogMoreInfoClick, self.__onDogMoreInfoClick),
         (self.viewModel.buttonsBar.onCrewBooksClick, self.__onCrewBooksClick),
         (self.viewModel.buttonsBar.onAcceleratedTrainingClick, self.__onAcceleratedTrainingClick),
         (self.viewModel.buttonsBar.onWotPlusClick, self.__onWotPlusClick),
         (self.itemsCache.onSyncCompleted, self.__onCacheResync),
         (self.lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChange),
         (AccountSettings.onSettingsChanging, self.__onAccountSettingsChanging),
         (JunkTankmanHelper().onShowNoveltyUpdated, self.__onShowNoveltyUpdated))

    def _finalize(self):
        super(CrewWidget, self)._finalize()
        self.__uiLogger.finalize()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _updateButtonsBar(self, vmButtonsBar, isCrewEmpty=True):
        vmButtonsBar.setIsVisible(self.__isButtonBarVisible)
        vmButtonsBar.crewOperations.setType(ButtonType.CREWOPERATIONS)
        vmButtonsBar.crewOperations.setIsAutoReturnOn(False)
        vmButtonsBar.crewBooks.setType(ButtonType.CREWBOOKS)
        vmButtonsBar.crewBooks.setIsDisabled(isCrewEmpty)
        self.__updateCrewBooksAmount(vmButtonsBar.crewBooks)
        vmButtonsBar.acceleratedTraining.setType(ButtonType.ACCELERATEDTRAINING)
        vmButtonsBar.acceleratedTraining.setIsDisabled(isCrewEmpty)
        vmButtonsBar.wotPlus.setType(ButtonType.WOTPLUS)
        vmButtonsBar.wotPlus.setIsDisabled(isCrewEmpty)
        if self.__currentVehicle is None:
            vmButtonsBar.crewBooks.setHasDiscount(False)
            vmButtonsBar.acceleratedTraining.setState(ToggleState.HIDDEN)
            vmButtonsBar.wotPlus.setState(ToggleState.HIDDEN)
        else:
            self.__updateCrewBooksDiscount(vmButtonsBar.crewBooks)
            isXPToTman = self.__currentVehicle.isXPToTman if self.__currentVehicle else False
            vmButtonsBar.acceleratedTraining.setState(ToggleState.ON if isXPToTman else (ToggleState.OFF if self.__currentVehicle.isElite else ToggleState.DISABLED))
            self.__updateWotPlusButtonModel(vmButtonsBar.wotPlus)
        return

    def _getLastSkillLevelFormat(self, lastSkillLevel):
        return lastSkillLevel.intSkillLvl

    def __updateWidgetModel(self):
        with self.viewModel.transaction() as vm:
            if self.__currentVehicle:
                self.__updateWidgetModelByVehicle(vm)
            elif self.__currentTankman:
                self.__updateWidgetModelByTankman(vm)
            else:
                self._updateButtonsBar(vm.buttonsBar)

    def __updateWidgetModelByVehicle(self, vm):
        isCrewEmpty, lessMastered = self.__findTmanData()
        self._updateButtonsBar(vm.buttonsBar, isCrewEmpty)
        self.__fillVehicleInfo(vm)
        self.__fillSlotsList(vm.getSlots(), lessMastered)
        self.__checkDog(vm)

    def __updateWidgetModelByTankman(self, vm):
        self._updateButtonsBar(vm.buttonsBar)
        vmSlotsList = vm.getSlots()
        vmSlotsList.clear()
        vmSlot = CrewWidgetSlotModel()
        self._fillTankmanModel(vmSlot.tankman, self.__currentTankman)
        vmSlotsList.addViewModel(vmSlot)
        self.updateVmSlotsData(vmSlotsList)
        vmSlotsList.invalidate()

    def __getSlotIdxByTankmanID(self, tankmanID):
        if self.__currentVehicle:
            for slotIdx, tman in self.__currentVehicle.crew:
                if tman and tman.invID == tankmanID:
                    return slotIdx

        return NO_SLOT

    def __onVehicleDossierUpdate(self, diff=None):
        crews = diff.get('crew', {})
        if self.__currentVehicle:
            settings = diff.get('settings', {})
            eqs = diff.get('eqs', {})
            compDescr = diff.get('compDescr', {})
            boosters = diff.get('boosters', {})
            changedVehicles = [ (vehInvID if isinstance(vehInvID, int) else vehInvID[0]) for vehInvID in crews.iterkeys() ]
            changedVehicles.extend((vehInvID for vehInvID in chain(settings.iterkeys(), eqs.iterkeys(), compDescr.iterkeys(), boosters.iterkeys())))
            if self.__currentVehicle.invID in changedVehicles:
                self.__currentVehicle = self.itemsCache.items.getVehicle(self.__currentVehicle.invID)
                self.__updateWidgetModel()
        elif self.__currentTankman and any((self.__currentTankman.invID in tankmen for tankmen in crews.itervalues() if tankmen is not None)):
            self.__currentTankman = self.itemsCache.items.getTankman(self.__currentTankman.invID)
            if self.__currentTankman.isInTank:
                self.__currentVehicle = self.itemsCache.items.getVehicle(self.__currentTankman.vehicleInvID)
            else:
                self.__currentVehicle = None
            self.__updateWidgetModel()
        if crews:
            if not self.__currentTankman and self.__currentSlotIdx != NO_SLOT:
                crewsList = crews[next(iter(crews))]
                if len(crewsList) > self.__currentSlotIdx:
                    self.__currentTankman = self.itemsCache.items.getTankman(crewsList[self.__currentSlotIdx])
            self.onSlotTrySelect(slotIDX=self.__currentSlotIdx, tankman=self.__currentTankman)
        return

    def __idleCrewXPUpdated(self, diff):
        with self.viewModel.transaction() as vm:
            self.__updateWotPlusButtonModel(vm.buttonsBar.wotPlus)

    def __updateTankmen(self, diff=None):
        if not self.__checkIsTankmanUpdated(diff):
            return
        if self.__currentVehicle:
            self.__currentVehicle = self.itemsCache.items.getVehicle(self.__currentVehicle.invID)
            self.__updateWidgetModel()
        elif self.__currentTankman:
            self.__currentTankman = self.itemsCache.items.getTankman(self.__currentTankman.invID)
            self.__updateWidgetModel()
            self.onSlotTrySelect(slotIDX=self.__currentSlotIdx, tankman=self.__currentTankman)
        else:
            with self.viewModel.transaction() as vm:
                self._updateButtonsBar(vm.buttonsBar)

    def __checkIsTankmanUpdated(self, diff):
        if self.__currentVehicle:
            for _, tman in self.__currentVehicle.crew:
                if tman and tman.invID in diff:
                    return True

        elif self.__currentTankman:
            return self.__currentTankman.invID in diff
        return False

    def __onChangeCrewClick(self, args):
        slotIdx = int(args.get('slotIdx'))
        self.updateSlotIdx(slotIdx)
        self.onChangeCrewClick(self.__currentVehicle.invID, slotIdx, self.__currentViewID)
        self.__uiLogger.logClick(CrewWidgetKeys.CHANGE_TANKMAN_BUTTON)

    def __onSlotClick(self, args):
        tankmanID = int(args.get('tankmanID'))
        slotIdx = int(args.get('slotIdx'))
        self.updateSlotIdx(slotIdx)
        self.onSlotClick(tankmanID, slotIdx)
        self.__uiLogger.logClick(CrewWidgetKeys.TANKMAN_SLOT)

    def __onServerSettingsChange(self, diff):
        if RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            with self.viewModel.transaction() as vm:
                self.__updateWotPlusButtonModel(vm.buttonsBar.wotPlus)

    def __onAccountSettingsChanging(self, key, _):
        if key == CREW_BOOKS_VIEWED:
            with self.viewModel.transaction() as vm:
                self.__updateCrewBooksAmount(vm.buttonsBar.crewBooks)

    def __onCacheResync(self, reason, diff):
        with self.viewModel.transaction() as vm:
            if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
                self.__updateCrewBooksDiscount(vm.buttonsBar.crewBooks)
            if diff is not None and GUI_ITEM_TYPE.CREW_BOOKS in diff:
                self.__updateCrewBooksAmount(vm.buttonsBar.crewBooks)
        return

    def __findTmanData(self):
        crew = OrderedDict(sorted(self.__currentVehicle.crew, key=lambda item: item[0]))
        tankmenDescrs = [ (tman.descriptor if tman else None) for tman in crew.itervalues() ]
        return getLessMasteredIDX(tankmenDescrs)

    def __fillVehicleInfo(self, vm):
        vm.setVehicleName(self.__currentVehicle.shortUserName)
        vm.setVehicleType(self.__currentVehicle.type)
        vm.setIsCrewLocked(self.__currentVehicle.isCrewLocked)
        vm.setNation(self.__currentVehicle.nationName)

    def __fillSlotsList(self, vmSlotsList, lessMastered):
        vehicle = self.__currentVehicle
        vmSlotsList.clear()
        for slotIdx, tman in vehicle.crew:
            tmanInvID = NO_TANKMAN if tman is None else tman.invID
            vmSlot = CrewWidgetSlotModel()
            vmSlot.setSlotIdx(slotIdx)
            vmSlotRoles = vmSlot.getRoles()
            sortedRoles = sortTankmanRoles(vehicle.descriptor.type.crewRoles[slotIdx], Tankman.TANKMEN_ROLES_ORDER)
            for crewRole in sortedRoles:
                vmSlotRoles.addString(crewRole)

            self._fillTankmanModel(vmSlot.tankman, tman, vehicle.crewIndices.get(tmanInvID) == lessMastered and vehicle.isXPToTman)
            vmSlotsList.addViewModel(vmSlot)

        self.updateVmSlotsData(vmSlotsList)
        vmSlotsList.invalidate()
        return

    def _fillTankmanModel(self, vmTankman, tman, isLessMastered=False):
        if tman is not None:
            tmanSkillsEfficiency = tman.currentVehicleSkillsEfficiency
            vmTankman.setTankmanID(tman.invID)
            vmTankman.setFullName(tman.getFullUserNameWithSkin())
            vmTankman.setIcon(tman.getExtensionLessIconWithSkin())
            vmTankman.setIsInSkin(tman.isInSkin)
            vmTankman.setIsFemale(tman.isFemale)
            vmTankman.setHasWarning(tmanSkillsEfficiency == SKILL_EFFICIENCY_UNTRAINED)
            vmTankman.setIsLessMastered(isLessMastered)
            vmTankman.setSkillsEfficiency(tmanSkillsEfficiency)
            setTmanSkillsModel(vmTankman.skills, tman, fillBonusSkills=tman.isInTank)
            newSkillsCount, lastSkillLevel = getTmanNewSkillCount(tman)
            if tman.earnedSkillsCount + newSkillsCount <= 0:
                lastSkillLevel = SkillLvlFormatter()
            vmTankman.setLastSkillLevel(self._getLastSkillLevelFormat(lastSkillLevel))
            vmTankman.setLastSkillLevelFull(lastSkillLevel.realSkillLvl)
            vmTankman.setHasPostProgression(tman.descriptor.isMaxSkillXp())
            vmTankmanRolesList = vmTankman.getRoles()
            for role in tman.roles():
                vmTankmanRolesList.addString(role)

        else:
            vmTankman.setTankmanID(NO_TANKMAN)
        vmTankman.setIsInteractive(True)
        return

    def __checkDog(self, vm):
        vm.setHasDog(DOG in self.itemsCache.items.getItemByCD(self.__currentVehicle.intCD).tags)

    def __updateWotPlusButtonModel(self, vmWotPlusButton):
        wotPlusState = ToggleState.HIDDEN
        vehicle = self.__currentVehicle
        if vehicle and self.lobbyContext.getServerSettings().isRenewableSubPassiveCrewXPEnabled():
            wotPlusState = ToggleState.DISABLED if not self.wotPlusCtrl.isEnabled() or not isTagsSetOk(vehicle.tags) or vehicle.isCrewFullyTrained else (ToggleState.ON if self.wotPlusCtrl.hasVehicleCrewIdleXP(vehicle.invID) else ToggleState.OFF)
        vmWotPlusButton.setState(wotPlusState)

    def __onDogMoreInfoClick(self):
        from gui.impl.dialogs import dialogs
        from gui.impl.dialogs.gf_builders import ResDialogBuilder
        builder = ResDialogBuilder()
        builder.setMessagesAndButtons(R.strings.dialogs.rudyInfo, buttons=R.invalid)
        builder.setIcon(R.images.gui.maps.icons.tankmen.windows.aboutRudy())
        dialogs.show(builder.build())

    def __onCrewBooksClick(self):
        from gui.shared.event_dispatcher import showQuickTraining
        showQuickTraining(vehicleInvID=self.__currentVehicle.invID, previousViewID=self.currentViewID)
        self.__uiLogger.logClick(CrewWidgetKeys.QUIK_TRAINING_BUTTON)

    @wg_async
    def __onAcceleratedTrainingClick(self):
        from gui.shared.event_dispatcher import showAccelerateCrewTrainingDialog
        vehicle = self.__currentVehicle
        if vehicle:
            wasActive = vehicle.isXPToTman
            self.__uiLogger.logClick(CrewWidgetKeys.ACCELERATE_BUTTON)

            def toggleCallback():
                self.__onAccelerateCrewTrainingConfirmed(vehicle, wasActive)

            if wasActive:
                toggleCallback()
            else:
                yield wg_await(showAccelerateCrewTrainingDialog(toggleCallback))

    @decorators.adisp_process('updateTankmen')
    def __onAccelerateCrewTrainingConfirmed(self, vehicle, wasActive):
        result = yield VehicleTmenXPAccelerator(vehicle, not wasActive, False).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @wg_async
    def __onWotPlusClick(self):
        wasActive = self.viewModel.buttonsBar.wotPlus.getState() == ToggleState.ON
        toBeActive = not wasActive

        def toggleCallback():
            vehId = self.__currentVehicle.invID if toBeActive else None
            self.wotPlusCtrl.selectIdleCrewXPVehicle(vehId)
            return

        dialogMessage = self.__buildConfirmationMessage()
        if not dialogMessage or not toBeActive:
            toggleCallback()
        else:
            from gui.shared.event_dispatcher import showIdleCrewBonusDialog
            yield wg_await(showIdleCrewBonusDialog(dialogMessage, toggleCallback))

    def __buildConfirmationMessage(self):
        previousVehicleId = self.wotPlusCtrl.getVehicleIDWithIdleXP()
        previousVehicle = self.itemsCache.items.getVehicle(previousVehicleId) if previousVehicleId else None
        stringRoot = R.strings.dialogs.idleCrewBonus
        message = None
        if previousVehicle:
            vehicleFromName = '{} %(typeIconFrom) {}'.format(int2roman(previousVehicle.level), previousVehicle.userName)
            removeTypeStringFrom = backport.text(stringRoot.message.removeTypeFrom())
            removeVehFromNameString = backport.text(stringRoot.message.removeName(), vehicleName=vehicleFromName)
            vehicleToName = '{} %(typeIconTo) {}'.format(int2roman(self.__currentVehicle.level), self.__currentVehicle.userName)
            removeTypeStringTo = backport.text(stringRoot.message.removeTypeTo())
            removeVehToNameString = backport.text(stringRoot.message.removeName(), vehicleName=vehicleToName)
            endDot = backport.text(stringRoot.message.dot())
            finalString = '{} {} {} {}{}'.format(removeTypeStringFrom, removeVehFromNameString, removeTypeStringTo, removeVehToNameString, endDot)
            message = BuildedMessage(text=finalString, iconFrom=R.images.gui.maps.icons.vehicleTypes.num('24x24').dyn(getIconResourceName(previousVehicle.type)), iconTo=R.images.gui.maps.icons.vehicleTypes.num('24x24').dyn(getIconResourceName(self.__currentVehicle.type)), vehFromCD=previousVehicle.intCD, vehToCD=self.__currentVehicle.intCD)
        return message

    def __getIdleCrewState(self):
        vehicle = self.__currentVehicle
        if not self.lobbyContext.getServerSettings().isRenewableSubPassiveCrewXPEnabled():
            return IdleCrewBonusEnum.INVISIBLE
        if not self.wotPlusCtrl.isEnabled():
            return IdleCrewBonusEnum.DISABLED
        if not isTagsSetOk(vehicle.tags):
            return IdleCrewBonusEnum.INCOMPATIBLEWITHCURRENTVEHICLE
        if vehicle.isCrewFullyTrained:
            return IdleCrewBonusEnum.POSTPROGRESSIONREACHED
        if self.wotPlusCtrl.hasVehicleCrewIdleXP(vehicle.invID):
            return IdleCrewBonusEnum.ACTIVEONCURRENTVEHICLE
        return IdleCrewBonusEnum.ACTIVEONANOTHERVEHICLE if self.wotPlusCtrl.getVehicleIDWithIdleXP() else IdleCrewBonusEnum.ENABLED

    def __onShowNoveltyUpdated(self):
        with self.viewModel.transaction() as vm:
            self.__updateCrewBooksAmount(vm.buttonsBar.crewBooks)

    def __updateCrewBooksAmount(self, vmCrewBooks):
        if self.__currentVehicle is None:
            vmCrewBooks.setNewAmount('0')
            vmCrewBooks.setTotalAmount(0)
        else:
            viewedCache = crewBooksViewedCache()
            newCrewBooksAmount = viewedCache.newCrewBooksAmount
            if newCrewBooksAmount:
                vmCrewBooks.setNewAmount(str(int(newCrewBooksAmount)))
            elif JunkTankmanHelper().isShowNovelty(showPlace=JUNK_TANKMAN_NOVELTY.WIDGET):
                vmCrewBooks.setNewAmount(backport.text(R.strings.crew.common.exclamationMark()))
            else:
                vmCrewBooks.setNewAmount('0')
            vmCrewBooks.setTotalAmount(viewedCache.crewBooksAmount)
        return

    def __updateCrewBooksDiscount(self, vmCrewBooks):
        shop = self.itemsCache.items.shop
        vmCrewBooks.setHasDiscount(shop.freeXPToTManXPRate != shop.defaults.freeXPToTManXPRate)


class QuickTrainingCrewWidget(CrewWidget):
    __slots__ = ('_cachePossibleSkillsLevels', '_cachePossibleSkillsEfficiency')

    def __init__(self, tankmanID=NO_TANKMAN, vehicleInvID=NO_VEHICLE_ID, slotIdx=NO_SLOT, currentViewID=None, previousViewID=None, isButtonBarVisible=True):
        super(QuickTrainingCrewWidget, self).__init__(tankmanID, vehicleInvID, slotIdx, currentViewID, previousViewID, isButtonBarVisible)
        self._cachePossibleSkillsLevels = None
        self._cachePossibleSkillsEfficiency = None
        return

    def updateInteractiveTankmen(self):
        qtView = self.gui.windowsManager.getViewByLayoutID(self.currentViewID)
        with self.viewModel.transaction() as vm:
            vmSlots = vm.getSlots()
            for vmSlot in vmSlots:
                if vmSlot.tankman is None:
                    continue
                tman = self.itemsCache.items.getTankman(vmSlot.tankman.getTankmanID())
                if tman is None:
                    continue
                vmSlot.tankman.setIsInteractive(qtView.canTmanBeSelected(tman))

            vmSlots.invalidate()
        return

    def clearPossibleSkillsLevelCache(self):
        self._cachePossibleSkillsLevels = None
        self._cachePossibleSkillsEfficiency = None
        return

    def updateVmSlotsData(self, vmSlotsList):
        self.__updatePossibleSkillsViewModel(vmSlotsList)
        self.__updatePossibleSkillsEfficiency(vmSlotsList)

    def updatePossibleSkillsLevel(self, possibleSkillsLevels, skillsEffLevels):
        self._cachePossibleSkillsLevels = possibleSkillsLevels
        self._cachePossibleSkillsEfficiency = skillsEffLevels
        with self.viewModel.transaction() as vm:
            vmSlots = vm.getSlots()
            self.__updatePossibleSkillsViewModel(vmSlots)
            self.__updatePossibleSkillsEfficiency(vmSlots)
            vmSlots.invalidate()

    def _finalize(self):
        super(QuickTrainingCrewWidget, self)._finalize()
        self._cachePossibleSkillsLevels = None
        self._cachePossibleSkillsEfficiency = None
        return

    def _updateButtonsBar(self, vmButtonsBar, isCrewEmpty=True):
        super(QuickTrainingCrewWidget, self)._updateButtonsBar(vmButtonsBar, isCrewEmpty)
        vmButtonsBar.crewBooks.setIsDisabled(True)

    def _getLastSkillLevelFormat(self, lastSkillLevel):
        return lastSkillLevel.formattedSkillLvl

    def __updatePossibleSkillsEfficiency(self, vmSlots):
        skillsEffLevels = self._cachePossibleSkillsEfficiency
        for vmSlot in iter(vmSlots):
            slotIDX = vmSlot.getSlotIdx()
            if vmSlot.tankman is None or skillsEffLevels and len(skillsEffLevels) <= slotIDX:
                continue
            if skillsEffLevels is None:
                vmSlot.tankman.setPossibleSkillsEfficiency(-1)
                continue
            possSkillsEff = skillsEffLevels[vmSlot.getSlotIdx()]
            vmSlot.tankman.setPossibleSkillsEfficiency(possSkillsEff)

        return

    def __updatePossibleSkillsViewModel(self, vmSlots):
        possibleSkillsLevels = self._cachePossibleSkillsLevels
        for vmSlot in iter(vmSlots):
            slotIDX = vmSlot.getSlotIdx()
            if vmSlot.tankman is None or possibleSkillsLevels and len(possibleSkillsLevels) <= slotIDX:
                continue
            tman = self.itemsCache.items.getTankman(vmSlot.tankman.getTankmanID())
            setTmanSkillsModel(vmSlot.tankman.possibleSkills, tman, fillBonusSkills=tman.isInTank if tman else False, possibleSkillsLevels=None if possibleSkillsLevels is None else possibleSkillsLevels[vmSlot.getSlotIdx()])
            if self._cachePossibleSkillsEfficiency is not None:
                possSkillsEff = self._cachePossibleSkillsEfficiency[vmSlot.getSlotIdx()]
                if possSkillsEff != CrewConstants.DONT_SHOW_LEVEL:
                    vmSlot.tankman.possibleSkills.setSkillsEfficiency(possSkillsEff)
            if possibleSkillsLevels is None:
                vmSlot.tankman.setPossibleSkillsAmount(0)
                vmSlot.tankman.setLastPossibleSkillLevel(-1)
                vmSlot.tankman.setHasPossibleProgress(False)
                continue
            currSkillsCount, possibleSkillsCount, currSkillsLvl, possibleLastSkillLevel = possibleSkillsLevels[vmSlot.getSlotIdx()]
            progressLvl = possibleLastSkillLevel - currSkillsLvl if possibleSkillsCount == currSkillsCount and currSkillsLvl.isSkillLvl and currSkillsLvl < MAX_SKILL_LEVEL else possibleLastSkillLevel
            vmSlot.tankman.setPossibleSkillsAmount(max(possibleSkillsCount - currSkillsCount, 0))
            vmSlot.tankman.setLastPossibleSkillLevel(progressLvl.formattedSkillLvl)
            vmSlot.tankman.setLastSkillLevel(currSkillsLvl.formattedSkillLvl)
            vmSlot.tankman.setLastSkillLevelFull(currSkillsLvl.realSkillLvl)
            vmSlot.tankman.setHasPossibleProgress(possibleSkillsCount > 0 or progressLvl.isSkillLvl)

        return


class SkillsTrainingCrewWidget(CrewWidget):

    def updateSelectedSkills(self, tankman, selectedSkills, role):
        with self.viewModel.transaction() as vm:
            for slotVM in vm.getSlots():
                if slotVM.tankman.getTankmanID() == tankman.invID:
                    possibleSkills = slotVM.tankman.possibleSkills
                    if role == tankman.role:
                        listVM = possibleSkills.getMajorSkills()
                        listVM.clear()
                        setTmanMajorSkillsModel(listVM, tankman)
                        for skillName in selectedSkills:
                            for skillVM in listVM:
                                if skillVM.getName() == CrewConstants.NEW_SKILL:
                                    skill = getTankmanSkill(skillName, tankman=tankman)
                                    skillVM.setName(skillName)
                                    skillVM.setIconName(skill.extensionLessIconName)
                                    break

                    else:
                        listVM = possibleSkills.getBonusSkills()
                        listVM.clear()
                        setTmanBonusSkillsModel(listVM, tankman, selectedRole=role, selectedSkills=selectedSkills)
                    listVM.invalidate()
                    break

    def _fillTankmanModel(self, vmTankman, tman, isLessMastered=False):
        super(SkillsTrainingCrewWidget, self)._fillTankmanModel(vmTankman, tman, isLessMastered)
        if tman is not None:
            setTmanSkillsModel(vmTankman.possibleSkills, tman, fillBonusSkills=tman.isInTank)
        return
