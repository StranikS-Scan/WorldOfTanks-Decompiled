# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/lobby/meta_view/subviews/summary_view.py
from collections import defaultdict
from contextlib import contextmanager
from adisp import adisp_process, adisp_async
from debug_utils import LOG_DEBUG, LOG_DEBUG_DEV, LOG_ERROR
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.wrappers.user_compound_price_model import PriceModelBuilder
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.money import DynamicMoney
from gui.shop import showBuyGoldForBundle
from helpers import dependency, int2roman
from items import vehicles, EQUIPMENT_TYPES
from skeletons.gui.shared import IItemsCache
import typing
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.subcategory_info_value_view_model import SubcategoryInfoValueViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.summary_view_model import SummaryViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.footer_view_model import FooterState
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.vehicle_properties_view_model import VehiclePropertiesViewModel, PropertyInfoViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.property_info_view_model import CategoryType, SubcategoryInfoViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.tech_tree_trade_in_view_model import MainViews
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.vehicle_detail_model import VehicleDetailModel
from tech_tree_trade_in.gui.impl.lobby.dialogs.trade_in_confirmation_dialog import TradeInConfirmationDialogBuilder
from tech_tree_trade_in.gui.shared.event_dispatcher import pushTechTreeTradeInUnavailableNotification
from tech_tree_trade_in.gui.shared.views.helper import packVehicleIconLowerCase
from tech_tree_trade_in.skeletons.gui.game_control import ITechTreeTradeInController, BranchType
from tech_tree_trade_in_common.tech_tree_trade_in_constants import TTT_OP_TYPES
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Optional
    from frameworks.wulf import Array
    from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.footer_view_model import FooterViewModel
rCategory = R.strings.tech_tree_trade_in.summary.vehicleProperties.category
_VEH_TRADED_STATUSES_GROUP = (SummaryViewModel.VEHICLE_TRADED_RESEARCH, SummaryViewModel.VEHICLE_TRADED_RESEARCH_INVENTORY)

def _addEmptyPropertyInfo(propInfoArray, categoryType, amount=0):
    propInfoVM = PropertyInfoViewModel()
    propInfoVM.setCategoryType(categoryType)
    propInfoArray.addViewModel(propInfoVM)
    if amount:
        propInfoVM.setAmount(amount)
    return propInfoVM


@contextmanager
def _addPropertyInfo(propInfoArray, categoryType, amount=0):
    propInfoVM = _addEmptyPropertyInfo(propInfoArray, categoryType, amount)
    yield propInfoVM
    propInfoVM.getSubcategories().invalidate()


def _addEmptySubcategory(propInfoVM, typeName):
    subcatArray = propInfoVM.getSubcategories()
    subcat = SubcategoryInfoViewModel()
    subcatArray.addViewModel(subcat)
    if typeName:
        subcat.setType(typeName)
    return subcat


@contextmanager
def _addSubcategory(propInfoVM, typeName):
    subcat = _addEmptySubcategory(propInfoVM, typeName)
    subcatList = subcat.getList()
    yield subcatList
    subcatList.invalidate()


def _addSubcatListItem(subcatList, label, amount=0):
    itemListModel = SubcategoryInfoValueViewModel()
    itemListModel.setLabel(label)
    itemListModel.setAmount(amount)
    subcatList.addViewModel(itemListModel)


def _convertMultipriceToDynamicMoney(resources):
    multiPrice = {}
    for key, val in resources.iteritems():
        name = key if key != 'fragments' else val.get('type')
        multiPrice[name] = val['value']

    return DynamicMoney(**multiPrice)


def _getMovedItemsSubcategoryText(items):
    return backport.text(rCategory.movedItemsSubcategory()) if items else None


def _getVehTypeIconName(vehicle):
    classTag = vehicle.descriptor.type.classTag
    return '{}_elite'.format(classTag) if vehicle.isElite else classTag


class SummaryView(SubModelPresenter):
    __techTreeTradeInController = dependency.descriptor(ITechTreeTradeInController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewModel, parentView):
        super(SummaryView, self).__init__(viewModel, parentView)
        self.__currentBranchToTradeId = -1
        self.__currentBranchToReceiveId = -1
        self.__ctx = None
        return

    @property
    def viewId(self):
        return MainViews.SUMMARY

    @property
    def viewModel(self):
        return super(SummaryView, self).getViewModel()

    @property
    def footerVM(self):
        return self.parentView.viewModel.mainOverlayModel.footer

    def initialize(self, *args, **kwargs):
        super(SummaryView, self).initialize(*args, **kwargs)
        ctx = kwargs.get('ctx')
        LOG_DEBUG_DEV('TechTreeTradeIn: SummaryView initialized', args, kwargs)
        if not ctx:
            LOG_ERROR('TechTreeTradeIn: SummaryView initialized without context data')
            return
        self.__ctx = ctx
        self.__update()

    def __getBalanceAfterFee(self, fee):
        accountGold = self.__itemsCache.items.stats.money.gold
        return accountGold - fee

    def onConfirm(self):
        price = self.__ctx['price']
        balanceDiff = self.__getBalanceAfterFee(price['gold']['value'])
        if balanceDiff < 0:
            showBuyGoldForBundle(price['gold']['value'], parent=self.getParentWindow())
        else:
            self.requestTradeIn(price)

    @adisp_process
    def requestTradeIn(self, price):
        isOk, _ = yield self.showConfirmDialog()
        if not isOk:
            return
        if self.__hasLockedTradedVehicles():
            pushTechTreeTradeInUnavailableNotification()
            return
        self.__techTreeTradeInController.requestTradeIn(self.__currentBranchToTradeId, self.__currentBranchToReceiveId, price, self.__onTradeInComplete)

    @adisp_async
    @wg_async
    def showConfirmDialog(self, callback):
        builder = TradeInConfirmationDialogBuilder()
        success = yield wg_await(dialogs.showSimpleWithResultData(builder.build(self.parentView)))
        callback(success)

    def __onTradeInComplete(self, result):
        if result.success:
            self.parentView.switchContent({'viewType': MainViews.POST_TRADE})
            return
        if result.msgData.get('errStr') not in ('UNAVAILABLE', 'COOLDOWN'):
            self.parentView.destroy()

    def clear(self):
        super(SummaryView, self).clear()
        self.__currentBranchToTradeId = -1
        self.__currentBranchToReceiveId = -1
        self.__ctx = None
        return

    def __update(self):
        self.__updateSummary()
        self.__updateFooter()

    def __updateSummary(self):
        summaryData = self.__ctx.get('summary')
        if self.__currentBranchToTradeId == summaryData['branchToTradeId'] and self.__currentBranchToReceiveId == summaryData['branchToReceiveId']:
            return
        with self.viewModel.transaction() as model:
            self.__fillBranch(model.branchToReceive, summaryData, BranchType.BRANCHES_TO_RECEIVE)
            self.__fillBranch(model.branchToGive, summaryData, BranchType.BRANCHES_TO_TRADE)
            self.__fillSummary(model.getVehicleProperties(), summaryData)
        self.__currentBranchToTradeId = summaryData['branchToTradeId']
        self.__currentBranchToReceiveId = summaryData['branchToReceiveId']

    def __updateFooter(self):
        price = _convertMultipriceToDynamicMoney(self.__ctx.get('price'))
        with self.footerVM.transaction() as model:
            model.setState(FooterState.COMPOUND_PRICE)
            PriceModelBuilder.clearPriceModel(model.price)
            PriceModelBuilder.fillPriceModel(model.price, price)

    def __fillSummary(self, vehPropsArray, tradeData):
        vehPropsArray.clear()
        for vehCD in tradeData[BranchType.BRANCHES_TO_TRADE]:
            vehicle = self.__itemsCache.items.getItemByCD(vehCD)
            vehOps = self.__getVehOps(vehCD, tradeData)
            vehPropsVM = VehiclePropertiesViewModel()
            vehState = self.__getVehTradeStatus(vehicle, vehOps)
            vehPropsVM.setVehicleState(vehState)
            if vehState in (SummaryViewModel.VEHICLE_TRADED_RESEARCH_INVENTORY, SummaryViewModel.VEHICLE_TRADED_RESEARCH):
                propInfoArray = vehPropsVM.getProperties()
                equipment, battleBoosters = self.__getEquipment(vehOps)
                self.__fillRentalVehicle(propInfoArray, vehicle)
                self.__fillPostProgression(propInfoArray, vehOps)
                self.__fillCrew(propInfoArray, vehOps)
                self.__fillEquipment(propInfoArray, equipment)
                self.__fillEquipment(propInfoArray, battleBoosters, isBattleBooster=True)
                self.__fillShells(propInfoArray, vehOps)
                self.__fillConsumables(propInfoArray, vehOps)
                self.__fillMovedXP(propInfoArray, vehOps)
                self.__fillCustomization(propInfoArray, vehOps)
                self.__fillModules(propInfoArray)
                propInfoArray.invalidate()
            vehPropsArray.addViewModel(vehPropsVM)

        vehPropsArray.invalidate()

    def __fillBranch(self, branchVM, tradeData, branchType):
        with branchVM.transaction():
            branchVM.getVehiclesList().clear()
            self.__setBranchNation(branchVM, tradeData[branchType])
            for vehCD in tradeData[branchType]:
                vehicle = self.__itemsCache.items.getItemByCD(vehCD)
                if vehicle:
                    self.__fillVehicleDetails(branchVM.getVehiclesList(), vehicle, self.__getVehOps(vehCD, tradeData), branchType)

            branchVM.getVehiclesList().invalidate()

    def __fillMovedXP(self, propInfoArray, vehOps):
        xp = vehOps.get(TTT_OP_TYPES.MOVE_XP)
        if not xp:
            return
        xpAmount = xp.get('amount')
        vehFirstTier = self.__itemsCache.items.getItemByCD(xp['intCD'])
        with _addPropertyInfo(propInfoArray, CategoryType.EXPERIENCE) as propInfoVM:
            if xpAmount > 0:
                typeName = backport.text(rCategory.experienceSubcategory())
                with _addSubcategory(propInfoVM, typeName) as subcatList:
                    _addSubcatListItem(subcatList, str(vehFirstTier.level))
                    _addSubcatListItem(subcatList, _getVehTypeIconName(vehFirstTier))
                    _addSubcatListItem(subcatList, vehFirstTier.descriptor.type.shortUserString)
                expSubcatName = backport.text(rCategory.experienceSubcategoryAmount())
                with _addSubcategory(propInfoVM, expSubcatName) as subcatList:
                    _addSubcatListItem(subcatList, 'eliteXP', xpAmount)
            else:
                typeName = backport.text(rCategory.experienceEmpty())
                _addEmptySubcategory(propInfoVM, typeName)

    def __getEquipment(self, vehOps):
        equipment, battleBoosters = [], []
        for intCD in vehOps.get(TTT_OP_TYPES.MOVE_EQUIPMENT, []):
            descriptor = vehicles.getItemByCompactDescr(intCD)
            if hasattr(descriptor, 'equipmentType') and descriptor.equipmentType == EQUIPMENT_TYPES.battleBoosters:
                battleBoosters.append(descriptor)
            equipment.append(descriptor)

        return (equipment, battleBoosters)

    def __fillEquipment(self, propInfoArray, equipment, isBattleBooster=False):
        categoryType = CategoryType.DIRECTIVES if isBattleBooster else CategoryType.EQUIPMENT
        with _addPropertyInfo(propInfoArray, categoryType, len(equipment)) as propInfoVM:
            typeName = _getMovedItemsSubcategoryText(equipment)
            with _addSubcategory(propInfoVM, typeName) as subcatList:
                for descr in equipment:
                    _addSubcatListItem(subcatList, descr.shortUserString, 1)

    def __fillShells(self, propInfoArray, vehOps):
        shells = vehOps.get(TTT_OP_TYPES.MOVE_SHELLS, [])
        with _addPropertyInfo(propInfoArray, CategoryType.AMMUNITION) as propInfoVM:
            if not shells:
                return
            total = 0
            nonZeroShells = [ (intCD, amount) for intCD, amount in shells if amount > 0 ]
            typeName = _getMovedItemsSubcategoryText(nonZeroShells)
            with _addSubcategory(propInfoVM, typeName) as subcatList:
                for intCD, amount in nonZeroShells:
                    total += amount
                    descr = vehicles.getItemByCompactDescr(intCD)
                    _addSubcatListItem(subcatList, descr.shortUserString, amount)

            propInfoVM.setAmount(total)

    def __fillConsumables(self, propInfoArray, vehOps):
        consumables = vehOps.get(TTT_OP_TYPES.MOVE_CONSUMABLES, [])
        with _addPropertyInfo(propInfoArray, CategoryType.CONSUMABLES, len(consumables)) as propInfoVM:
            typeName = _getMovedItemsSubcategoryText(consumables)
            with _addSubcategory(propInfoVM, typeName) as subcatList:
                for intCD in consumables:
                    descr = vehicles.getItemByCompactDescr(intCD)
                    _addSubcatListItem(subcatList, descr.shortUserString, 1)

    def __fillCustomization(self, propInfoArray, vehOps):
        customizationItems = vehOps.get(TTT_OP_TYPES.MOVE_CUSTOMIZATION, [])
        grouped = defaultdict(int)
        total = 0
        for itemTypeCD, count in customizationItems:
            grouped[itemTypeCD] += count
            total += count

        with _addPropertyInfo(propInfoArray, CategoryType.EXTERIORELEMENTS, total) as propInfoVM:
            typeName = _getMovedItemsSubcategoryText(grouped)
            with _addSubcategory(propInfoVM, typeName) as subcatList:
                for intCD, count in grouped.iteritems():
                    item = self.__itemsCache.items.getItemByCD(intCD)
                    _addSubcatListItem(subcatList, item.userName, count)

    def __fillCrew(self, propInfoArray, vehOps):
        turnedToRecruits = vehOps.get(TTT_OP_TYPES.TURN_CREW, [])
        sentToBarracks = vehOps.get(TTT_OP_TYPES.MOVE_TANKMAN, [])
        totalAmount = len(turnedToRecruits) + len(sentToBarracks)
        with _addPropertyInfo(propInfoArray, CategoryType.CREW, totalAmount) as propInfoVM:
            for subcategory, tankmen in (('recruits', turnedToRecruits), ('barracks', sentToBarracks)):
                subcategoryTypeName = backport.text(rCategory.crewSubcategory.dyn(subcategory)())
                if tankmen:
                    with _addSubcategory(propInfoVM, subcategoryTypeName) as subcatList:
                        for strCompactDescr in tankmen:
                            tankman = Tankman(strCompactDescr)
                            if not tankman:
                                LOG_ERROR('TechTreeTradeIn: failed to get tankman from descriptor: ', strCompactDescr)
                            _addSubcatListItem(subcatList, tankman.fullUserName, 1)

    def __fillPostProgression(self, propInfoArray, vehOps):
        postProgData = vehOps.get(TTT_OP_TYPES.POST_PROGRESSION, {})
        postProgLevel = postProgData.get('amount', 0)
        with _addPropertyInfo(propInfoArray, CategoryType.FIELDMODIFICATION, -1) as propInfoVM:
            if postProgLevel <= 0:
                typeName = backport.text(rCategory.fieldModificationEmpty())
                _addEmptySubcategory(propInfoVM, typeName)
                return
            targetVeh = self.__itemsCache.items.getItemByCD(postProgData['intCD'])
            mainSubcatName = backport.text(rCategory.fieldModificationMessage(), level=int2roman(postProgLevel), vehicle='%(vehicle)s')
            with _addSubcategory(propInfoVM, mainSubcatName) as subcatList:
                _addSubcatListItem(subcatList, str(targetVeh.level))
                _addSubcatListItem(subcatList, '{}_elite'.format(targetVeh.descriptor.type.classTag))
                _addSubcatListItem(subcatList, targetVeh.descriptor.type.shortUserString)
            creditsSubcatName = backport.text(rCategory.fieldModificationCredits())
            creditsComp = vehOps.get(TTT_OP_TYPES.CREDITS_COMPENSATION, 0)
            if creditsComp:
                with _addSubcategory(propInfoVM, creditsSubcatName) as subcatList:
                    _addSubcatListItem(subcatList, 'credits', creditsComp)

    def __fillRentalVehicle(self, propInfoArray, vehicle):
        if vehicle.isRented:
            with _addPropertyInfo(propInfoArray, CategoryType.RENTALVEHICLE):
                pass

    def __fillModules(self, propInfoArray):
        with _addPropertyInfo(propInfoArray, CategoryType.MODULES) as propInfoVM:
            subcategoryTypeName = backport.text(rCategory.modulesDescription())
            _addEmptySubcategory(propInfoVM, subcategoryTypeName)

    @staticmethod
    def __getVehOps(vehCD, tradeData):
        return tradeData['operations'].get(vehCD, {})

    @staticmethod
    def __setBranchNation(branchVM, branch):
        nationName = vehicles.getVehicleType(branch[0]).name.split(':')[0]
        branchVM.setNation(nationName)

    def __fillVehicleDetails(self, array, vehicle, vehOps, branchType):
        vehDetails = VehicleDetailModel()
        vehTradeStatus = self.__getVehTradeStatus(vehicle, vehOps)
        fillVehicleInfo(vehDetails, vehicle)
        vehDetails.setIcon(packVehicleIconLowerCase(vehicle))
        vehDetails.setVehicleState(vehTradeStatus)
        if branchType == BranchType.BRANCHES_TO_RECEIVE and vehTradeStatus in _VEH_TRADED_STATUSES_GROUP:
            vehDetails.setIsElite(True)
        array.addViewModel(vehDetails)
        array.invalidate()

    def __getVehTradeStatus(self, vehicle, vehOps):
        isTraded = vehOps.get(TTT_OP_TYPES.DERESEARCH) or vehOps.get(TTT_OP_TYPES.RESEARCH)
        return self.__mapVehicleStatus(isTraded, vehicle.isInInventory or vehOps.get(TTT_OP_TYPES.ACCRUAL), vehicle.isRented)

    @staticmethod
    def __mapVehicleStatus(isTraded=False, isInInventory=False, isRented=False):
        if not isTraded:
            if isInInventory and not isRented:
                return SummaryViewModel.VEHICLE_NOT_TRADED_RESEARCH_INVENTORY
            return SummaryViewModel.VEHICLE_NOT_TRADED_RESEARCH
        return SummaryViewModel.VEHICLE_TRADED_RESEARCH_INVENTORY if isInInventory and not isRented else SummaryViewModel.VEHICLE_TRADED_RESEARCH

    def __hasLockedTradedVehicles(self):
        summaryData = self.__ctx['summary']
        branchToTradeCDs = summaryData[BranchType.BRANCHES_TO_TRADE]
        ops = summaryData['operations']
        for intCD in branchToTradeCDs:
            vehOps = ops.get(intCD)
            if vehOps and (TTT_OP_TYPES.REMOVAL in vehOps or TTT_OP_TYPES.DERESEARCH in vehOps):
                vehicle = self.__itemsCache.items.getItemByCD(intCD)
                if vehicle.isLocked:
                    LOG_DEBUG("TechTreeTradeIn: one of player's traded vehicles is locked", intCD)
                    return True

        return False
