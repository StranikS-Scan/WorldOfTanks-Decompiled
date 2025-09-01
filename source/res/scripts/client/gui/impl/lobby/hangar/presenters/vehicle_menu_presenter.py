# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_menu_presenter.py
from __future__ import absolute_import
import json
import logging
from collections import namedtuple
from functools import partial
import typing
from future.utils import iteritems
import BigWorld
import adisp
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CREW_BOOKS_VIEWED
from frameworks.wulf.view.array import fillStringsArray
from PlayerEvents import g_playerEvents
from armor_inspector_common.schemas import armorInspectorConfigSchema
from gui import SystemMessages
from gui.easy_tank_equip.easy_tank_equip_helpers import isAvailableForVehicle
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from gui.impl.dialogs.dialogs import showRetrainMassiveDialog
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel
from gui.impl.lobby.tank_setup.dialogs.main_content.main_contents import NeedRepairMainContent
from gui.impl.lobby.tank_setup.dialogs.need_repair import NeedRepair
from gui.impl.pub.view_component import ViewComponent
from gui.shared.event_dispatcher import showQuickTraining, showVehicleHubOverview, showVehicleHubModules, showVehicleHubArmor, showChangeVehicleNationDialog, showEasyTankEquipScreen, showVehPostProgressionView, showVehicleHubVehSkillTree
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getLowEfficiencyTankmenIDs
from gui.shared.gui_items.items_actions import factory
from gui.shared.gui_items.items_actions.actions import VehicleRepairAction
from gui.shared.gui_items.processors.tankman import TankmanReturn, TankmanAutoReturn
from gui.shared.gui_items.processors.vehicle import VehicleAutoReturnProcessor
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from gui.shared.utils.module_upd_available_helper import getResearchInfo
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.veh_post_progression.helpers import storeLastSeenStep, needToShowCounter
from gui.veh_post_progression.models.ext_money import ExtendedMoney
from helpers import dependency
from items.components.c11n_constants import ItemTags
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IVehicleComparisonBasket, IVehiclePostProgressionController, IEasyTankEquipController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IPlatoonController
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared import events, EVENT_BUS_SCOPE
if typing.TYPE_CHECKING:
    from gui.shared.utils.requesters import RequestCriteria
_logger = logging.getLogger(__name__)
_ItemInfo = namedtuple('itemInfo', ['state', 'counter', 'handler'])
_ItemStateWithReason = namedtuple('itemStateWithReason', ['state', 'reason'])

def _handleFunctionCallForCurrentVehicle(func):
    func(g_currentVehicle.item.intCD)


class VehicleMenuPresenter(ViewComponent[VehicleMenuModel], IPrbListener):
    __customizationService = dependency.descriptor(ICustomizationService)
    __easyTankEquipCtrl = dependency.descriptor(IEasyTankEquipController)
    __postProgressionCtrl = dependency.descriptor(IVehiclePostProgressionController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __cmpBasket = dependency.descriptor(IVehicleComparisonBasket)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(VehicleMenuPresenter, self).__init__(model=VehicleMenuModel)
        self._menuItems = {}
        self.__hasInventoryTankman = False
        self.__hasTankman = False

    @property
    def viewModel(self):
        return super(VehicleMenuPresenter, self).getViewModel()

    def _createMenuItems(self):
        return {VehicleMenuModel.CUSTOMIZATION: _ItemInfo(partial(self.__getStylesState, requestCriteria=~REQ_CRITERIA.CUSTOMIZATION.HAS_TAGS([ItemTags.IS_3D])), 0, self.__customizationService.showCustomization),
         VehicleMenuModel.CREW_AUTO_RETURN: _ItemInfo(self.__setCrewAutoReturnState, 0, self.__handleAutoReturnToggleSwitch),
         VehicleMenuModel.CREW_RETRAIN: _ItemInfo(self.__getCrewRetrainState, 0, self.__handleCrewRetrain),
         VehicleMenuModel.QUICK_TRAINING: _ItemInfo(self.__getQuickTrainingState, self.__getCrewBooksCount, showQuickTraining),
         VehicleMenuModel.CREW_OUT: _ItemInfo(self.__getCrewOutState, 0, self.__handleCrewOut),
         VehicleMenuModel.CREW_BACK: _ItemInfo(self.__getCrewBackState, 0, self.__handleCrewBack),
         VehicleMenuModel.EASY_EQUIP: _ItemInfo(self.__getEasyEquipState, 0, showEasyTankEquipScreen),
         VehicleMenuModel.NATION_CHANGE: _ItemInfo(self.__getNationChangeState, 0, partial(_handleFunctionCallForCurrentVehicle, showChangeVehicleNationDialog)),
         VehicleMenuModel.ARMOR_INSPECTOR: _ItemInfo(self.__getArmorState, 0, partial(_handleFunctionCallForCurrentVehicle, showVehicleHubArmor)),
         VehicleMenuModel.FIELD_MODIFICATION: _ItemInfo(self.__getProgressionState, 0, partial(_handleFunctionCallForCurrentVehicle, showVehPostProgressionView)),
         VehicleMenuModel.RESEARCH: _ItemInfo(self.__getResearchState, self.__getAvailableModulesForResearchCount, partial(_handleFunctionCallForCurrentVehicle, showVehicleHubModules)),
         VehicleMenuModel.ABOUT_VEHICLE: _ItemInfo(lambda : VehicleMenuModel.ENABLED, 0, partial(_handleFunctionCallForCurrentVehicle, showVehicleHubOverview)),
         VehicleMenuModel.COMPARE: _ItemInfo(self.__getCompareState, 0, self.__handleCompare),
         VehicleMenuModel.REPAIRS: _ItemInfo(self.__getRepairState, 0, self.__handleRepair),
         VehicleMenuModel.VEH_SKILL_TREE: _ItemInfo(partial(self.__getProgressionState, isVehSkillTree=True), 0, partial(_handleFunctionCallForCurrentVehicle, showVehicleHubVehSkillTree))}

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self.__updateModel),
         (AccountSettings.onSettingsChanging, self.__onAccountSettingsChanging),
         (self.viewModel.onNavigate, self.__onNavigate),
         (self.__easyTankEquipCtrl.onUpdated, self.__onSettingsChange),
         (self.__itemsCache.onSyncCompleted, self.__onSyncCompleted),
         (self.__platoonCtrl.onMembersUpdate, self.__onPlatoonMembersUpdate),
         (self.__cmpBasket.onChange, self.__onCmpBasketChange),
         (self.__cmpBasket.onSwitchChange, self.__onVehCmpBasketStateChanged),
         (g_playerEvents.onConfigModelUpdated, self.__configChangeHandler))

    def _getListeners(self):
        return ((events.PrebattleEvent.SWITCHED, self.__onPrbEntitySwitched, EVENT_BUS_SCOPE.LOBBY),)

    def _onLoading(self, *args, **kwargs):
        super(VehicleMenuPresenter, self)._onLoading()
        self._menuItems = self._createMenuItems()
        for key, value in iteritems(self._menuItems):
            if not callable(value.handler):
                _logger.error('Vehicle menu item %s call function %r is not callable', key, value)

        self.__updateModel()

    def _finalize(self):
        super(VehicleMenuPresenter, self)._finalize()
        self._menuItems = {}
        self.__styleCriteria = None
        return

    def __onPlatoonMembersUpdate(self, *_):
        self.__updateModel()

    def __onPrbEntitySwitched(self, _):
        self.__updateModel()

    def __onSyncCompleted(self, reason, diff):
        if reason != CACHE_SYNC_REASON.CLIENT_UPDATE:
            return
        if diff.get(GUI_ITEM_TYPE.CREW_BOOKS, {}):
            self.__updateMenuItemModel(VehicleMenuModel.QUICK_TRAINING)

    def __onAccountSettingsChanging(self, key, _):
        if key == CREW_BOOKS_VIEWED:
            self.__updateMenuItemModel(VehicleMenuModel.QUICK_TRAINING)

    def __onSettingsChange(self):
        self.__updateMenuItemModel(VehicleMenuModel.EASY_EQUIP)

    def __updateModel(self):
        self.__hasInventoryTankman = bool(self.__itemsCache.items.getInventoryTankmen(limit=1))
        self.__hasTankman = bool(self.__itemsCache.items.getInventoryTankmen(REQ_CRITERIA.TANKMAN.IS_LOCK_CREW(isLocked=False), limit=1))
        with self.viewModel.transaction() as model:
            menuItems = model.getMenuItems()
            menuItems.clear()
            researchItems = model.getResearchItems()
            researchItems.clear()
            for menuItemName in self._menuItems:
                self.__setItem(menuItemName, menuItems)
                if menuItemName == VehicleMenuModel.RESEARCH and self.__getMenuItemState(menuItemName) == VehicleMenuModel.WARNING:
                    unviewedModules = self.__getUnviewedResearchModules()
                    if unviewedModules:
                        fillStringsArray(unviewedModules, researchItems)

            researchItems.invalidate()

    def __updateMenuItemModel(self, menuItemName):
        menuItems = self.viewModel.getMenuItems()
        self.__setItem(menuItemName, menuItems)

    def __setItem(self, name, menuItems):
        data = {'state': self.__getMenuItemState(name),
         'counter': 0}
        if g_currentVehicle.isPresent():
            data['counter'] = self._menuItems[name].counter if isinstance(self._menuItems[name].counter, int) else self._menuItems[name].counter()
            menuItemStateValue = self._menuItems[name].state()
            if isinstance(menuItemStateValue, tuple) and hasattr(menuItemStateValue, '_fields'):
                data['stateReason'] = menuItemStateValue.reason
        menuItems.set(name, json.dumps(data))

    def __getMenuItemState(self, name):
        if not g_currentVehicle.isPresent():
            return VehicleMenuModel.DISABLED
        menuItemStateValue = self._menuItems[name].state()
        return menuItemStateValue.state if isinstance(menuItemStateValue, tuple) and hasattr(menuItemStateValue, '_fields') else menuItemStateValue

    def __getUnviewedResearchModules(self):
        researchInfo = getResearchInfo(vehicle=g_currentVehicle.item)
        if not researchInfo:
            return None
        else:
            researchItems = researchInfo.getUnviewedItems()
            if not researchItems:
                return []
            modules = []
            for item in researchItems:
                module = self.__itemsCache.items.getItemByCD(item)
                if module.itemTypeName == 'vehicle':
                    continue
                if module.itemTypeName == 'vehicleChassis' and module.isWheeledChassis():
                    modules.append('vehicleWheels')
                modules.append(module.itemTypeName)

            return modules

    def __isVehicleUnavailable(self):
        return g_currentVehicle.item.isInBattle or g_currentVehicle.item.isInPrebattle

    def __getCrewBooksCount(self):
        return crewBooksViewedCache().newCrewBooksAmount if g_currentVehicle is not None else 0

    def __getAvailableModulesForResearchCount(self):
        if g_currentVehicle is not None:
            unviewedModules = self.__getUnviewedResearchModules()
            if unviewedModules:
                return len(unviewedModules)
            return 0
        else:
            return

    def __getCrewBackState(self):
        if not self.__hasTankman:
            return VehicleMenuModel.DISABLED
        elif not g_currentVehicle.isPresent() or self.__isVehicleUnavailable():
            return VehicleMenuModel.DISABLED
        vehicle = g_currentVehicle.item
        if vehicle.isCrewLocked:
            return VehicleMenuModel.DISABLED
        crew = vehicle.crew
        lastCrewIDs = vehicle.lastCrew
        if lastCrewIDs is None:
            return _ItemStateWithReason(VehicleMenuModel.DISABLED, VehicleMenuModel.BATTLE_NEEDED)
        freeBerths = self.__itemsCache.items.freeTankmenBerthsCount()
        tankmenToBarracksCount = 0
        demobilizedMembersCounter = 0
        isCrewAlreadyInCurrentVehicle = True
        hasReturnableTankmen = False
        for _, tankman in crew:
            if tankman is not None:
                tankmenToBarracksCount += 1

        for lastTankmenInvID in lastCrewIDs:
            actualLastTankman = self.__itemsCache.items.getTankman(lastTankmenInvID)
            if actualLastTankman is None or actualLastTankman.isDismissed:
                demobilizedMembersCounter += 1
                isCrewAlreadyInCurrentVehicle = False
                continue
            if actualLastTankman.isInTank:
                lastTankmanVehicle = self.__itemsCache.items.getVehicle(actualLastTankman.vehicleInvID)
                if lastTankmanVehicle:
                    if lastTankmanVehicle.isLocked:
                        return VehicleMenuModel.DISABLED
                    if lastTankmanVehicle.invID != vehicle.invID:
                        isCrewAlreadyInCurrentVehicle = False
                        hasReturnableTankmen = True
                    else:
                        tankmenToBarracksCount -= 1
            hasReturnableTankmen = True
            isCrewAlreadyInCurrentVehicle = False
            freeBerths += 1

        if not hasReturnableTankmen:
            return VehicleMenuModel.DISABLED
        elif tankmenToBarracksCount > 0 and tankmenToBarracksCount > freeBerths:
            return VehicleMenuModel.DISABLED
        elif demobilizedMembersCounter > 0 and demobilizedMembersCounter == len(lastCrewIDs):
            return VehicleMenuModel.DISABLED
        elif isCrewAlreadyInCurrentVehicle:
            return VehicleMenuModel.DISABLED
        else:
            return _ItemStateWithReason(VehicleMenuModel.ENABLED, VehicleMenuModel.CREW_MEMBERS_RETIRED) if 0 < demobilizedMembersCounter < len(lastCrewIDs) else VehicleMenuModel.ENABLED

    def __onCmpBasketChange(self, *_):
        self.__updateMenuItemModel(VehicleMenuModel.COMPARE)

    def __onVehCmpBasketStateChanged(self):
        self.__updateMenuItemModel(VehicleMenuModel.COMPARE)

    def __getStylesState(self, requestCriteria):
        if self.__isVehicleUnavailable() or g_currentVehicle.isBroken() or not self.__lobbyContext.getServerSettings().isCustomizationEnabled():
            return VehicleMenuModel.DISABLED
        if g_currentVehicle.item.isOutfitLocked:
            return VehicleMenuModel.DISABLED
        if g_currentVehicle.item.isProgressionDecalsOnly:
            return VehicleMenuModel.ENABLED
        criteria = requestCriteria | REQ_CRITERIA.CUSTOMIZATION.FOR_VEHICLE(g_currentVehicle.item)
        hasStyle = bool(self.__itemsCache.items.getItems(GUI_ITEM_TYPE.STYLE, criteria, limit=1))
        return VehicleMenuModel.ENABLED if g_currentVehicle.isCustomizationEnabled and hasStyle else VehicleMenuModel.DISABLED

    def __getCrewRetrainState(self):
        if not self.__hasInventoryTankman:
            return VehicleMenuModel.DISABLED
        if not g_currentVehicle.isPresent():
            return VehicleMenuModel.DISABLED
        if g_currentVehicle.item.isCrewLocked:
            return VehicleMenuModel.DISABLED
        return VehicleMenuModel.DISABLED if not getLowEfficiencyTankmenIDs(g_currentVehicle.item) or not g_currentVehicle.hasCrew() or self.__isVehicleUnavailable() else VehicleMenuModel.ENABLED

    def __getCrewOutState(self):
        if not self.__hasInventoryTankman:
            return VehicleMenuModel.DISABLED
        if not g_currentVehicle.isPresent():
            return VehicleMenuModel.DISABLED
        if g_currentVehicle.item.isCrewLocked:
            return VehicleMenuModel.DISABLED
        return VehicleMenuModel.DISABLED if not g_currentVehicle.hasCrew() or self.__isVehicleUnavailable() else VehicleMenuModel.ENABLED

    def __getQuickTrainingState(self):
        if not self.__hasInventoryTankman:
            return VehicleMenuModel.DISABLED
        if not g_currentVehicle.isPresent():
            return VehicleMenuModel.DISABLED
        if not g_currentVehicle.hasCrew() or self.__isVehicleUnavailable():
            return VehicleMenuModel.DISABLED
        return VehicleMenuModel.WARNING if crewBooksViewedCache().haveNewCrewBooks() else VehicleMenuModel.ENABLED

    def __getCompareState(self):
        cmpBasket = self.__cmpBasket
        readyToAdd = cmpBasket.isReadyToAdd(g_currentVehicle.item)
        return VehicleMenuModel.DISABLED if not cmpBasket.isEnabled() or not readyToAdd else VehicleMenuModel.ENABLED

    def __getRepairState(self):
        if g_currentVehicle.isBroken():
            return VehicleMenuModel.CRITICAL
        return VehicleMenuModel.DISABLED if g_currentVehicle.isInBattle() or g_currentVehicle.isLocked() else VehicleMenuModel.ENABLED

    def __getResearchState(self):
        unviewedModules = self.__getUnviewedResearchModules()
        return VehicleMenuModel.WARNING if unviewedModules else VehicleMenuModel.ENABLED

    def __setCrewAutoReturnState(self):
        if not self.__hasTankman:
            return VehicleMenuModel.DISABLED
        elif not g_currentVehicle.isPresent():
            return VehicleMenuModel.UNAVAILABLE
        elif g_currentVehicle.item.isCrewLocked:
            return VehicleMenuModel.UNAVAILABLE
        elif g_currentVehicle.item.lastCrew is None:
            return _ItemStateWithReason(VehicleMenuModel.UNAVAILABLE, VehicleMenuModel.BATTLE_NEEDED)
        else:
            return VehicleMenuModel.ENABLED if g_currentVehicle.item.isAutoReturn else VehicleMenuModel.DISABLED

    def __getEasyEquipState(self):
        if not self.__easyTankEquipCtrl.config.enabled:
            return VehicleMenuModel.UNAVAILABLE
        if not g_currentVehicle.isPresent() or self.__isVehicleUnavailable() or g_currentVehicle.item.isOnlyForEventBattles or g_currentVehicle.isUnsuitableToQueue():
            return VehicleMenuModel.DISABLED
        if g_currentVehicle.isPresent() and isAvailableForVehicle(g_currentVehicle.item):
            isAmmoNotFull = g_currentVehicle.item.isAmmoFull
            isHighlight = not g_currentVehicle.item.isCrewFull or not isAmmoNotFull or not g_currentVehicle.item.consumables.installed.getItems()
            if isHighlight:
                return VehicleMenuModel.WARNING
            return VehicleMenuModel.ENABLED
        return VehicleMenuModel.DISABLED

    def __getNationChangeState(self):
        if g_currentVehicle.isPresent() and g_currentVehicle.item.isNationChangeAvailable:
            return VehicleMenuModel.ENABLED
        return VehicleMenuModel.DISABLED if g_currentVehicle.item.hasNationGroup else VehicleMenuModel.UNAVAILABLE

    def __getProgressionState(self, isVehSkillTree=False):
        if g_currentVehicle.item.postProgression.isVehSkillTree() != isVehSkillTree:
            return VehicleMenuModel.UNAVAILABLE
        elif not self.__postProgressionCtrl.isExistsFor(g_currentVehicle.item.descriptor.type):
            return VehicleMenuModel.UNAVAILABLE
        else:
            return VehicleMenuModel.WARNING if g_currentVehicle.item.postProgression.getFirstPurchasableStep(ExtendedMoney(xp=g_currentVehicle.item.xp)) is not None and (isVehSkillTree or g_currentVehicle.item.isElite) and needToShowCounter(g_currentVehicle.item) else VehicleMenuModel.ENABLED

    def __getArmorState(self):
        vehicle = g_currentVehicle.item
        configModel = armorInspectorConfigSchema.getModel()
        return VehicleMenuModel.DISABLED if vehicle is None or not configModel.enabled or configModel.isDisabledForVehicle(vehicle.name) else VehicleMenuModel.ENABLED

    def __handleCrewOut(self):
        vehicle = g_currentVehicle.item
        actions = [ (factory.UNLOAD_TANKMAN, vehicle.invID, slotIdx) for slotIdx, tmanInvId in vehicle.crew if tmanInvId is not None ]
        BigWorld.player().doActions(actions)
        return

    @adisp.adisp_process
    def __handleCrewBack(self):
        result = yield TankmanReturn(g_currentVehicle.item).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __handleCrewRetrain(self):
        tankmanIDs = [ tman.invID for _, tman in g_currentVehicle.item.crew if tman is not None and not tman.isMaxCurrentVehicleSkillsEfficiency ]
        vehicleCD = g_currentVehicle.item.intCD
        showRetrainMassiveDialog(tankmanIDs, vehicleCD)
        return

    def __handleCompare(self):
        self.__cmpBasket.addVehicle(g_currentVehicle.item.intCD)
        if self.__cmpBasket.isFull():
            self.__setItem(VehicleMenuModel.COMPARE, self.viewModel.getMenuItems())

    @adisp.adisp_process
    def __handleRepair(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            yield VehicleRepairAction(vehicle, NeedRepair, NeedRepairMainContent).doAction()

    @decorators.adisp_process('updating')
    def __handleAutoReturnToggleSwitch(self):
        if not g_currentVehicle.isPresent():
            return
        result = yield VehicleAutoReturnProcessor(g_currentVehicle.item, not g_currentVehicle.item.isAutoReturn).request()
        if result.success and g_currentVehicle.item.isAutoReturn:
            result = yield TankmanAutoReturn(g_currentVehicle.item).request()
        if not result.success:
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
        self.__updateMenuItemModel(VehicleMenuModel.CREW_AUTO_RETURN)

    def __onNavigate(self, args):
        name = args.get('name')
        if name == VehicleMenuModel.FIELD_MODIFICATION:
            self.__updateLastSeenModification()
        self._menuItems[name].handler()

    def __configChangeHandler(self, gpKey):
        if gpKey == armorInspectorConfigSchema.gpKey:
            self.__updateModel()

    def __updateLastSeenModification(self):
        purchasableStep = g_currentVehicle.item.postProgression.getFirstPurchasableStep(ExtendedMoney(xp=g_currentVehicle.item.xp))
        if purchasableStep is not None:
            storeLastSeenStep(g_currentVehicle.intCD, purchasableStep.stepID)
        return
