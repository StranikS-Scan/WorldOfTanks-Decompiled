# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/modules_sub_presenter.py
from __future__ import absolute_import
import typing
from collections import namedtuple
from CurrentVehicle import g_currentPreviewVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import BECOME_ELITE_VEHICLES_WATCHED
from frameworks.wulf.view.array import fillIntsArray
from items.components.c11n_constants import SeasonType
from gui.shared import events
from gui.shared.event_dispatcher import showVehPostProgressionView, showVehicleHubModules
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.impl.backport import createTooltipData
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.tooltips.veh_post_progression_entry_point_tooltip import VehPostProgressionEntryPointTooltip
from gui.impl.lobby.vehicle_hub.sub_presenters.sub_presenter_base import SubPresenterBase
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.modules_model import ModulesModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.research_item_model import ResearchItemModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.research_item_display_model import ResearchItemDisplayModel
from gui.impl.gen.view_models.common.vehicle_mechanic_model import VehicleMechanicModel
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.techtree import dumpers
from gui.Scaleform.daapi.view.lobby.techtree.listeners import TTListenerDecorator
from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.shared.utils.module_upd_available_helper import updateViewedItems
from gui.veh_post_progression.helpers import needToShowCounter
from skeletons.gui.shared import IItemsCache
from helpers import dependency
if typing.TYPE_CHECKING:
    from typing import Optional

class _ModulesTreeViewDumper(dumpers.ResearchItemsObjDumper):
    _itemsCache = dependency.descriptor(IItemsCache)

    def _getItemData(self, node, rootItem):
        itemId = node.getNodeCD()
        item = self._itemsCache.items.getItemByCD(itemId)
        nodePrice = item.getBuyPrice()
        nodePriceCurrency = nodePrice.getCurrency()
        nodeUnlockProps = node.getUnlockProps()
        nodeState = node.getState()
        if node.isVehicle():
            vClass = self._vClassInfo.getInfoByTags(node.getTags())
            mechanics = set()
            imageName = item.name
        else:
            vClass = {'name': node.getTypeName()}
            mechanics = item.getVehicleMechanicsGuiNames(rootItem.descriptor)
            imageName = item.iconName
        return {'id': itemId,
         'image': imageName,
         'userName': node.getShortUserName(),
         'primaryClass': vClass,
         'level': node.getLevel(),
         'state': node.getState(),
         'requiredXp': nodeUnlockProps.xpCost,
         'isDiscountedXp': nodeUnlockProps.xpCost < nodeUnlockProps.xpFullCost,
         'earnedXp': node.getEarnedXP(),
         'priceAmount': nodePrice.price.get(nodePriceCurrency),
         'priceCurrency': nodePriceCurrency,
         'isDiscountedPrice': nodePrice.isActionPrice(),
         'isResearched': NODE_STATE.isUnlocked(nodeState),
         'hasEnoughCurrency': bool(nodeState & NODE_STATE_FLAGS.ENOUGH_MONEY),
         'hasEnoughXP': bool(nodeState & NODE_STATE_FLAGS.ENOUGH_XP),
         'isElite': bool(nodeState & NODE_STATE_FLAGS.ELITE),
         'isDisabled': bool(nodeState & NODE_STATE_FLAGS.LOCKED),
         'autoUnlocked': bool(nodeState & NODE_STATE_FLAGS.AUTO_UNLOCKED),
         'isInstalled': NODE_STATE.isInstalled(nodeState),
         'isInInventory': NODE_STATE.inInventory(nodeState),
         'mechanics': mechanics,
         'displayInfo': node.getDisplayInfo()}


_GUINode = namedtuple('_GUINode', ('id', 'state', 'unlockProps'))

class ModulesSubPresenter(SubPresenterBase):

    def __init__(self, model, parentView):
        super(ModulesSubPresenter, self).__init__(model, parentView)
        self.__listener = None
        self._data = None
        self._eliteWatchedList = None
        return

    @property
    def vehicle(self):
        return self._data.getRootItem()

    def redraw(self):
        self._data.load()
        self.updateResearchItems()
        self.__updateFieldModification()

    def updateResearchItems(self):
        with self.viewModel.transaction() as model:
            researchItems = model.getResearchItems()
            researchItems.clear()
            self.__fillResearchModels(self._data.dump()['top'], model.getPrevResearchItems(), researchItems)
            self.__fillResearchModels(self._data.dump()['nodes'], model.getCurrentResearchItems(), researchItems)

    def setVehicleHubCtx(self, vhCtx):
        super(ModulesSubPresenter, self).setVehicleHubCtx(vhCtx)
        if not self._data:
            self._data = ResearchItemsData(_ModulesTreeViewDumper())
        self._data.setRootCD(self.vehicleHubCtx.intCD)
        self._data.load()
        self.redraw()

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def isUnlockShowed(self):
        return self._eliteWatchedList is not None and self.vehicle.intCD in self._eliteWatchedList

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ModulesSubPresenter, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId == TOOLTIPS_CONSTANTS.TECHTREE_MODULE:
            nodeCD = event.getArgument('nodeCD', 0)
            nodeCD = int(nodeCD)
            if not nodeCD:
                return None
            thisNode = self._data.getNodeByItemCD(nodeCD)
            guiNode = _GUINode(nodeCD, thisNode.getState(), thisNode.getUnlockProps())
            return createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(guiNode, self.vehicleHubCtx.intCD))
        elif tooltipId == TOOLTIPS_CONSTANTS.TECHTREE_VEHICLE:
            vehCD = int(event.getArgument('vehCD', 0))
            if not vehCD:
                return None
            topLevel = event.getArgument('topLevel', False)
            thisNode = self._data.getTopLevelByItemCD(vehCD) if topLevel else self._data.getNodeByItemCD(vehCD)
            guiNode = _GUINode(vehCD, thisNode.getState(), thisNode.getUnlockProps())
            return createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(guiNode, self.vehicleHubCtx.intCD))
        else:
            return None

    def createToolTipContent(self, event, contentID):
        return VehPostProgressionEntryPointTooltip(self.vehicle.intCD) if contentID == R.views.lobby.tooltips.VehPostProgressionEntryPointTooltip() else super(ModulesSubPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def initialize(self, vhCtx, *args, **kwargs):
        super(ModulesSubPresenter, self).initialize(vhCtx, *args, **kwargs)
        self.updateResearchItems()
        self.__updateFieldModification()
        updateViewedItems(vehicle=self.vehicle)

    def finalize(self):
        super(ModulesSubPresenter, self).finalize()
        if self._data is not None:
            self._data.clear(full=True)
            self._data = None
        self._eliteWatchedList = None
        return

    def invalidateCredits(self):
        self.__updateResearchItemsMap(self._data.invalidateCredits())

    def invalidateGold(self):
        self.__updateResearchItemsMap(self._data.invalidateGold())
        self.invalidateFreeXP()
        self.invalidateCredits()

    def invalidateFreeXP(self):
        self.__updateResearchItemsMap(self._data.invalidateFreeXP())

    def invalidateElites(self, elites):
        elitesResult = self._data.invalidateElites(elites)
        self.__updateResearchItemsMap(elitesResult)

    def invalidateVTypeXP(self, _):
        vTypeXPResult = self._data.invalidateVTypeXP()
        self.__updateResearchItemsMap(vTypeXPResult)

    def invalidateUnlocks(self, unlocks):
        _, unlocked, _ = self._data.invalidateUnlocks(unlocks)
        if unlocked:
            self.redraw()

    def invalidateInventory(self, _):
        installedResult = self._data.invalidateInstalled()
        for installedItem in installedResult:
            if NODE_STATE.isInstalled(installedItem[1]):
                g_currentPreviewVehicle.selectVehicle(self.vehicle.intCD, vehicleStrCD=self.vehicle.strCD, outfit=self.vehicle.getOutfit(SeasonType.SUMMER))

        self.redraw()

    def invalidateBlueprints(self, blueprints):
        if blueprints:
            self.redraw()

    def invalidateBlueprintMode(self, _):
        pass

    def invalidatePrbState(self):
        self._data.invalidatePrbState()
        self.redraw()

    def invalidateDiscounts(self, data):
        if self._data.invalidateDiscounts(data):
            self._data.invalidateCredits()
            self._data.invalidateGold()
            self.redraw()

    def invalidateVehLocks(self, locks):
        if self._data.invalidateLocks(locks):
            self.redraw()

    def invalidateWalletStatus(self, _):
        self.invalidateFreeXP()

    def invalidateRent(self, vehicles):
        if self._data.getRootCD() in vehicles:
            self.redraw()

    def invalidateRestore(self, vehicles):
        if self._data.getRootCD() in vehicles:
            self.redraw()

    def invalidateVehCompare(self):
        pass

    def invalidateVehicleCollectorState(self):
        pass

    def invalidateVehPostProgression(self):
        self.redraw()

    def _subscribe(self):
        super(ModulesSubPresenter, self)._subscribe()
        self.__listener = TTListenerDecorator()
        self.__listener.startListen(self)

    def _unsubscribe(self):
        if self.__listener is not None:
            self.__listener.stopListen()
            self.__listener = None
        super(ModulesSubPresenter, self)._unsubscribe()
        return

    def _getEvents(self):
        return super(ModulesSubPresenter, self)._getEvents() + ((self.viewModel.fieldModificationModel.onVehiclePostProgression, self.__onPostProgression),
         (self.viewModel.onVehicleChange, self.__changeVehicle),
         (self.viewModel.onInstallItem, self.__installItem),
         (self.viewModel.onUnlockItem, self.__unlockItem),
         (self.viewModel.onBuyAndInstallItem, self.__buyAndInstallItem),
         (self.viewModel.onSellItem, self.__sellItem),
         (self._itemsCache.onSyncCompleted, self._onSyncCompleted))

    def _getCallbacks(self):
        callbacksTuple = super(ModulesSubPresenter, self)._getCallbacks()
        return callbacksTuple + (('stats.eliteVehicles', self.__onVehicleBecomeElite), ('stats.vehTypeXP', self.__updateVehTypeXP), ('stats.unlocks', self.__onVehicleBecomeUnlock))

    def _getListeners(self):
        return super(ModulesSubPresenter, self)._getListeners() + ((events.CloseWindowEvent.BUY_VEHICLE_VIEW_CLOSED, self.__onBuyVehicleWindowClosed), (events.CloseWindowEvent.ELITE_WINDOW_CLOSED, self.__onEliteWindowClosed))

    def __onEliteWindowClosed(self, _):
        self.__updateFieldModification()

    def __onBuyVehicleWindowClosed(self, event):
        if not event.isAgree:
            self.__updateFieldModification()

    def __onPostProgression(self):
        if not self.isUnlockShowed:
            self._eliteWatchedList.add(self.vehicle.intCD)
            AccountSettings.setSettings(BECOME_ELITE_VEHICLES_WATCHED, self._eliteWatchedList)
            self.__updateFieldModification()
        showVehPostProgressionView(self.vehicle.intCD)

    def __updateFieldModification(self):
        postProgression = self.viewModel.fieldModificationModel
        state = postProgression.HIDDEN
        if self.vehicle.isPostProgressionExists and not self.vehicle.postProgression.isVehSkillTree():
            state = postProgression.UNLOCKED if self.vehicle.postProgressionAvailability(unlockOnly=True) else postProgression.LOCKED
        self._eliteWatchedList = AccountSettings.getSettings(BECOME_ELITE_VEHICLES_WATCHED)
        counter = 1 if needToShowCounter(self.vehicle) or state == postProgression.UNLOCKED and not self.isUnlockShowed else 0
        postProgression.setState(state)
        postProgression.setCounter(counter)

    def __updateVehTypeXP(self, diff):
        vehicleCDs = self._data.getVehicleCDs()
        if any((key in vehicleCDs for key in diff.keys())):
            self.redraw()

    def __fillResearchModels(self, data, researchItemsModel, researchItemsMap):
        researchItemsModel.clear()
        for item in data:
            researchItemModel = self.__fillResearchItemModel(item)
            researchItemDisplayModel = self.__fillResearchItemDisplayModel(item)
            researchItemsMap.set(researchItemModel.getId(), researchItemModel)
            researchItemsModel.addViewModel(researchItemDisplayModel)

        researchItemsModel.invalidate()

    def __fillResearchItemModel(self, item):
        researchItemModel = ResearchItemModel()
        displayInfo = item['displayInfo']
        researchItemModel.setId(item['id'])
        researchItemModel.setImage(item['image'])
        researchItemModel.setRenderer(displayInfo['renderer'])
        researchItemModel.setUserName(item['userName'])
        researchItemModel.setLevel(item['level'])
        researchItemModel.setState(item['state'])
        researchItemModel.setRequiredXp(item['requiredXp'])
        researchItemModel.setIsDiscountedXp(item['isDiscountedXp'])
        researchItemModel.setPrimaryClass(item['primaryClass']['name'])
        researchItemModel.setEarnedXp(item['earnedXp'])
        researchItemModel.setPriceAmount(item['priceAmount'])
        researchItemModel.setPriceCurrency(item['priceCurrency'])
        researchItemModel.setIsDiscountedPrice(item['isDiscountedPrice'])
        researchItemModel.setIsResearched(item['isResearched'])
        researchItemModel.setHasEnoughXP(item['hasEnoughXP'])
        researchItemModel.setHasEnoughCurrency(item['hasEnoughCurrency'])
        researchItemModel.setIsElite(item['isElite'])
        researchItemModel.setAutoUnlocked(item['autoUnlocked'])
        researchItemModel.setIsInstalled(item['isInstalled'])
        researchItemModel.setIsDisabled(item['isDisabled'])
        researchItemModel.setIsInInventory(item['isInInventory'])
        fillIntsArray(displayInfo['path'], researchItemModel.getPath())
        mechanics = researchItemModel.getMechanics()
        mechanics.clear()
        for mechanicName in item.get('mechanics'):
            mechanicModel = VehicleMechanicModel()
            mechanicModel.setName(mechanicName)
            mechanics.addViewModel(mechanicModel)

        mechanics.invalidate()
        if displayInfo['renderer'] == 'item':
            urgentIds = [ id for id, _ in self._data.getUrgentIds(item['id']) ]
            fillIntsArray(urgentIds, researchItemModel.getUrgentIds())
        return researchItemModel

    def __fillResearchItemDisplayModel(self, item):
        researchItemDisplayModel = ResearchItemDisplayModel()
        displayInfo = item['displayInfo']
        researchItemDisplayModel.setId(item['id'])
        researchItemDisplayModel.setLevel(displayInfo['level'])
        researchItemDisplayModel.setRenderer(displayInfo['renderer'])
        fillIntsArray(displayInfo['path'], researchItemDisplayModel.getPath())
        return researchItemDisplayModel

    def __getNodesToUpdate(self, invalidationResult):
        return {r[0] for r in invalidationResult}

    def __updateResearchItemsMap(self, invalidationResult):
        nodesToUpdate = self.__getNodesToUpdate(invalidationResult)
        if not nodesToUpdate:
            return
        else:
            with self.viewModel.transaction() as model:
                researchItems = model.getResearchItems()
                for intCD in nodesToUpdate:
                    item = self._data.invalidateItem(intCD)
                    if item is not None:
                        researchItems.set(intCD, self.__fillResearchItemModel(item))

            return

    @args2params(int)
    def __changeVehicle(self, itemCD):
        showVehicleHubModules(itemCD)

    def __onVehicleBecomeElite(self, elite):
        if self.vehicle.intCD in elite:
            self.invalidateElites(elite)
            self.__updateFieldModification()

    def __onVehicleBecomeUnlock(self, unlocks):
        if self.vehicle.intCD in unlocks:
            self.__updateFieldModification()

    def _onSyncCompleted(self, _, diff):
        if self.vehicle.intCD in diff.get(GUI_ITEM_TYPE.VEH_POST_PROGRESSION, {}):
            self.__updateFieldModification()

    @args2params(int)
    def __buyAndInstallItem(self, itemCD):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_AND_SELL_ITEM, itemCD, self._data.getRootCD(), skipConfirm=False)

    @args2params(int)
    def __unlockItem(self, itemCD):
        node = self._data.getNodeByItemCD(itemCD)
        unlockProps = node.getUnlockProps() if node is not None else None
        if unlockProps is not None:
            ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, itemCD, unlockProps, skipConfirm=False)
        return

    @args2params(int)
    def __installItem(self, itemCD):
        ItemsActionsFactory.doAction(ItemsActionsFactory.INSTALL_ITEM, itemCD, self._data.getRootCD())

    @args2params(int)
    def __sellItem(self, itemCD):
        ItemsActionsFactory.doAction(ItemsActionsFactory.SELL_ITEM, itemCD)
