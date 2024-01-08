# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/widget/crew_widget.py
from itertools import chain
from typing import TYPE_CHECKING, NamedTuple
import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CREW_BOOKS_VIEWED
from constants import RENEWABLE_SUBSCRIPTION_CONFIG
from frameworks.wulf import ViewFlags, ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from gui.impl.backport import BackportContextMenuWindow, createContextMenuData
from gui.impl.backport.backport_pop_over import BackportPopOverContent, createPopOverData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.button_model import ButtonType
from gui.impl.gen.view_models.views.lobby.crew.common.crew_widget_model import CrewWidgetModel
from gui.impl.gen.view_models.views.lobby.crew.common.crew_widget_slot_model import CrewWidgetSlotModel
from gui.impl.gen.view_models.views.lobby.crew.common.toggle_button_model import ToggleState
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.idle_crew_bonus import IdleCrewBonusEnum
from gui.impl.gen_utils import DynAccessor
from gui.impl.lobby.crew.crew_header_tooltip_view import CrewHeaderTooltipView
from gui.impl.lobby.crew.crew_helpers.model_setters import setTmanSkillsModel
from gui.impl.lobby.crew.crew_helpers.skill_formatters import SkillLvlFormatter
from gui.impl.lobby.crew.crew_helpers.skill_helpers import getTmanNewSkillCount
from gui.impl.lobby.crew.tooltips.perk_available_tooltip import PerkAvailableTooltip
from gui.impl.lobby.crew.tooltips.training_level_tooltip import TrainingLevelTooltip
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import NO_TANKMAN, NO_SLOT
from gui.shared.gui_items.Vehicle import getIconResourceName, getRetrainTankmenIds, NO_VEHICLE_ID
from gui.shared.gui_items.processors.vehicle import VehicleTmenXPAccelerator
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils import decorators
from helpers import dependency, int2roman
from helpers.dependency import descriptor
from items.tankmen import compareMastery, MAX_SKILL_LEVEL
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
    from gui.impl.lobby.crew.quick_training_view import QuickTrainingView
    from gui.shared.gui_items.Tankman import Tankman
    from typing import Union
BuildedMessage = NamedTuple('BuildedMessage', [('text', str), ('icon', DynAccessor)])
DOG = 'dog'

class CrewWidget(ViewImpl):
    __slots__ = ('__toolTipMgr', '__currentViewID', '__previousViewID', '__currentTankman', '__currentVehicle', 'onSlotClick', '__currentSlotIdx', 'onChangeCrewClick', 'onSlotTrySelect', '__isButtonBarVisible', '__uiLogger', '_cachePossibleSkillsLevels')
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
        self._cachePossibleSkillsLevels = None
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
        qtvLayoutID = R.views.lobby.crew.QuickTrainingView()
        if self.__currentViewID != qtvLayoutID:
            return
        else:
            qtView = self.gui.windowsManager.getViewByLayoutID(qtvLayoutID)
            with self.viewModel.transaction() as vm:
                vmSlots = vm.getSlots()
                for vmSlot in vmSlots:
                    if vmSlot.tankman is None:
                        continue
                    tman = self.itemsCache.items.getTankman(vmSlot.tankman.getTankmanID())
                    isInteractive = qtView.canTmanBeSelected(tman)
                    vmSlot.tankman.setIsInteractive(isInteractive)

                vmSlots.invalidate()
            return

    def clearPossibleSkillsLevelCache(self):
        self._cachePossibleSkillsLevels = None
        return

    def updatePossibleSkillsLevel(self, possibleSkillsLevels, viewModel=None):
        self._cachePossibleSkillsLevels = possibleSkillsLevels
        if viewModel:
            self.__updatePossibleSkillsViewModel(viewModel)
        else:
            with self.viewModel.transaction() as vm:
                vmSlots = vm.getSlots()
                self.__updatePossibleSkillsViewModel(vmSlots)
                vmSlots.invalidate()

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
                args = [event.getArgument('skillName'), int(event.getArgument('tankmanID'))]
                self.__toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_PERK_GF, args, event.mouse.positionX, event.mouse.positionY)
                return TOOLTIPS_CONSTANTS.CREW_PERK_GF
            if tooltipId == TooltipConstants.TANKMAN:
                args = (self.getParentWindow(), event.getArgument('tankmanID'))
                self.__toolTipMgr.onCreateWulfTooltip(TooltipConstants.TANKMAN, args, event.mouse.positionX, event.mouse.positionY)
                return TooltipConstants.TANKMAN
        return super(CrewWidget, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.crew.CrewHeaderTooltipView():
            return CrewHeaderTooltipView(self.__getIdleCrewState())
        if contentID == R.views.lobby.crew.tooltips.TrainingLevelTooltip():
            tankmanID = event.getArgument('tankmanID')
            return TrainingLevelTooltip(tankmanID)
        if contentID == R.views.lobby.crew.tooltips.PerkAvailableTooltip():
            tankmanID = event.getArgument('tankmanID')
            return PerkAvailableTooltip(tankmanID)
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
        args = {'tankmenIds': getRetrainTankmenIds(self.__currentVehicle),
         'vehicleCD': self.__currentVehicle.intCD}
        return BackportPopOverContent(createPopOverData(VIEW_ALIAS.CREW_OPERATIONS_POPOVER, args))

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
         (AccountSettings.onSettingsChanging, self.__onAccountSettingsChanging))

    def _finalize(self):
        super(CrewWidget, self)._finalize()
        self._cachePossibleSkillsLevels = None
        self.__uiLogger.finalize()
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

    def __updateWidgetModel(self):
        with self.viewModel.transaction() as vm:
            if self.__currentVehicle:
                self.__updateWidgetModelByVehicle(vm)
            elif self.__currentTankman:
                self.__updateWidgetModelByTankman(vm)
            else:
                self.__updateButtonsBar(vm.buttonsBar)

    def __updateWidgetModelByVehicle(self, vm):
        isCrewEmpty, lessMastered = self.__findTmanData()
        self.__updateButtonsBar(vm.buttonsBar, isCrewEmpty)
        self.__fillVehicleInfo(vm)
        self.__fillSlotsList(vm.getSlots(), lessMastered)
        self.__checkDog(vm)

    def __updateWidgetModelByTankman(self, vm):
        self.__updateButtonsBar(vm.buttonsBar)
        vmSlotsList = vm.getSlots()
        vmSlotsList.clear()
        vmSlot = CrewWidgetSlotModel()
        self.__fillTankmanModel(vmSlot.tankman, self.__currentTankman)
        vmSlotsList.addViewModel(vmSlot)
        self.updatePossibleSkillsLevel(self._cachePossibleSkillsLevels, vmSlotsList)
        vmSlotsList.invalidate()

    def __updatePossibleSkillsViewModel(self, vmSlots):
        possibleSkillsLevels = self._cachePossibleSkillsLevels
        for vmSlot in iter(vmSlots):
            slotIDX = vmSlot.getSlotIdx()
            if vmSlot.tankman is None or possibleSkillsLevels and len(possibleSkillsLevels) <= slotIDX:
                continue
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

    def getSlotIdxByTankmanID(self, tankmanID):
        return self.__getSlotIdxByTankmanID(tankmanID)

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
                self.__updateButtonsBar(vm.buttonsBar)

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
        lessMastered = 0
        tankmenDescrs = dict(self.__currentVehicle.crew)
        isCrewEmpty = True
        for slotIdx, tman in self.__currentVehicle.crew:
            if tman is not None:
                isCrewEmpty = False
                if slotIdx > 0 and (tankmenDescrs[lessMastered] is None or compareMastery(tankmenDescrs[lessMastered].descriptor, tman.descriptor) > 0):
                    lessMastered = slotIdx

        return (isCrewEmpty, lessMastered)

    def __updateButtonsBar(self, vmButtonsBar, isCrewEmpty=True):
        vmButtonsBar.setIsVisible(self.__isButtonBarVisible)
        vmButtonsBar.crewOperations.setType(ButtonType.CREWOPERATIONS)
        vmButtonsBar.crewOperations.setIsAutoReturnOn(False)
        vmButtonsBar.crewBooks.setType(ButtonType.CREWBOOKS)
        vmButtonsBar.crewBooks.setIsDisabled(isCrewEmpty or self.__currentViewID == R.views.lobby.crew.QuickTrainingView())
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
            for crewRole in vehicle.descriptor.type.crewRoles[slotIdx]:
                vmSlotRoles.addString(crewRole)

            self.__fillTankmanModel(vmSlot.tankman, tman, vehicle.crewIndices.get(tmanInvID) == lessMastered and vehicle.isXPToTman)
            vmSlotsList.addViewModel(vmSlot)

        self.updatePossibleSkillsLevel(self._cachePossibleSkillsLevels, vmSlotsList)
        vmSlotsList.invalidate()
        return

    def __fillTankmanModel(self, vmTankman, tman, isLessMastered=False):
        isInteractive = True
        if tman is not None:
            rrl = tman.realRoleLevel
            isUntrained = tman.roleLevel < MAX_SKILL_LEVEL or rrl.bonuses.penalty < 0
            hasWarning = isUntrained
            if self.__currentViewID == R.views.lobby.crew.QuickTrainingView():
                isInteractive = not isUntrained
                hasWarning |= tman.isInTank and not tman.isInNativeTank
            vmTankman.setTankmanID(tman.invID)
            vmTankman.setFullName(tman.getFullUserNameWithSkin())
            vmTankman.setIcon(tman.getExtensionLessIconWithSkin())
            vmTankman.setIsInSkin(tman.isInSkin)
            vmTankman.setIsFemale(tman.isFemale)
            vmTankman.setSpecializationLevel(int(rrl.lvl))
            vmTankman.setIsUntrained(isUntrained)
            vmTankman.setHasWarning(hasWarning)
            vmTankman.setBaseSpecializationLevel(tman.roleLevel)
            vmTankman.setIsLessMastered(isLessMastered)
            setTmanSkillsModel(vmTankman.getSkills(), tman)
            newSkillsCount, lastSkillLevel = getTmanNewSkillCount(tman)
            isResidualUsed = self.__currentViewID == R.views.lobby.crew.QuickTrainingView()
            if tman.earnedSkillsCount + newSkillsCount <= 0:
                lastSkillLevel = SkillLvlFormatter()
            vmTankman.setLastSkillLevel(lastSkillLevel.formattedSkillLvl if isResidualUsed else lastSkillLevel.intSkillLvl)
            vmTankman.setLastSkillLevelFull(lastSkillLevel.realSkillLvl)
            vmTankmanRolesList = vmTankman.getRoles()
            for role in tman.roles():
                vmTankmanRolesList.addString(role)

        else:
            vmTankman.setTankmanID(NO_TANKMAN)
        vmTankman.setIsInteractive(isInteractive)
        return

    def __checkDog(self, vm):
        vm.setHasDog(DOG in self.itemsCache.items.getItemByCD(self.__currentVehicle.intCD).tags)

    def __updateWotPlusButtonModel(self, vmWotPlusButton):
        wotPlusState = ToggleState.HIDDEN
        vehicle = self.__currentVehicle
        if vehicle and self.lobbyContext.getServerSettings().isRenewableSubPassiveCrewXPEnabled():
            wotPlusState = ToggleState.DISABLED if not self.wotPlusCtrl.isEnabled() or not isTagsSetOk(vehicle.tags) else (ToggleState.ON if self.wotPlusCtrl.hasVehicleCrewIdleXP(vehicle.invID) else ToggleState.OFF)
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
            vehicleName = '{} {}'.format(int2roman(previousVehicle.level), previousVehicle.userName)
            removeTypeString = backport.text(stringRoot.message.removeType())
            removeNameString = backport.text(stringRoot.message.removeName(), vehicleName=vehicleName)
            finalString = '{} {}'.format(removeTypeString, removeNameString)
            message = BuildedMessage(text=finalString, icon=R.images.gui.maps.icons.vehicleTypes.dyn(getIconResourceName(previousVehicle.type)))
        return message

    def __getIdleCrewState(self):
        if not self.lobbyContext.getServerSettings().isRenewableSubPassiveCrewXPEnabled():
            return IdleCrewBonusEnum.INVISIBLE
        if not self.wotPlusCtrl.isEnabled():
            return IdleCrewBonusEnum.DISABLED
        if not isTagsSetOk(self.__currentVehicle.tags):
            return IdleCrewBonusEnum.INCOMPATIBLEWITHCURRENTVEHICLE
        if self.wotPlusCtrl.hasVehicleCrewIdleXP(self.__currentVehicle.invID):
            return IdleCrewBonusEnum.ACTIVEONCURRENTVEHICLE
        return IdleCrewBonusEnum.ACTIVEONANOTHERVEHICLE if self.wotPlusCtrl.getVehicleIDWithIdleXP() else IdleCrewBonusEnum.ENABLED

    def __updateCrewBooksAmount(self, vmCrewBooks):
        if self.__currentVehicle is None:
            vmCrewBooks.setNewAmount(0)
            vmCrewBooks.setTotalAmount(0)
        else:
            viewedCache = crewBooksViewedCache()
            vmCrewBooks.setNewAmount(viewedCache.newCrewBooksAmount)
            vmCrewBooks.setTotalAmount(viewedCache.crewBooksAmount)
        return

    def __updateCrewBooksDiscount(self, vmCrewBooks):
        shop = self.itemsCache.items.shop
        vmCrewBooks.setHasDiscount(shop.freeXPToTManXPRate != shop.defaults.freeXPToTManXPRate)
