# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/personal_case.py
from collections import defaultdict
import typing
import nations
from account_helpers.AccountSettings import CREW_SKINS_VIEWED, CREW_BOOKS_VIEWED
from async import async, await
from frameworks.wulf import ViewFlags, ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from gui.impl.auxiliary.detachment_helper import fillRoseSheetsModel, fillDetachmentTopPanelModel, getDetachmentVehicleSlotMoney, fillVehicleSlotPriceModel, getDetachmentDismissState
from gui.impl.auxiliary.instructors_helper import showInstructorSlotsDisabledMessage, fillInstructorBaseModel, GUI_NO_INSTRUCTOR_ID
from gui.impl.backport import BackportContextMenuWindow
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.dismiss_states import DismissStates
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_short_model import PerkShortModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.detachment.personal_case.instructor_slot_model import InstructorSlotModel
from gui.impl.gen.view_models.views.lobby.detachment.personal_case.vehicle_slot_model import VehicleSlotModel
from gui.impl.gen.view_models.views.lobby.detachment.personal_case_model import PersonalCaseModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.points_info_tooltip_model import PointsInfoTooltipModel
from gui.impl.lobby.detachment.context_menu.context_menu_helper import getContextMenuData
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl
from gui.impl.lobby.detachment.navigation_view_settings import NavigationViewSettings
from gui.impl.lobby.detachment.sound_constants import BARRACKS_SOUND_SPACE
from gui.impl.lobby.detachment.tooltips.dismiss_tooltip import DismissTooltip
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import getInstructorTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.perk_tooltip import PerkTooltip
from gui.impl.lobby.detachment.tooltips.points_info_tooltip_view import PointInfoTooltipView
from gui.impl.lobby.detachment.tooltips.rank_tooltip import RankTooltip
from gui.impl.lobby.detachment.tooltips.skills_branch_view import SkillsBranchTooltipView
from gui.impl.lobby.detachment.tooltips.commander_perk_tooltip import CommanderPerkTooltip
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.event_dispatcher import isViewLoaded, showInstructorPageWindow
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getIconResource, getIconResourceName, getNationLessName
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.shared.gui_items.perk import PerkGUI
from gui.shared.gui_items.processors.detachment import DetachmentUnlockVehicleSlot
from gui.shared.money import Currency
from gui.shared.utils import decorators
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shop import showBuyGoldForDetachmentVehicleSlot
from helpers.dependency import descriptor
from items import ITEM_TYPES
from items.components.detachment_constants import DemobilizeReason, DetachmentSlotType, NO_DETACHMENT_ID, PROGRESS_MAX
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.game_control import IDetachmentController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.constants import GROUP, ACTION
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger
if typing.TYPE_CHECKING:
    from frameworks.wulf.view.view import View
    from frameworks.wulf.view.view_event import ViewEvent
    from gui.shared.gui_items.detachment import Detachment
    from gui.shared.gui_items.Vehicle import Vehicle

class PersonalCase(NavigationViewImpl):
    __itemsCache = descriptor(IItemsCache)
    __lobbyContext = descriptor(ILobbyContext)
    __detachmentCache = descriptor(IDetachmentCache)
    __detachmentController = descriptor(IDetachmentController)
    __settingsCore = descriptor(ISettingsCore)
    __gui = descriptor(IGuiLoader)
    __slots__ = ('_detachmentInvID', '_detachment', '__playAnimationSound', '__tooltipByContentID')
    _CLOSE_IN_PREBATTLE = True
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    uiLogger = DetachmentLogger(GROUP.DETACHMENT_PERSONAL_CASE)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = PersonalCaseModel()
        super(PersonalCase, self).__init__(settings, True, ctx=ctx)
        ctx = self._navigationViewSettings.getViewContextSettings()
        self._detachmentInvID = ctx.get('detInvID')
        self._detachment = None
        self.__playAnimationSound = False
        rTooltip = R.views.lobby.detachment.tooltips
        self.__tooltipByContentID = {rTooltip.PerkTooltip(): self.__getPerkTooltip,
         rTooltip.CommanderPerkTooltip(): self.__getCommanderPerkTooltip,
         rTooltip.PointsInfoTooltip(): self.__getPointsInfoTooltip,
         rTooltip.SkillsBranchTooltip(): self.__getSkillsBranchTooltip,
         rTooltip.InstructorTooltip(): self.__getInstructorTooltip,
         rTooltip.PremiumVehicleSlotTooltip(): self.__getPremiumVehicleSlotTooltip,
         rTooltip.LevelBadgeTooltip(): self.__getLevelBadgeTooltip,
         rTooltip.DismissTooltip(): self.__getDismissTooltip,
         rTooltip.RankTooltip(): self.__getRankTooltip,
         R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent(): self.__getBackportTooltip}
        return

    @property
    def viewModel(self):
        return super(PersonalCase, self).getViewModel()

    def isParamsEqual(self, ctx):
        detInvID = ctx.get('detInvID')
        return True if detInvID is None else int(self._detachmentInvID) == int(detInvID)

    def createToolTipContent(self, event, contentID):
        createTooltip = self.__tooltipByContentID.get(contentID)
        return createTooltip(event) if createTooltip else super(PersonalCase, self).createToolTipContent(event, contentID)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            contextMenuData = getContextMenuData(event, self.__itemsCache, self.__detachmentCache)
            if contextMenuData is not None:
                window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                window.load()
                return window
        return super(PersonalCase, self).createContextMenuContent(event)

    def _initialize(self, *args, **kwargs):
        super(PersonalCase, self)._initialize()
        self.viewModel.setCurrentViewId(NavigationViewModel.PERSONAL_CASE_BASE)
        self.uiLogger.startAction(ACTION.OPEN)
        instructorPage = self.__gui.windowsManager.getViewByLayoutID(R.views.lobby.detachment.InstructorPageView())
        if instructorPage:
            instructorPage.destroyWindow()

    def _finalize(self):
        self.uiLogger.stopAction(ACTION.OPEN)
        self.__tooltipByContentID.clear()
        super(PersonalCase, self)._finalize()
        if self.__detachmentController.isConnected:
            for index in xrange(self._detachment.maxVehicleSlots):
                if index < len(self._detachment.getVehicleCDs()):
                    self.__detachmentController.saveAnimationAsShown(self._detachmentInvID, DetachmentSlotType.VEHICLES, index)

            for index in xrange(self._detachment.getMaxInstructorsCount()):
                if index < len(self._detachment.getInstructorsIDs()):
                    self.__detachmentController.saveAnimationAsShown(self._detachmentInvID, DetachmentSlotType.INSTRUCTORS, index)

    def _initModel(self, vm):
        super(PersonalCase, self)._initModel(vm)
        self.__onClientUpdate(vm)

    def _addListeners(self):
        super(PersonalCase, self)._addListeners()
        self.viewModel.onVehicleSlotClick += self.__onVehicleSlotClick
        self.viewModel.onInstructorClick += self.__onInstructorClick
        self.viewModel.onDemountInstructorClick += self.__onDemountInstructorClick
        self.viewModel.onInstructorsPreviewClick += self.__onInstructorsPreviewClick
        self.viewModel.onDemobilizeDetachmentClick += self.__onDemobilizeDetachmentClick
        self.viewModel.onPerksPreviewClick += self.__onPerksPreviewClick
        self.__detachmentController.onSlotsAnimationRenew += self.__onSlotsAnimationRenew
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        g_clientUpdateManager.addCallbacks({'inventory.{}'.format(ITEM_TYPES.detachment): self.__onClientUpdateTran,
         'inventory.{}'.format(ITEM_TYPES.crewBook): self.__onClientUpdateTran,
         'inventory.{}'.format(ITEM_TYPES.crewSkin): self.__onClientUpdateTran,
         'cache.vehsLock': self.__onClientUpdateTran,
         'shop': self.__onClientUpdateTran})
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdate)

    def _removeListeners(self):
        super(PersonalCase, self)._removeListeners()
        self.viewModel.onVehicleSlotClick -= self.__onVehicleSlotClick
        self.viewModel.onInstructorClick -= self.__onInstructorClick
        self.viewModel.onDemountInstructorClick -= self.__onDemountInstructorClick
        self.viewModel.onInstructorsPreviewClick -= self.__onInstructorsPreviewClick
        self.viewModel.onDemobilizeDetachmentClick -= self.__onDemobilizeDetachmentClick
        self.viewModel.onPerksPreviewClick -= self.__onPerksPreviewClick
        self.__detachmentController.onSlotsAnimationRenew -= self.__onSlotsAnimationRenew
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _onLoadPage(self, args=None):
        if args['viewId'] != NavigationViewModel.BARRACK_DETACHMENT:
            args['detInvID'] = self._detachmentInvID
        super(PersonalCase, self)._onLoadPage(args)

    def __updateDetachmentSource(self):
        self._detachment = self.__detachmentCache.getDetachment(self._detachmentInvID)

    def __getCurrentBuild(self):
        return self._detachment.getDescriptor().build

    def __getVehicleLockState(self):
        if self._detachment.isInTank:
            vehicle = self.__itemsCache.items.getVehicle(self._detachment.vehInvID)
            return vehicle.isCrewLocked
        return False

    def __updateTopPanel(self, model):
        fillDetachmentTopPanelModel(model=model.topPanelModel, detachment=self._detachment)

    def __updateCurrentVehicle(self, model):
        vehicleVM = model.currentVehicle
        if self._detachment.isInTank:
            currentVehicle = self.__itemsCache.items.getVehicle(self._detachment.vehInvID)
            if currentVehicle is not None:
                vehicleVM.setType(currentVehicle.type)
                vehicleVM.setName(currentVehicle.userName)
                vehicleVM.setNation(nations.MAP[currentVehicle.nationID])
                vehicleVM.setLevel(currentVehicle.level)
                resName = getIconResourceName(getNationLessName(currentVehicle.name))
                vehicleVM.setIcon(resName)
                vehicleVM.setIsElite(currentVehicle.isElite)
        return

    def __updatePersonalCaseInfo(self, model):
        model.setHasVehicleLock(self.__getVehicleLockState())
        model.setCanCustomizeCommander(self._detachment.canCustomizeCommander)
        dismissState = getDetachmentDismissState(self._detachment)
        model.setIsDismissDisable(dismissState != DismissStates.AVAILABLE)
        if self.__lobbyContext.getServerSettings().isCrewSkinsEnabled() and self._detachment.canCustomizeCommander:
            skins = self.__itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_SKINS, REQ_CRITERIA.CREW_ITEM.IN_ACCOUNT)
            newSkins = sum((item.getNewCount() for item in skins.itervalues() if not item.getNation() or item.getNation() == nations.NAMES[self._detachment.nationID]))
            model.setNewSkinsCount(newSkins)
        booksCount = crewBooksViewedCache().getNewBooksCount()
        model.setNewAllowanceCount(booksCount)

    def __updateVehicleSlots(self, model):
        vehicleSlots = model.getVehicleSlots()
        vehicleSlots.clear()
        slotLevels = self._detachment.getVehicleSlotUnlockLevels()
        hasLockCrew = self.__getVehicleLockState()
        firstNotAvailable = True
        for index, slotInfo in enumerate(self._detachment.getDescriptor().getAllSlotsInfo(DetachmentSlotType.VEHICLES)):
            if index > 0 and hasLockCrew:
                break
            vehicleSlot = VehicleSlotModel()
            vehicleSlot.setId(index)
            if slotInfo.available:
                vehicleCD = slotInfo.typeCompDescr
                isAnimationActive = self.__detachmentController.isSlotAnimationActive(self._detachmentInvID, DetachmentSlotType.VEHICLES, index)
                vehicleSlot.setIsAnimationActive(isAnimationActive)
                vehicleSlot.setIsLocked(slotInfo.locked)
                if isAnimationActive:
                    self.__playAnimationSound = True
                if vehicleCD:
                    vehicleGuiItem = self.__itemsCache.items.getItemByCD(vehicleCD)
                    vehicleSlot.setName(vehicleGuiItem.userName)
                    vehicleSlot.setLevel(vehicleGuiItem.level)
                    vehicleSlot.setType(vehicleGuiItem.uiType)
                    vehName = getNationLessName(vehicleGuiItem.name)
                    vehicleImageR = R.images.gui.maps.shop.vehicles.c_180x135.dyn(getIconResourceName(vehName))
                    if not vehicleImageR.exists():
                        vehicleImageR = getIconResource(vehicleGuiItem.name)
                    vehicleSlot.setIcon(backport.image(vehicleImageR()))
                    vehicleSlot.setNation(vehicleGuiItem.nationName)
                    vehicleSlot.setIsElite(vehicleGuiItem.isElite)
                    vehicleSlot.setStatus(VehicleSlotModel.ASSIGNED)
                else:
                    vehicleSlot.setStatus(VehicleSlotModel.EMPTY)
            else:
                vehicleSlot.setLevelReq(slotLevels[index])
                if firstNotAvailable:
                    vehicleSlot.setStatus(VehicleSlotModel.NOT_AVAILABLE_PRICE)
                    fillVehicleSlotPriceModel(vehicleSlot.priceModel, index, self._detachmentInvID, self.__itemsCache)
                    firstNotAvailable = False
                else:
                    vehicleSlot.setStatus(VehicleSlotModel.NOT_AVAILABLE)
            vehicleSlots.addViewModel(vehicleSlot)

        vehicleSlots.invalidate()

    def __getPerkVM(self, perkId, isUltimate=False):
        build = self.__getCurrentBuild()
        perk = PerkShortModel()
        perk.setId(perkId)
        if perkId in build:
            perk.setPoints(0 if isUltimate else build[perkId])
        return perk

    def __updateInstructorSlots(self, model):
        detachment = self._detachment
        instructorSlots = model.getInstructorSlots()
        instructorSlots.clear()
        instructorUnlockLevels = detachment.getInstructorUnlockLevels()
        instructorsIDs = detachment.getInstructorsIDs()
        hasLockCrew = self.__getVehicleLockState()
        processedInstrs = set()
        occupiedSlotsCount = len(instructorsIDs)
        for index in xrange(detachment.getMaxInstructorsCount()):
            if index < occupiedSlotsCount:
                instructorInvID = instructorsIDs[index]
                instructorItem = self.__detachmentCache.getInstructor(instructorInvID)
                if instructorItem and instructorInvID in processedInstrs:
                    continue
                elif instructorItem:
                    processedInstrs.add(instructorInvID)
                instructorSlot = InstructorSlotModel()
                if instructorItem is not None:
                    instructorSlot.setStatus(InstructorSlotModel.ASSIGNED)
                    instructorSlot.setSlotsCount(instructorItem.descriptor.getSlotsCount())
                    fillInstructorBaseModel(instructorSlot, instructorItem)
                    instructorSlot.setName(instructorItem.fullName)
                    instructorSlot.setNation(instructorItem.nationName)
                    instructorSlot.setBonusExperience(instructorItem.xpBonus * PROGRESS_MAX)
                    instructorSlot.setIsUnique(instructorItem.isUnremovable or hasLockCrew)
                    instructorSlot.setBackground(instructorItem.pageBackground)
                    instructorSlot.setIsVoiced(bool(instructorItem.voiceOverID))
                    instructorSlot.setIsVoiceActive(detachment.getDescriptor().getActiveInstructorInvID() == instructorItem.invID)
                    perksList = instructorSlot.getPerks()
                    perksList.clear()
                    for perkID, pointsCount, overcap in instructorItem.getPerksInfluence():
                        perk = PerkGUI(perkID)
                        perkVM = PerkShortModel()
                        perkVM.setId(perkID)
                        perkVM.setPoints(pointsCount)
                        perkVM.setIsOvercapped(overcap > 0)
                        perkVM.setIcon(perk.icon)
                        perksList.addViewModel(perkVM)

                else:
                    instructorSlot.setStatus(InstructorSlotModel.EMPTY)
                    instructorSlot.setId(GUI_NO_INSTRUCTOR_ID)
                isAnimationActive = self.__detachmentController.isSlotAnimationActive(self._detachmentInvID, DetachmentSlotType.INSTRUCTORS, index, checkSlotEmpty=False)
                instructorSlot.setIsAnimationActive(isAnimationActive)
                if isAnimationActive:
                    self.__detachmentController.saveAnimationAsShown(self._detachmentInvID, DetachmentSlotType.INSTRUCTORS, index)
                    self.__playAnimationSound = True
            else:
                instructorSlot = InstructorSlotModel()
                instructorSlot.setLevelReq(instructorUnlockLevels[index])
                instructorSlot.setStatus(InstructorSlotModel.LOCKED)
                instructorSlot.setId(GUI_NO_INSTRUCTOR_ID)
            instructorSlot.setSlotIndex(index)
            instructorSlots.addViewModel(instructorSlot)

        instructorSlots.invalidate()
        model.setIsInstPreviewAvailable(any(instructorsIDs))
        return

    def __updatePerks(self, model):
        perksVM = model.getPerks()
        perksVM.clear()
        detachment = self._detachment
        build = self.__getCurrentBuild()
        detDescr = detachment.getDescriptor()
        totalPerks = detachment.getPerks()
        perksMatrix = detDescr.getPerksMatrix()
        ultimatePerksIDs = []
        perksIDs = []
        instructorBonuses = defaultdict(int)
        for _, perkID, bonus, _ in detachment.getPerksInstructorInfluence():
            instructorBonuses[perkID] += bonus

        boosterBonuses = defaultdict(int)
        for _, perkID, bonus, _ in detachment.getPerksBoosterInfluence():
            boosterBonuses[perkID] += bonus

        for branchID in perksMatrix.branches.iterkeys():
            nonUltimatePerks = perksMatrix.getNonUltimatePerksInBranch(branchID)
            ultimatePerks = perksMatrix.getUltimatePerksInBranch(branchID)
            ultimatePerksIDs.extend((perkID for perkID in ultimatePerks if perkID in build))
            perksIDs.extend((perkID for perkID in nonUltimatePerks if perkID in build or perkID in instructorBonuses or perkID in boosterBonuses))

        for perkId in ultimatePerksIDs:
            perksVM.addViewModel(self.__getPerkVM(perkId, True))

        for perkId in perksIDs:
            perkVM = self.__getPerkVM(perkId)
            perkVM.setInstructorPoints(instructorBonuses[perkId])
            if perkId in boosterBonuses:
                perkVM.setBoosterPoints(boosterBonuses[perkId])
            perkVM.setIsOvercapped(totalPerks.get(perkId, 0) > perksMatrix.perks[perkId].max_points)
            perksVM.addViewModel(perkVM)

        perksVM.invalidate()

    def __updateRose(self, model):
        fillRoseSheetsModel(roseModel=model.topPanelModel.roseModel, detachment=self._detachment, newBuild=self.__getCurrentBuild())

    def __onClientUpdateTran(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            self.__onClientUpdate(model)

    def __onClientUpdate(self, model):
        self.__updateDetachmentSource()
        self.__updateTopPanel(model)
        self.__updatePersonalCaseInfo(model)
        self.__updateSlots(model)
        self.__updatePerks(model)
        self.__updateRose(model)
        self.__updateCurrentVehicle(model)

    def __onMoneyUpdate(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            self.__updateSlots(model, updateInstructorsSlots=False)

    def __onSlotsAnimationRenew(self, detInvID):
        if self._detachmentInvID == detInvID:
            with self.viewModel.transaction() as model:
                self.__updateSlots(model)

    def __updateSlots(self, model, updateVehiclesSlots=True, updateInstructorsSlots=True):
        self.__playAnimationSound = False
        if updateVehiclesSlots:
            self.__updateVehicleSlots(model)
        if updateInstructorsSlots:
            self.__updateInstructorSlots(model)
        if self.__playAnimationSound:
            self.soundManager.playInstantSound(backport.sound(R.sounds.detachment_recruiting()))

    def __onSettingsChanged(self, diff):
        if CREW_SKINS_VIEWED in diff or CREW_BOOKS_VIEWED in diff:
            with self.viewModel.transaction() as model:
                self.__updatePersonalCaseInfo(model)

    def __onVehicleSlotClick(self, event):
        slotIndex = event.get('slotIndex')
        unlockedVehicleSlots = self._detachment.getVehicleCDs()
        if self._detachmentInvID != NO_DETACHMENT_ID and slotIndex < len(unlockedVehicleSlots):
            g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.SPECIALIZATION_VEHICLE_LIST_CHOICE)
            self._showDetachmentView(NavigationViewModel.VEHICLE_LIST, {'detInvID': self._detachmentInvID,
             'vehicleSlotIndex': int(slotIndex)})
        elif slotIndex == len(unlockedVehicleSlots):
            self.__buyVehicleSlot(slotIndex)

    def __canPurchaseVehicleSlot(self, slotIndex):
        money = getDetachmentVehicleSlotMoney(self._detachmentInvID, slotIndex, default=False)
        currency = money.getCurrency(byWeight=True)
        price = money.get(currency)
        playerCurrencyAmount = self.__itemsCache.items.stats.money.get(currency)
        return (price <= playerCurrencyAmount, price, currency)

    @async
    def __buyVehicleSlot(self, slotIndex):
        if isViewLoaded(R.views.lobby.detachment.dialogs.BuyVehicleSlotDialogView()):
            return
        canPurchase, price, currency = self.__canPurchaseVehicleSlot(slotIndex)
        if not canPurchase:
            if currency == Currency.GOLD:
                self.uiLogger.log(ACTION.BUY_GOLD)
                showBuyGoldForDetachmentVehicleSlot(price)
            return
        g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.BUY_VEHICLE_SLOT_DIALOG)
        sdr = yield await(dialogs.buyVehicleSlot(self.getParentWindow(), ctx={'slotID': slotIndex,
         'detInvID': self._detachmentInvID}))
        if sdr.result:
            self.__unlockVehicleSlot()

    def __getPerkTooltip(self, event):
        perkId = event.getArgument('id')
        PerkTooltip.uiLogger.setGroup(self.uiLogger.group)
        return PerkTooltip(perkId, detachmentInvID=self._detachmentInvID)

    def __getCommanderPerkTooltip(self, event):
        perkType = event.getArgument('perkType')
        return CommanderPerkTooltip(perkType=perkType)

    def __getPointsInfoTooltip(self, event):
        PointInfoTooltipView.uiLogger.setGroup(self.uiLogger.group)
        return PointInfoTooltipView(event.contentID, state=PointsInfoTooltipModel.DEFAULT, isClickable=True, detachmentID=self._detachmentInvID)

    def __getSkillsBranchTooltip(self, event):
        course = event.getArgument('course')
        SkillsBranchTooltipView.uiLogger.setGroup(self.uiLogger.group)
        return SkillsBranchTooltipView(detachmentID=self._detachmentInvID, branchID=int(course) + 1)

    def __getPremiumVehicleSlotTooltip(self, event):
        model = VehicleModel()
        model.setNation(self._detachment.nationName)
        model.setType(self._detachment.classType.replace('-', '_'))
        return ViewImpl(ViewSettings(R.views.lobby.detachment.tooltips.PremiumVehicleSlotTooltip(), model=model))

    def __getLevelBadgeTooltip(self, event):
        LevelBadgeTooltipView.uiLogger.setGroup(self.uiLogger.group)
        return LevelBadgeTooltipView(self._detachmentInvID)

    def __getDismissTooltip(self, event):
        DismissTooltip.uiLogger.setGroup(self.uiLogger.group)
        return DismissTooltip(detachmentID=self._detachmentInvID)

    def __getRankTooltip(self, event):
        RankTooltip.uiLogger.setGroup(self.uiLogger.group)
        return RankTooltip(self._detachment.rankRecord)

    def __getInstructorTooltip(self, event):
        instructorID = event.getArgument('instructorInvID')
        isLocked = event.getArgument('isLocked')
        return getInstructorTooltip(instructorInvID=instructorID, detachment=self._detachment, isLocked=isLocked)

    def __getBackportTooltip(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId == VehicleSlotModel.VEHICLE_SLOT_TOOLTIP:
            id_ = int(event.getArgument('id'))
            vehicleCDs = self._detachment.getVehicleCDs()
            if id_ < len(vehicleCDs) and vehicleCDs[id_] is not None:
                return createBackportTooltipContent(TOOLTIPS_CONSTANTS.DETACHMENT_VEHICLE_PARAMETERS, (vehicleCDs[id_], self._detachmentInvID))
            vehicleSlotList = self.viewModel.getVehicleSlots()
            model = vehicleSlotList.getValue(id_)
            rTooltips = R.views.lobby.detachment.tooltips
            return ViewImpl(ViewSettings(rTooltips.VehicleSlotTooltip(), model=model))
        elif tooltipId == TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY:
            currency = event.getArgument('currency')
            value = int(event.getArgument('value', 0))
            shortage = max(value - self.__itemsCache.items.stats.money.get(currency, 0), 0)
            return createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (shortage, currency))
        else:
            return

    def __onInstructorClick(self, event):
        slotID = int(event.get('slotID'))
        instructorIDs = self._detachment.getInstructorsIDs()
        if slotID >= len(instructorIDs):
            return
        elif not self.__lobbyContext.getServerSettings().isInstructorSlotsEnabled():
            showInstructorSlotsDisabledMessage()
            return
        else:
            instructorInvID = instructorIDs[slotID]
            args = {'instructorInvID': instructorInvID if instructorInvID is not None else 0,
             'slotID': slotID,
             'detInvID': self._detachmentInvID}
            if instructorInvID is not None:
                g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.INSTRUCTOR_PAGE)
                showInstructorPageWindow({'navigationViewSettings': NavigationViewSettings(NavigationViewModel.INSTRUCTOR_PAGE, args, self._navigationViewSettings)})
            else:
                g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.INSTRUCTOR_CHOICE_LIST)
                self._showDetachmentView(NavigationViewModel.INSTRUCTORS_LIST, args)
            return

    def __onPerksPreviewClick(self):
        self._showDetachmentView(NavigationViewModel.LEARNED_SKILLS, {'detInvID': self._detachmentInvID})

    @async
    def __onDemountInstructorClick(self, event):
        if isViewLoaded(R.views.lobby.detachment.dialogs.DemountInstructorDialogView()):
            return
        else:
            instructorInvID = event.get('instructorInvID')
            if instructorInvID is None:
                return
            if not self.__lobbyContext.getServerSettings().isInstructorSlotsEnabled():
                showInstructorSlotsDisabledMessage()
                return
            g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.DEMOUNT_INSTRUCTOR_DIALOG)
            yield await(dialogs.demountInstructor(self.getParentWindow(), ctx={'instructorInvID': instructorInvID}))
            return

    def __onInstructorsPreviewClick(self):
        self._showDetachmentView(NavigationViewModel.INSTRUCTORS_OFFICE, {'detInvID': self._detachmentInvID})

    @async
    def __onDemobilizeDetachmentClick(self):
        sdr = yield await(dialogs.showDetachmentDemobilizeDialogView(self._detachmentInvID, DemobilizeReason.DISMISS))
        if sdr.busy:
            return
        g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.DEMOBILIZE_DETACHMENT_DIALOG)
        isOk, data = sdr.result
        if isOk == DialogButtons.SUBMIT:
            ActionsFactory.doAction(ActionsFactory.DEMOBILIZED_DETACHMENT, data['detInvID'], data['allowRemove'], data['freeExcludeInstructors'])
            self._onClose()

    @decorators.process('updating')
    def __unlockVehicleSlot(self):
        processor = DetachmentUnlockVehicleSlot(self._detachmentInvID)
        result = yield processor.request()
        SystemMessages.pushMessages(result)
