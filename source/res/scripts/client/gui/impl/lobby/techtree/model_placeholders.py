# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/techtree/model_placeholders.py
import typing
import nations
from nations import INDICES as NATION_NAME_TO_INDEX
from account_helpers.AccountSettings import AccountSettings, Paragons as ParagonsAccountSettingsKeys
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen.view_models.views.lobby.techtree.node_relation import LineType, NodeRelation
from gui.impl.gen.view_models.views.lobby.techtree.node_tech_tree_model import NodeTechTreeModel as NodeModel
from gui.impl.gen.view_models.views.lobby.techtree.tech_tree_nation_model import TechTreeNationModel
from gui.impl.gen.view_models.views.lobby.techtree.vehicle_node_data import VehicleNodeData
from gui.impl.gen.view_models.views.lobby.techtree.tech_tree_buttons import ButtonType, State
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IEarlyAccessController, IParagonsController
from gui.shared.ext_money import ExtendedMoney
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.techtree.selected_nation import SelectedNation
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.views.lobby.techtree.vehicle_tech_tree_model import VehicleTechTreeModel
    from gui.impl.gen.view_models.views.lobby.techtree.paragons_unlocked_branch import ParagonsUnlockedBranch
    from gui.impl.gen.view_models.views.lobby.techtree.item_unlock import ItemUnlock
    from gui.impl.gen.view_models.views.lobby.techtree.tech_tree_buttons import TechTreeButtons as Button
    from skeletons.gui.techtree_events import ITechTreeEventsListener
    from gui.techtree.nodes import ExposedNode
    from gui.techtree.settings import UnlockProps
TECH_TREE_BUTTONS_PRIORITIES = {ButtonType.EARLYACCESS: 1,
 ButtonType.PARAGONS: 2}

def fillNationTechTreeModel(model, techTreeEventListener, availableNations):
    actionNations = techTreeEventListener.getNations(unviewed=True)
    with model.transaction():
        aNations = model.getAvailableNations()
        aNations.clear()
        for an in availableNations:
            nationModel = TechTreeNationModel()
            nationIdx = nations.INDICES.get(an, nations.NONE_INDEX)
            nationModel.setNation(an)
            nationModel.setNationIndex(nationIdx)
            nationModel.setHasNewDiscountEvent(nationIdx in actionNations)
            aNations.addViewModel(nationModel)

        aNations.invalidate()


def fillVehicleTechTreeNodesModel(model, nodes):
    with model.transaction():
        nodesArray = model.getNodes()
        nodesRelations = model.getNodesRelation()
        vehiclesData = model.getVehiclesData()
        nodesArray.clear()
        nodesRelations.clear()
        vehiclesData.clear()
        for node in nodes:
            displayInfo = node.getDisplayInfo()
            nodesArray.addViewModel(createNodeModel(node))
            for line in displayInfo['lines']:
                nodesRelations.addViewModel(createNodeRelationModel(node, line))

            if node.getTypeName() == GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.VEHICLE]:
                vehiclesData.addViewModel(createVehicleDataModel(node))

        nodesArray.invalidate()
        nodesRelations.invalidate()
        vehiclesData.invalidate()


def createNodeModel(node):
    displayInfo = node.getDisplayInfo()
    bpfProps = node.getBpfProps()
    nodeModel = NodeModel()
    nodeModel.setId(node.getNodeCD())
    nodeModel.setState(node.getState())
    nodeModel.setExtendedState(node.getExtendedState())
    nodeModel.setItemLevel(node.getLevel())
    nodeModel.setItemType(node.getTypeName())
    nodeModel.setEarnedXP(node.getEarnedXP())
    nodeModel.setBlueprintBalance(bpfProps.filledCount if bpfProps is not None else 0)
    nodeModel.setBlueprintMaxCount(bpfProps.totalCount if bpfProps is not None else 0)
    nodeModel.setBlueprintCanConvert(bpfProps.canConvert if bpfProps is not None else 0)
    nodeModel.setRow(displayInfo['row'])
    nodeModel.setColumn(displayInfo['column'])
    return nodeModel


def createNodeRelationModel(node, lineData):
    nodesRelation = NodeRelation()
    nodesRelation.setNodeInId(lineData['childID'])
    nodesRelation.setNodeOutId(node.getNodeCD())
    nodesRelation.setLineType(getattr(LineType, lineData['lineName'].upper()))
    return nodesRelation


def createVehicleDataModel(node):
    vehicleData = VehicleNodeData()
    vehicleData.setNodeId(node.getNodeCD())
    vehicle = node.getItem()
    if vehicle:
        fillVehicleInfo(vehicleData, vehicle)
        BuyPriceModelBuilder.clearPriceModel(vehicleData.price)
        BuyPriceModelBuilder.fillPriceModelByItemPrice(vehicleData.price, vehicle.getBuyPrice(), checkBalanceAvailability=True)
        fillUnlockModel(vehicleData.unlock, node.getUnlockProps())
    return vehicleData


def fillUnlockModel(model, unlockProps):
    model.setParentID(unlockProps.parentID)
    model.setUnlockIdx(unlockProps.unlockIdx)
    BuyPriceModelBuilder.clearPriceModel(model.xpCost)
    BuyPriceModelBuilder.fillPriceModel(model.xpCost, ExtendedMoney(xp=unlockProps.xpCost), ExtendedMoney(xp=unlockProps.discount), ExtendedMoney(xp=unlockProps.xpFullCost))
    reqs = model.getRequiredItems()
    reqs.clear()
    for idx in unlockProps.required:
        reqs.addNumber(idx)

    reqs.invalidate()


def updateVehiclePrices(model, diff):
    vehiclesData = model.getVehiclesData()
    for vehicleData in vehiclesData:
        diffNode = diff.get(vehicleData.getNodeId(), None)
        if diffNode:
            BuyPriceModelBuilder.clearPriceModel(vehicleData.price)
            BuyPriceModelBuilder.fillPriceModelByItemPrice(vehicleData.price, diffNode.getItem().getBuyPrice(), checkBalanceAvailability=True)

    vehiclesData.invalidate()
    return


def updateVehiclesInfo(model, diff):
    vehiclesData = model.getVehiclesData()
    for vehicleData in vehiclesData:
        diffNode = diff.get(vehicleData.getNodeId(), None)
        if diffNode:
            fillVehicleInfo(vehicleData, diffNode.getItem())

    vehiclesData.invalidate()
    return


def updateVehiclesUnlocks(model, diff):
    vehiclesData = model.getVehiclesData()
    for vehicleData in vehiclesData:
        diffNode = diff.get(vehicleData.getNodeId(), None)
        if diffNode:
            fillUnlockModel(vehicleData.unlock, diffNode.getUnlockProps())

    vehiclesData.invalidate()
    return


def updateVehiclesCmpStatus(model, cmpBasket, itemsCache):
    vehiclesData = model.getVehiclesData()
    for vehicleData in vehiclesData:
        vehicle = itemsCache.items.getItemByCD(vehicleData.getVehicleCD())
        vehicleData.setCanAddToCompare(cmpBasket.isReadyToAdd(vehicle))

    vehiclesData.invalidate()


def updateEarlyAccessNodes(model, earlyAccessCtl):
    nodesArray = model.getNodes()
    for nodeModel in nodesArray:
        nodeModel.setEarlyAccessPrice(earlyAccessCtl.getVehiclePrice(nodeModel.getId()))
        nodeModel.setIsEarlyAccessLocked(nodeModel.getId() in earlyAccessCtl.getBlockedVehicles())

    nodesArray.invalidate()


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def formatBlueprintBalance(model, itemsCache=None):
    bpRequester = itemsCache.items.blueprints
    universalAmount = bpRequester.getIntelligenceCount()
    nationalFragmentsData = bpRequester.getAllNationalFragmentsData()
    selectedNation = SelectedNation.getIndex()
    nationalAmount = nationalFragmentsData.get(selectedNation, 0)
    model.setNationBlueprintsCount(nationalAmount)
    model.setUniversalBlueprintsCount(universalAmount)


def updateBlueprintsMode(model, isBlueprintMode, isEnabled):
    model.setIsBlueprintModeEnabled(isEnabled)
    if isEnabled:
        model.setIsBlueprintMode(isBlueprintMode)
    else:
        model.setIsBlueprintMode(False)


@dependency.replace_none_kwargs(paragonsCtrl=IParagonsController, itemsCache=IItemsCache)
def updateParagonsUnlockedBranches(techTreeModel, paragonsCtrl=None, itemsCache=None):
    if paragonsCtrl is None or itemsCache is None:
        return
    else:
        paragonsUnlockIDsToShow = AccountSettings.getParagons(ParagonsAccountSettingsKeys.NEED_TO_SHOW_ANIMATION_FOR_PARAGONS_UNLOCK_IDS)
        paragonsUnlockModels = techTreeModel.getParagonsUnlockedBranchesToShow()
        paragonsUnlockModels.clear()
        for paragonsUnlockID in paragonsUnlockIDsToShow:
            unlockedBranchModel = techTreeModel.getParagonsUnlockedBranchesToShowType()()
            fillParagonsUnlockedBranchModel(unlockedBranchModel, paragonsCtrl, itemsCache, paragonsUnlockID)
            paragonsUnlockModels.addViewModel(unlockedBranchModel)

        paragonsUnlockModels.invalidate()
        return


def fillParagonsUnlockedBranchModel(unlockedBranchModel, paragonsCtrl, itemsCache, paragonsUnlockID):
    unlockedBranchModel.setParagonsUnlockID(paragonsUnlockID)
    nationIndex = NATION_NAME_TO_INDEX.get(paragonsCtrl.config.getParagonsUnlockNationName(paragonsUnlockID))
    SelectedNation.select(nationIndex)
    unlockedBranchModel.setNation(paragonsCtrl.config.getParagonsUnlockNationName(paragonsUnlockID))
    sortedUnlockedVehicles = sorted((itemsCache.items.getItemByCD(vehicleCD) for vehicleCD in paragonsCtrl.config.getParagonsUnlockVehicles(paragonsUnlockID)), key=lambda vehicle: vehicle.level)
    sortedUnlockedVehicleCDs = [ vehicle.compactDescr for vehicle in sortedUnlockedVehicles ]
    sortedUnlockedVehicleCDsArray = unlockedBranchModel.getUnlockedVehicleCDs()
    sortedUnlockedVehicleCDsArray.clear()
    for vehicleCD in sortedUnlockedVehicleCDs:
        sortedUnlockedVehicleCDsArray.addNumber(vehicleCD)


def addButtonIfDataExists(buttonType, rowToButton, buttonModel, nodesArray, **kwargs):
    data = _getDataForButton(buttonType, nodesArray, **kwargs)
    if data is not None:
        fillTechTreeButtonModel(data, buttonModel, **kwargs)
        addButtonByPriority(rowToButton, buttonModel)
    return


def addButtonByPriority(rowToButton, buttonModel):
    if buttonModel is None:
        return
    else:
        row = buttonModel.getButtonRow()
        type = buttonModel.getButtonType()
        if row not in rowToButton or TECH_TREE_BUTTONS_PRIORITIES[type] < TECH_TREE_BUTTONS_PRIORITIES[rowToButton[row].getButtonType()]:
            rowToButton[row] = buttonModel
        return


def _getDataForButton(buttonType, nodesArray, **kwargs):
    if buttonType == ButtonType.EARLYACCESS:
        affectedVehicles, buttonState = _getEarlyAccessDataForButton()
    elif buttonType == ButtonType.PARAGONS:
        resetBranchID = kwargs.get('resetBranchID', 0)
        affectedVehicles, buttonState = _getParagonsDataForButton(resetBranchID)
    if affectedVehicles:
        lastAffectedVehicle = affectedVehicles[-1]
        vehicleCDs = [ vehicle.intCD for vehicle in affectedVehicles ]
        row = _getNodeRowByVehCD(lastAffectedVehicle.intCD, nodesArray)
        return (buttonType,
         buttonState,
         row,
         vehicleCDs)
    else:
        return None


@dependency.replace_none_kwargs(eaCtrl=IEarlyAccessController)
def _getEarlyAccessDataForButton(eaCtrl=None):
    affectedVehicles = []
    buttonState = None
    if eaCtrl is not None:
        affectedVehicles = [ veh for veh, _ in eaCtrl.getAffectedVehiclesOrderedList() ]
        buttonState = State.ENABLED if not eaCtrl.isPaused() else State.DISABLED
    return (affectedVehicles, buttonState)


@dependency.replace_none_kwargs(paragonsCtrl=IParagonsController, itemsCache=IItemsCache)
def _getParagonsDataForButton(resetBranchID=0, paragonsCtrl=None, itemsCache=None):
    affectedVehicles = []
    buttonState = State.DISABLED
    if paragonsCtrl is None:
        return (affectedVehicles, buttonState)
    else:
        affectedVehicles = paragonsCtrl.getBranchResetVehicles(resetBranchID)
        if paragonsCtrl.isPaused:
            return (affectedVehicles, buttonState)
        if resetBranchID in paragonsCtrl.branches.availableToResetBranchIds:
            buttonState = State.ENABLED
        elif paragonsCtrl.isBranchReset(resetBranchID):
            buttonState = State.DROPPED_BRANCH
        elif paragonsCtrl.isFirstUnlockBranchAvailable(resetBranchID, includeParagonsAvailable=False):
            buttonState = State.FIRST_BRANCH_RESET
        return (affectedVehicles, buttonState)


def _getNodeRowByVehCD(vehCD, nodesArray):
    for nodeModel in nodesArray:
        if nodeModel.getId() == vehCD:
            return nodeModel.getRow()


def fillTechTreeButtonModel(buttonData, buttonModel, **kwargs):
    type, state, row, vehiclesCDs = buttonData
    buttonModel.setBranchID(kwargs.get('resetBranchID', 0))
    buttonModel.setButtonType(type)
    buttonModel.setButtonState(state)
    buttonModel.setButtonRow(row)
    vehiclesCDsModelArray = buttonModel.getVehiclesCDs()
    vehiclesCDsModelArray.clear()
    for vehicleCD in vehiclesCDs:
        vehiclesCDsModelArray.addNumber(vehicleCD)


def fillTechTreeButtonModelArray(rowToButton, buttonsModelArray):
    buttonsModelArray.clear()
    for buttonModel in rowToButton.itervalues():
        buttonsModelArray.addViewModel(buttonModel)

    buttonsModelArray.invalidate()
