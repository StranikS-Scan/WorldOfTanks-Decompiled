# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/techtree/model_placeholders.py
import typing
import nations
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen.view_models.views.lobby.techtree.node_relation import LineType, NodeRelation
from gui.impl.gen.view_models.views.lobby.techtree.node_tech_tree_model import NodeTechTreeModel
from gui.impl.gen.view_models.views.lobby.techtree.tech_tree_nation_model import TechTreeNationModel
from gui.impl.gen.view_models.views.lobby.techtree.vehicle_node_data import VehicleNodeData
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.veh_post_progression.models.ext_money import ExtendedMoney
from gui.techtree.selected_nation import SelectedNation
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.techtree.vehicle_tech_tree_model import VehicleTechTreeModel
    from gui.impl.gen.view_models.views.lobby.techtree.item_unlock import ItemUnlock
    from skeletons.gui.techtree_events import ITechTreeEventsListener
    from gui.techtree.nodes import ExposedNode
    from gui.techtree.settings import UnlockProps

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
    nodeModel = NodeTechTreeModel()
    nodeModel.setId(node.getNodeCD())
    nodeModel.setState(node.getState())
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
