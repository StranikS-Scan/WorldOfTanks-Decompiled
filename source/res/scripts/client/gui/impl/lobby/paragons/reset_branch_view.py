# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/reset_branch_view.py
import typing
from collections import defaultdict
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.customization.shared import TYPES_ORDER
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.paragons.reset_branch_view_model import ResetBranchViewModel, ResetState
from gui.impl.gen.view_models.views.lobby.paragons.reset_vehicle_info_model import ResetVehicleInfoModel
from gui.impl.gen.view_models.views.lobby.paragons.returned_items_model import GroupInfoTypes, ReturnedItemsModel
from gui.impl.gen.view_models.views.lobby.paragons.returned_row_model import ReturnedRowModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.crew.tooltips.tankman_tooltip import TankmanTooltip
from gui.impl.lobby.paragons.paragons_helpers.paragons_model_helpers import fillVehicleModel
from gui.impl.lobby.paragons.paragons_helpers.paragons_helpers import setParagonsResetBranchToShow, getFirstResetHintShown
from gui.impl.lobby.paragons.sound_constants import PARAGONS_RESET_BRANCH_SOUND_SPACE
from gui.impl.lobby.paragons.tooltips.reset_branch_tooltip import ResetBranchTooltip
from gui.impl.lobby.paragons.tooltips.blueprint_universal_tooltip import BlueprintUniversalTooltip
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from helpers import dependency
from items import ITEM_TYPES
from items.components.c11n_constants import ItemTags
from skeletons.gui.game_control import IParagonsController
from skeletons.gui.shared import IItemsCache
from tutorial.control.context import GLOBAL_FLAG
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from frameworks.wulf import Array, View
    from frameworks.wulf.view.view_event import ViewEvent

class ResetBranchView(ViewImpl):
    __slots__ = ('__branchID', '__groupInfoFillersByType', '__vehiclesCopy', '__vehicleConfiguration', '__closeCallback', '__tutorialStorage')
    _COMMON_SOUND_SPACE = PARAGONS_RESET_BRANCH_SOUND_SPACE
    __itemsCache = dependency.descriptor(IItemsCache)
    __paragonsController = dependency.descriptor(IParagonsController)
    __toolTipAlias = (TOOLTIPS_CONSTANTS.HANGAR_CARD_MODULE, TOOLTIPS_CONSTANTS.DEFAULT_SHELL, TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_BLOCK)

    def __init__(self, layoutID, branchID, closeCallback=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = ResetBranchViewModel()
        self.__branchID = branchID
        self.__vehiclesCopy = []
        self.__vehicleConfiguration = ResetBranchViewModel.VAL_CURRENT
        self.__closeCallback = closeCallback
        self.__tutorialStorage = getTutorialGlobalStorage()
        self.__groupInfoFillersByType = {GroupInfoTypes.OPTIONALDEVICES: self.__fillReturnedOptionalDevices,
         GroupInfoTypes.SHELLS: self.__fillReturnedShells,
         GroupInfoTypes.CUSTOMIZATION: self.__fillVehicleOutfit,
         GroupInfoTypes.EQUIPMENTS: self.__fillReturnedEquipments,
         GroupInfoTypes.BATTLEBOOSTERS: self.__fillReturnedBattleBoosters,
         GroupInfoTypes.CREW: self.__fillReturnedCrew}
        super(ResetBranchView, self).__init__(settings)
        Waiting.show('loadPage', isAlwaysOnTop=True, isSingle=True)

    @property
    def viewModel(self):
        return super(ResetBranchView, self).getViewModel()

    def _getEvents(self):
        return ((self.__itemsCache.onSyncCompleted, self.__onInventoryUpdated),
         (self.__paragonsController.onSettingsChanged, self.__onServerSettingsChanged),
         (self.viewModel.onConfirm, self.__resetBranch),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onInstallVehicleConfiguration, self.__onInstallVehicleConfiguration))

    def _onLoading(self, *args, **kwargs):
        super(ResetBranchView, self)._onLoading()
        self.__updateData()

    def _finalize(self):
        super(ResetBranchView, self)._finalize()
        self.__groupInfoFillersByType.clear()
        self.__closeCallback = None
        return

    def __installAutoUnlockedItems(self):
        totalCredits = 0
        for vehicle in self.__vehiclesCopy:
            modulesSellPrice = 0
            stockModules = [ self.__itemsCache.items.getItemByCD(itemCD) for itemCD in vehicle.getAutoUnlockedItems() ]
            equipStockModules = [ item for item in stockModules if item.itemTypeID != ITEM_TYPES.vehicleFuelTank ]
            inventoryStockModules = [ item for item in equipStockModules if item.isInInventory ]
            for module in vehicle.modules:
                if module and module not in equipStockModules:
                    if any((module.itemTypeID == invStockModule.itemTypeID for invStockModule in inventoryStockModules)):
                        modulesSellPrice += int(module.sellPrices.itemPrice.defPrice.credits)

            for equipModule in inventoryStockModules:
                if equipModule and equipModule not in vehicle.modules:
                    modulesSellPrice -= int(equipModule.sellPrices.itemPrice.defPrice.credits)

            totalCredits += self.__updatePrice(vehicle, modulesSellPrice)

        return totalCredits

    def __updatePrice(self, resetVehicle, modulesSellPrice=0):
        with self.viewModel.transaction() as tx:
            for vehicleModel in tx.getResetVehicles():
                if resetVehicle.isInInventory and vehicleModel.vehicleInfo.getVehicleCD() == resetVehicle.compactDescr:
                    sellPrice = int(resetVehicle.sellPrices.itemPrice.defPrice.credits) - modulesSellPrice
                    vehicleModel.setCredits(sellPrice)
                    return sellPrice

    def __updateProgress(self, vehComDescr, vehicleModel):
        vehicleModel.setProgressPoints(self.__paragonsController.getVehicleProgressPoints(vehComDescr))
        vehicleModel.setBlueprintFragments(self.__paragonsController.getVehicleResetBonusBlueprintsCount(vehComDescr))

    def __onInstallVehicleConfiguration(self, event):
        self.__vehicleConfiguration = event.get(ResetBranchViewModel.VEH_CONFIG_KEY, ResetBranchViewModel.VAL_CURRENT)
        if self.__vehicleConfiguration == ResetBranchViewModel.VAL_STOCK:
            totalCredits = self.__installAutoUnlockedItems()
        else:
            totalCredits = sum((self.__updatePrice(vehicle) for vehicle in self.__paragonsController.getBranchResetVehicles(self.__branchID)))
        self.getViewModel().setTotalCredits(totalCredits)

    def __onClose(self):
        closeCallback = self.__closeCallback
        self.destroy()
        if closeCallback is not None:
            closeCallback()
        return

    def __resetBranch(self):
        isStock = self.__vehicleConfiguration == ResetBranchViewModel.VAL_STOCK
        ctx = {'credits': self.viewModel.getTotalCredits()}
        self.__paragonsController.branches.resetBranch(self.__branchID, isStock, ctx, self.__resetCallback)

    def __resetCallback(self, isSuccess):
        setParagonsResetBranchToShow(isShow=isSuccess)
        isFirstResetHintShown = getFirstResetHintShown()
        if not isFirstResetHintShown and isSuccess:
            self.__tutorialStorage.setValue(GLOBAL_FLAG.PARAGONS_FIRST_RESET, isSuccess)
        self.viewModel.setResetState(ResetState.FAILED if not isSuccess else ResetState.SUCCESS)

    def __onServerSettingsChanged(self, serverSettings):
        with self.viewModel.transaction() as tx:
            for vehicleModel in tx.getResetVehicles():
                comDescr = vehicleModel.vehicleInfo.getVehicleCD()
                self.__updateProgress(comDescr, vehicleModel)

    def __onInventoryUpdated(self, _, invDiff):
        if GUI_ITEM_TYPE.VEHICLE in invDiff:
            paragonsChangedVehicles = invDiff[GUI_ITEM_TYPE.VEHICLE] & set((vehicle.intCD for vehicle in self.__paragonsController.getBranchResetVehicles(self.__branchID)))
            if paragonsChangedVehicles:
                self.viewModel.getResetVehicles().clear()
                self.__vehiclesCopy = []
                self.__updateData()
        self.__onInstallVehicleConfiguration({ResetBranchViewModel.VEH_CONFIG_KEY: self.__vehicleConfiguration})

    def __updateData(self):
        with self.viewModel.transaction() as tx:
            tx.setResetState(ResetState.INITIAL)
            tx.setResetBranchesCount(self.__paragonsController.branches.resetBranchesCount)
            tx.setMaxResetBranchesCount(self.__paragonsController.branches.maxResetBranchesCount)
            tx.setTotalCredits(self.__paragonsController.branches.getBranchResetCompensation(self.__branchID))
        resetVehiclesArray = self.viewModel.getResetVehicles()
        if not self.__vehiclesCopy:
            for vehicle in self.__paragonsController.getBranchResetVehicles(self.__branchID):
                self.__vehiclesCopy.append(self.__itemsCache.items.getVehicleCopy(vehicle))

        for resetVehicle in self.__vehiclesCopy:
            resetVehicleModel = self.__getResetVehicleModel(resetVehicle)
            resetVehiclesArray.addViewModel(resetVehicleModel)

        resetVehiclesArray.invalidate()
        if Waiting.isOpened('loadPage'):
            Waiting.hide('loadPage')
            with self.viewModel.transaction() as tx:
                tx.setIsFill(True)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ResetBranchView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.crew.tooltips.TankmanTooltip():
            invID = int(event.getArgument('invID'))
            return TankmanTooltip(invID)
        if contentID == R.views.lobby.paragons.tooltips.ResetBranchTooltip():
            return ResetBranchTooltip(header=event.getArgument('header', ''), description=event.getArgument('description', ''), additionalDescription=event.getArgument('additionalDescription', ''))
        if contentID == R.views.lobby.paragons.tooltips.BlueprintUniversalTooltip():
            vehicleCD = int(event.getArgument('vehicleCD'))
            return BlueprintUniversalTooltip(vehicleCD)
        return super(ResetBranchView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        intCD = int(event.getArgument('intCD') or 0)
        vehicleCD = int(event.getArgument('vehicleCD'))
        alias = event.getArgument('alias')
        if alias in self.__toolTipAlias:
            return backport.createTooltipData(specialAlias=alias, isSpecial=True, specialArgs=[intCD])
        if alias == TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM:
            return backport.createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM, specialArgs=CustomizationTooltipContext(itemCD=intCD))
        return backport.createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AWARD_VEHICLE, specialArgs=[vehicleCD]) if alias == TOOLTIPS_CONSTANTS.AWARD_VEHICLE else None

    def __isStockConfigurationAvailable(self):
        canEquipStock = any((self.__isHaveStockModulesForChange(resetVehicle) for resetVehicle in self.__vehiclesCopy))
        self.viewModel.setCanEquipStock(canEquipStock)

    def __isHaveStockModulesForChange(self, resetVehicle):
        stockModules = [ self.__itemsCache.items.getItemByCD(itemCD) for itemCD in resetVehicle.getAutoUnlockedItems() ]
        equipStockModules = [ item for item in stockModules if item.itemTypeID != ITEM_TYPES.vehicleFuelTank ]
        inventoryStockModules = [ item for item in equipStockModules if item.isInInventory ]
        for module in resetVehicle.modules:
            if module and module not in equipStockModules:
                if any((module.itemTypeID == invStockModule.itemTypeID for invStockModule in inventoryStockModules)):
                    return True

        return False

    def __getResetVehicleModel(self, resetVehicle):
        model = ResetVehicleInfoModel()
        fillVehicleModel(model.vehicleInfo, resetVehicle)
        self.__updateProgress(resetVehicle.compactDescr, model)
        if resetVehicle.isInInventory:
            sellPrice = int(resetVehicle.sellPrices.itemPrice.defPrice.credits)
            model.setCredits(sellPrice)
            self.__fillReturnedItemsArray(model.getReturnedItems(), resetVehicle)
        return model

    def __fillReturnedItemsArray(self, returnedItemsArray, resetVehicle):
        for groupInfoType in GroupInfoTypes:
            returnedItemsModel = ReturnedItemsModel()
            returnedItemsModel.setType(groupInfoType)
            groupInfoArray = returnedItemsModel.getGroupInfo()
            if resetVehicle.isInInventory:
                filler = self.__groupInfoFillersByType[groupInfoType]
                filler(groupInfoArray, resetVehicle)
            groupInfoArray.invalidate()
            returnedItemsArray.addViewModel(returnedItemsModel)

        returnedItemsArray.invalidate()

    def __fillVehicleOutfit(self, groupInfoArray, resetVehicle):
        outfits = resetVehicle.outfits
        allItems = []
        itemToCount = defaultdict(int)
        for outfit in outfits.itervalues():
            if outfit.style:
                allItems.append(outfit.style.compactDescr)
                break
            allItems.extend(outfit.items())

        for itemCD in allItems:
            itemToCount[itemCD] += 1

        installedCustomizations = sorted([ self.__itemsCache.items.getItemByCD(itemCD) for itemCD in itemToCount.keys() ], key=lambda item: TYPES_ORDER.index(item.itemTypeID))
        for item in installedCustomizations:
            if item.tags.issuperset({ItemTags.NATIONAL_EMBLEM}):
                continue
            returnedRowModel = ReturnedRowModel()
            returnedRowModel.setName(item.userName)
            returnedRowModel.setCount(itemToCount[item.intCD])
            returnedRowModel.setIntCD(item.intCD)
            returnedRowModel.setIcon(item.itemTypeName)
            groupInfoArray.addViewModel(returnedRowModel)

    def __fillReturnedOptionalDevices(self, groupInfoArray, resetVehicle):
        for optDevice in resetVehicle.optDevices.setupLayouts.getUniqueItems():
            returnedRowModel = ReturnedRowModel()
            returnedRowModel.setName(optDevice.userName)
            returnedRowModel.setIntCD(optDevice.intCD)
            returnedRowModel.setCount(1)
            returnedRowModel.setIcon(optDevice.iconName)
            returnedRowModel.setOverlayIcon(optDevice.getOverlayType())
            groupInfoArray.addViewModel(returnedRowModel)

    def __fillReturnedShells(self, groupInfoArray, resetVehicle):
        for shell in resetVehicle.shells.setupLayouts.getUniqueItems():
            if shell.count > 0:
                returnedRowModel = ReturnedRowModel()
                returnedRowModel.setName(shell.userName)
                returnedRowModel.setCount(shell.count)
                returnedRowModel.setIntCD(shell.intCD)
                returnedRowModel.setIcon(shell.type)
                groupInfoArray.addViewModel(returnedRowModel)

    def __fillReturnedEquipments(self, groupInfoArray, resetVehicle):
        for equipment in resetVehicle.consumables.setupLayouts.getUniqueItems():
            if not equipment.isBuiltIn:
                returnedRowModel = ReturnedRowModel()
                returnedRowModel.setName(equipment.name)
                returnedRowModel.setIntCD(equipment.intCD)
                returnedRowModel.setCount(1)
                returnedRowModel.setIcon(equipment.name)
                groupInfoArray.addViewModel(returnedRowModel)

    def __fillReturnedBattleBoosters(self, groupInfoArray, resetVehicle):
        installedItems = resetVehicle.battleBoosters.setupLayouts.getUniqueItems()
        for booster in installedItems:
            returnedRowModel = ReturnedRowModel()
            returnedRowModel.setName(booster.userName)
            returnedRowModel.setIntCD(booster.intCD)
            returnedRowModel.setCount(1)
            returnedRowModel.setIcon(booster.descriptor.icon[0])
            returnedRowModel.setOverlayIcon(booster.getOverlayType())
            groupInfoArray.addViewModel(returnedRowModel)

    def __fillReturnedCrew(self, groupInfoArray, resetVehicle):
        for _, tankman in resetVehicle.crew:
            if tankman is not None:
                returnedRowModel = ReturnedRowModel()
                returnedRowModel.setName('{}: {} {}'.format(tankman.roleUserName, tankman.rankUserName, tankman.fullUserName))
                returnedRowModel.setCount(1)
                returnedRowModel.setIntCD(tankman.invID)
                returnedRowModel.setIcon('tankwoman' if tankman.isFemale else 'tankman')
                groupInfoArray.addViewModel(returnedRowModel)

        return


class ResetBranchViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None, branchID=None, closeCallback=None):
        super(ResetBranchViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ResetBranchView(R.views.lobby.paragons.ResetBranchView(), branchID, closeCallback), parent=parent)
