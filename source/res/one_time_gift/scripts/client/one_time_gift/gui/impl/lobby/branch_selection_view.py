# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/branch_selection_view.py
import logging
import typing
from adisp import adisp_process
from constants import MAX_VEHICLE_LEVEL
from frameworks.wulf import ViewStatus
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.page.wallet_presenter import CrystalProvider, GoldProvider, CreditsProvider, FreeXpProvider, WalletPresenter
from gui.shared.event_dispatcher import showHangar
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency
from shared_utils import safeCall
from skeletons.gui.shared import IItemsCache
from one_time_gift.gui.gui_constants import TOOLTIP_CONSTANTS
from one_time_gift.gui.impl.gen.view_models.views.lobby.branch_selection_view_model import BranchSelectionViewModel
from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_view_model import MainViews
from one_time_gift.gui.impl.gen.view_models.views.lobby.branch_vehicle_info_model import BranchVehicleInfoModel
from one_time_gift.gui.impl.gen.view_models.views.lobby.branch_view_model import BranchViewModel
from one_time_gift.gui.impl.gen.view_models.views.lobby.nation_view_model import NationViewModel
from one_time_gift.gui.impl.lobby.navigation_presenter import OneTimeGiftNavigationPresenter
from one_time_gift.gui.shared.processors import OneTimeGiftBranchRewardProcessor
from one_time_gift.skeletons.gui.game_control import IOneTimeGiftController
from one_time_gift.gui.impl.lobby.meta_view.sub_view_base import SubViewBase
from one_time_gift_common.one_time_gift_constants import BranchListType, TechTreeBranch
if typing.TYPE_CHECKING:
    from typing import Optional, Callable
_logger = logging.getLogger(__name__)
FIRST_SELECTION_STEP = 1
SECOND_SELECTION_STEP = 2
VETERAN_MAX_SELECTION_STEPS = 1
NEWBIE_MAX_SELECTION_STEPS = 2
MAX_ACCRUED_VEH_LEVEL = MAX_VEHICLE_LEVEL - 1

class BranchSelectionView(SubViewBase):
    __itemsCache = dependency.descriptor(IItemsCache)
    __oneTimeGiftController = dependency.descriptor(IOneTimeGiftController)

    def __init__(self, viewModel, parentView):
        self.__currentBranchListType = None
        self.__allVehiclesPurchased = False
        self.__childViews = {}
        self.__isConfirmationDialogBeingShown = False
        super(BranchSelectionView, self).__init__(viewModel, parentView)
        return

    @property
    def viewId(self):
        return MainViews.BRANCH_SELECTION

    @property
    def viewModel(self):
        return super(BranchSelectionView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BranchSelectionView, self).createToolTip(event)

    @staticmethod
    def getTooltipData(event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId == TOOLTIP_CONSTANTS.ONE_TIME_GIFT_VEHICLE_TOOLTIP:
            vehCD = int(event.getArgument('id'))
            return createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(vehCD,))
        else:
            return None

    def initialize(self, branchListType, allVehiclesPurchased=False, onConfirmCallback=None, onCloseCallback=None, onErrorCallback=None):
        self.__currentBranchListType = branchListType
        self.__allVehiclesPurchased = allVehiclesPurchased
        self.__isConfirmationDialogBeingShown = False
        super(BranchSelectionView, self).initialize(onConfirmCallback, onCloseCallback, onErrorCallback)
        self.__initChildren()
        self.__update()

    def finalize(self):
        self.__currentBranchListType = None
        self.__allVehiclesPurchased = False
        self.__isConfirmationDialogBeingShown = False
        self.__destroyChildren()
        super(BranchSelectionView, self).finalize()
        return

    def _getEvents(self):
        return super(BranchSelectionView, self)._getEvents() + ((self.viewModel.onConfirm, self.__onConfirm),
         (self.viewModel.onClose, self._onClose),
         (self.__oneTimeGiftController.onSettingsChanged, self.__onSettingsChanged),
         (self.__oneTimeGiftController.onEntryPointUpdated, self.__onSettingsChanged))

    def __initChildren(self):
        resId = R.aliases.one_time_gift.default.NavigationBar()
        if resId not in self.__childViews:
            self.__registerChild(resId, OneTimeGiftNavigationPresenter(self._onClose, self.__onInfoAction))
        resId = R.aliases.lobby_header.default.Wallet()
        if resId not in self.__childViews:
            self.__registerChild(resId, WalletPresenter((CrystalProvider(),
             GoldProvider(),
             CreditsProvider(),
             FreeXpProvider())))

    def __registerChild(self, resId, viewComponent):
        self.parentView.setChildView(resId, viewComponent)
        self.__childViews[resId] = viewComponent

    def __destroyChildren(self):
        for resId, child in self.__childViews.iteritems():
            if child.viewStatus not in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
                _logger.debug('Destroying %s', child)
                child.destroy()
            if self.parentView.getChildView(resId) is not None:
                self.parentView.setChildView(resId, None)

        self.__childViews = {}
        return

    def __fillBranches(self, branchesCollection, collection):
        for nation, branches in collection:
            nationVM = NationViewModel()
            nationVM.setNation(nation)
            self.__fillBranchesInNation(nationVM.getBranches(), branches)
            branchesCollection.addViewModel(nationVM)

        branchesCollection.invalidate()

    def __fillBranchesInNation(self, branchesInNation, branches):
        branchesInNation.clear()
        for branch in branches:
            branchVM = BranchViewModel()
            branchVM.setId(branch.branchId)
            self.__fillVehiclesList(branchVM.getVehiclesList(), branch.vehCDs)
            branchVM.setNumVehiclesToCredit(sum((not veh.getObtained() and veh.getVehicleLvl() <= MAX_ACCRUED_VEH_LEVEL for veh in branchVM.getVehiclesList())))
            branchesInNation.addViewModel(branchVM)

        branchesInNation.invalidate()

    def __fillVehiclesList(self, vehArray, vehCDs):
        vehArray.clear()
        for vehCD in vehCDs:
            vehicle = self.__itemsCache.items.getItemByCD(vehCD)
            if vehicle is not None:
                self.__addVehicleToList(vehArray, vehicle)
                if vehicle.level == MAX_ACCRUED_VEH_LEVEL:
                    for unlocked in vehicle.descriptor.type.unlocksDescrs:
                        item = self.__itemsCache.items.getItemByCD(unlocked[1])
                        if isinstance(item, Vehicle):
                            self.__addVehicleToList(vehArray, item)

        vehArray.invalidate()
        return

    def __onInfoAction(self):
        if self.__isConfirmationDialogBeingShown:
            return
        self.__oneTimeGiftController.onShowInfoClicked()

    @args2params(int)
    def __onConfirm(self, branchId):
        try:
            _logger.debug('BranchSelectionView::__onConfirm, branchId: %s', branchId)
            if branchId < 0:
                if self.__oneTimeGiftController.isPlayerNewbie() and self.__allVehiclesPurchased:
                    safeCall(self._onConfirmCallback)
                    return
                _logger.warning('OneTimeGift: Branch selection confirmed with invalid branchId: %s', branchId)
                return
            self.__requestOneTimeGift(branchId)
        except Exception:
            self.__oneTimeGiftController.onViewError()
            raise

    def __onSettingsChanged(self, *_, **__):
        _logger.debug('BranchSelectionView::__onSettingsChanged')
        error = self.__oneTimeGiftController.getAvailabilityError()
        if error is not None:
            safeCall(self._onErrorCallback, error=error)
        return

    @adisp_process
    def __requestOneTimeGift(self, branchID):
        branch = self.__oneTimeGiftController.getBranchById(branchID, self.__currentBranchListType)
        if self.__isBranchPurchased(branch):
            safeCall(self._onErrorCallback)
            return
        self.__isConfirmationDialogBeingShown = True
        result = yield OneTimeGiftBranchRewardProcessor(branch.vehCDs, self.getParentWindow()).request()
        self.__isConfirmationDialogBeingShown = False
        if result.success and callable(self._onConfirmCallback):
            showHangar()
            self._onConfirmCallback(rewards=result.auxData)
            return
        if result.userMsg:
            safeCall(self._onErrorCallback, error=result.userMsg)

    def __update(self):
        curSelectionStep = FIRST_SELECTION_STEP
        maxSelectionSteps = VETERAN_MAX_SELECTION_STEPS
        if self.__oneTimeGiftController.isPlayerNewbie():
            maxSelectionSteps = NEWBIE_MAX_SELECTION_STEPS
            if self.__currentBranchListType == BranchListType.ALL:
                curSelectionStep = SECOND_SELECTION_STEP
        with self.viewModel.transaction() as model:
            branchesArray = model.getBranches()
            branchesArray.clear()
            if self.__allVehiclesPurchased:
                branchesArray.invalidate()
            else:
                self.__fillBranches(model.getBranches(), self.__oneTimeGiftController.getBranchesSortedForNation(self.__currentBranchListType).items())
            model.setSelectionStep(curSelectionStep)
            model.setMaxSelectionSteps(maxSelectionSteps)

    @staticmethod
    def __addVehicleToList(vehArray, vehicle):
        vehInfo = BranchVehicleInfoModel()
        fillVehicleInfo(vehInfo, vehicle)
        vehInfo.setIsElite(vehicle.isElite)
        vehInfo.setIconSmall(vehicle.name.replace(':', '-'))
        vehInfo.setIcon(replaceHyphenToUnderscore(vehicle.name.split(':')[1].lower()))
        vehInfo.setUnlocked(vehicle.isUnlocked)
        vehInfo.setObtained(vehicle.isPurchased)
        vehInfo.setId(vehicle.intCD)
        vehArray.addViewModel(vehInfo)

    def __isBranchPurchased(self, branch):
        for vehCD in branch.vehCDs:
            vehicle = self.__itemsCache.items.getItemByCD(vehCD)
            if not vehicle.isPurchased:
                return False

        return True
