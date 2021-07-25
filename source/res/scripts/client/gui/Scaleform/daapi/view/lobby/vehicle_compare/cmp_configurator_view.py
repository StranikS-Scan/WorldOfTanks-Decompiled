# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_configurator_view.py
import typing
from adisp import process
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover import FITTING_MODULES
from gui.Scaleform.daapi.view.lobby.shared.fitting_slot_vo import FittingSlotVO
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_base import VehicleCompareConfiguratorBaseView
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_parameters import VehicleCompareParameters
from gui.Scaleform.daapi.view.meta.VehicleCompareConfiguratorMainMeta import VehicleCompareConfiguratorMainMeta
from gui.Scaleform.daapi.view.meta.VehicleCompareConfiguratorViewMeta import VehicleCompareConfiguratorViewMeta
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.VEHICLE_COMPARE_CONSTANTS import VEHICLE_COMPARE_CONSTANTS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.game_control.veh_comparison_basket import PerksData
from gui.impl.lobby.vehicle_compare.interactors import CompareInteractingItem
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE, vehicle_adjusters, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.items_actions.actions import processMsg
from gui.shared.gui_items.processors.module import ModuleProcessor
from helpers import dependency
from helpers.i18n import makeString as _ms
from shared_utils import findFirst
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple, List
    from gui.impl.lobby.vehicle_compare.detachment import CompareDetachmentView
    from gui.game_control.veh_comparison_basket import _VehCompareData
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_inject import VehicleCompareConfiguratorInject
VEHICLE_FITTING_SLOTS = FITTING_MODULES
_EMPTY_ID = -1

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getFittingSlotsData(vehicle, slotsRange, voClass=None, itemsCache=None):
    devices = []
    voClass = voClass or FittingSlotVO
    modulesData = _getVehicleModulesBySlotType(vehicle)
    for slotType in slotsRange:
        devices.append(voClass(modulesData[slotType], vehicle, slotType, tooltipType=TOOLTIPS_CONSTANTS.HANGAR_MODULE))

    return devices


def _getVehicleModulesBySlotType(vehicle):
    modules = {GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.CHASSIS]: (vehicle.chassis,),
     GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.TURRET]: (vehicle.turret,),
     GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.GUN]: (vehicle.gun,),
     GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.ENGINE]: (vehicle.engine,),
     GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.RADIO]: (vehicle.radio,)}
    return modules


def _getSlotDataIndexes(slots):
    index = 0
    indexes = []
    for _ in slots:
        indexes.append((index,))
        index += 1

    return indexes


_SLOT_DATA_INDEXES = _getSlotDataIndexes(VEHICLE_FITTING_SLOTS)

class _CmpOptDeviceRemover(ModuleProcessor):

    def __init__(self, vehicle, item, slotIndex, plugs=tuple()):
        super(_CmpOptDeviceRemover, self).__init__(item, 'remove', plugs)
        self.__vehicle = vehicle
        self.__slotIndex = slotIndex

    def _request(self, callback):
        removed, reason = vehicle_adjusters.removeOptionalDevice(self.__vehicle, self.__slotIndex)
        if removed:
            super(_CmpOptDeviceRemover, self)._request(callback)
        else:
            callback(self._errorHandler(0, reason))

    def _errorHandler(self, code, errStr='', ctx=None):
        if errStr == 'too heavy':
            errStr = 'error_too_heavy'
        return super(_CmpOptDeviceRemover, self)._errorHandler(code, errStr, ctx)

    def _getMsgCtx(self):
        return {'name': self.item.userName,
         'kind': self.item.userType,
         'money': 0}


class _ConfigFittingSlotVO(FittingSlotVO):

    def __init__(self, modulesData, vehicle, moduleType, tooltipType=None, isDisabledTooltip=False):
        super(_ConfigFittingSlotVO, self).__init__(modulesData, vehicle, moduleType, tooltipType, isDisabledTooltip)
        slotEmpty = self['id'] == -1
        self['showRemoveBtn'] = not slotEmpty
        self['tooltipType'] = TOOLTIPS_CONSTANTS.COMPARE_MODULE


class VehicleCompareConfiguratorView(LobbySubView, VehicleCompareConfiguratorViewMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        self.__parametersView = None
        self.__configuratorInject = None
        self.__detachmentView = None
        super(VehicleCompareConfiguratorView, self).__init__(ctx)
        self.__slotsVoData = [None] * (_SLOT_DATA_INDEXES[-1][-1] + 1)
        return

    def onCloseView(self):
        self._container.closeView()

    def onCamouflageUpdated(self):
        self.__configuratorInject.updateCamouflage()
        self.__updateParametersView()

    def onOptDeviceUpdated(self):
        self.__configuratorInject.update()
        self.__updateParametersView()

    def onEquipmentUpdated(self):
        self.__configuratorInject.update()
        self.__updateParametersView()

    def onBattleBoosterUpdated(self):
        self.__configuratorInject.update()
        self.__updateParametersView()

    def onModulesUpdated(self):
        self.__updateSlotsData(FITTING_MODULES)
        self.__updateParametersView()
        self.as_setTopModulesSelectedS(self._container.isTopModulesSelected())

    def onResetToDefault(self):
        self.__parametersView.setVehicle(self._container.getCurrentVehicle())
        self.__updateSlotsData(VEHICLE_FITTING_SLOTS)
        self.as_setTopModulesSelectedS(self._container.isTopModulesSelected())
        self.__configuratorInject.update()

    def onShellsUpdated(self, updateShells=False, selectedIndex=-1):
        if selectedIndex != -1:
            self.__updateParametersView()
        self.__updateShellSlots()
        self.__updateControlBtns()

    def onPerksUpdated(self):
        perks = self._container.perks
        self.__detachmentView.setPerks(perks)
        self.__updateParametersView()

    def resetConfig(self):
        self._container.resetToDefault()

    def applyConfig(self):
        self._container.applyNewParameters()
        self.onCloseView()

    def installDevice(self, newId, slotType, slotIndex):
        if slotType == cmp_helpers.OPTIONAL_DEVICE_TYPE_NAME:
            self._container.installOptionalDevice(newId, slotIndex)
        elif slotType == cmp_helpers.EQUIPMENT_TYPE_NAME:
            self._container.installEquipment(newId, slotIndex)
        else:
            LOG_ERROR('{} installDevice. Unsupported slotType: {}'.format(self, slotType))

    def removeDevice(self, slotType, slotIndex):
        if slotType == cmp_helpers.OPTIONAL_DEVICE_TYPE_NAME:
            self._container.removeOptionalDevice(slotIndex)
        elif slotType == cmp_helpers.EQUIPMENT_TYPE_NAME:
            self._container.removeEquipment(slotIndex)
        elif slotType == cmp_helpers.BATTLE_BOOSTER_TYPE_NAME:
            self._container.removeBattleBooster()
        else:
            LOG_ERROR('{} removeDevice. Unsupported slotType: {}'.format(self, slotType))

    def toggleTopModules(self, value):
        self._container.selectTopModules(value)

    def showModules(self):
        self._container.as_showViewS(VEHICLE_COMPARE_CONSTANTS.VEHICLE_MODULES_VIEW)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(VehicleCompareConfiguratorView, self)._onRegisterFlashComponent(viewPy, alias)
        if isinstance(viewPy, VehicleCompareParameters):
            self.__parametersView = viewPy
        elif alias == VEHICLE_COMPARE_CONSTANTS.VEHICLE_CONFIGURATOR_EQUIPMENT_WIDGET:
            self.__configuratorInject = viewPy
        elif alias == VEHICLE_COMPARE_CONSTANTS.VEHICLE_CONFIGURATOR_DETACHMENT_WIDGET:
            self.__detachmentView = viewPy.getInjectView()
            self.__detachmentView.onSetHeight += self.__onDetachmentSetHeightHandler
            self.as_setDetachmentHeightS(self.__detachmentView.height)

    def _init(self):
        super(VehicleCompareConfiguratorView, self)._init()
        currentVehicle = self._container.getCurrentVehicle()
        topModulesFromStock = self._container.isTopModulesFromStock()
        enableTopModules = not (currentVehicle.isPremium or topModulesFromStock)
        self.as_setInitDataS({'title': _ms(VEH_COMPARE.VEHCONF_HEADER, vehName=currentVehicle.userName),
         'resetBtnLabel': VEH_COMPARE.VEHCONF_RESETBTNLABEL,
         'cancelBtnLabel': VEH_COMPARE.VEHCONF_CANCELBTNLABEL,
         'applyBtnLabel': VEH_COMPARE.VEHCONF_APPLYBTNLABEL,
         'resetBtnTooltip': VEH_COMPARE.VEHCONF_RESETBTNLABEL_TOOLTIP,
         'cancelBtnTooltip': VEH_COMPARE.VEHCONF_CANCELBTNLABEL_TOOLTIP,
         'applyBtnTooltip': VEH_COMPARE.VEHCONF_COMPAREBTNLABEL_TOOLTIP,
         'enableTopModules': enableTopModules})
        self.__updateControlBtns()
        topModulesSelected = topModulesFromStock or self._container.isTopModulesSelected()
        self.as_setTopModulesSelectedS(topModulesSelected)
        initialVehicle = self._container.getInitialVehicleData()
        self.__parametersView.setInitialVehicle(initialVehicle)
        self.__parametersView.setVehicle(currentVehicle)
        self.__detachmentView.setPerks(self._container.perks)
        self.__updateSlotsData(VEHICLE_FITTING_SLOTS)

    def _dispose(self):
        if self.__detachmentView:
            self.__detachmentView.onSetHeight -= self.__onDetachmentSetHeightHandler
            self.__detachmentView = None
        self.__parametersView = None
        self.__configuratorInject = None
        super(VehicleCompareConfiguratorView, self)._dispose()
        return

    def __onDetachmentSetHeightHandler(self):
        self.as_setDetachmentHeightS(self.__detachmentView.height)

    def __updateSlotsData(self, slotsTypes):
        newVoData = getFittingSlotsData(self._container.getCurrentVehicle(), slotsTypes, _ConfigFittingSlotVO)
        for slotType in slotsTypes:
            indexesRange = _SLOT_DATA_INDEXES[VEHICLE_FITTING_SLOTS.index(slotType)]
            for idx in indexesRange:
                newSlotData = newVoData.pop(0)
                self.__slotsVoData[idx] = newSlotData

        self.as_setDevicesDataS(self.__slotsVoData)
        self.__updateParametersView()

    def __updateParametersView(self):
        if self.__parametersView is not None:
            self.__parametersView.update()
            self.__updateControlBtns()
        return

    def __updateControlBtns(self):
        self.as_setResetEnabledS(self._container.isDifferentWithInitialBasketVeh())
        self.as_setApplyEnabledS(self._container.isCurrentVehicleModified())

    def __updateShellSlots(self):
        self.__configuratorInject.updateShells()


class VehicleCompareConfiguratorMain(LobbySubView, VehicleCompareConfiguratorMainMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, ctx=None):
        super(VehicleCompareConfiguratorMain, self).__init__(ctx)
        self.__vehIndex = ctx.get('index')
        if not isinstance(self.__vehIndex, int):
            raise UserWarning('Index of vehicle should be integer: {}'.format(self.__vehIndex))
        if self.__vehIndex < 0 or self.__vehIndex >= self.comparisonBasket.getVehiclesCount():
            raise UserWarning('Index of vehicle out of range: {} not in (0, {})'.format(self.__vehIndex, self.comparisonBasket.getVehiclesCount()))
        self.__backAlias = ctx.get('previewAlias', VIEW_ALIAS.VEHICLE_COMPARE)
        self.__vehicle = None
        self.__vehItem = None
        self.__views = {}
        self.__topModules = None
        self.__stockModules = None
        self.__selectedShellIndex = None
        self.__perks = PerksData()
        return

    @property
    def perks(self):
        return self.__perks

    def as_showViewS(self, alias):
        result = super(VehicleCompareConfiguratorMain, self).as_showViewS(alias)
        if alias in self.__views:
            self.__views[alias].onShow()
        return result

    def getCurrentVehicle(self):
        return self.__vehicle

    def getCurrentVehicleItem(self):
        return self.__vehItem

    def getInitialVehicleData(self):
        basketVehicle = self.getBasketVehCmpData()
        if basketVehicle.isInInventory():
            strCD = basketVehicle.getInvVehStrCD()
            equipment = basketVehicle.getInvEquipment()
            perks = basketVehicle.getInvPerks()
            battleBooster = basketVehicle.getInvBattleBooster()
        else:
            strCD = basketVehicle.getStockVehStrCD()
            equipment = basketVehicle.getStockEquipment()
            perks = basketVehicle.getStockPerks()
            battleBooster = None
        vehicle = Vehicle(strCD)
        for slotIndex, equipmentSlot in enumerate(equipment):
            vehicle_adjusters.installEquipment(vehicle, equipmentSlot, slotIndex)

        cmp_helpers.applyCamouflage(vehicle, basketVehicle.invHasCamouflage())
        if battleBooster is not None:
            vehicle_adjusters.installBattleBoosterOnVehicle(vehicle, battleBooster.intCD)
        cmp_helpers.setPerksController(vehicle, perks)
        return vehicle

    def getInitialPerks(self):
        basketVehicle = self.getBasketVehCmpData()
        return basketVehicle.getInvPerks() if basketVehicle.isInInventory() else basketVehicle.getStockPerks()

    def getBasketVehCmpData(self):
        return self.comparisonBasket.getVehicleAt(self.__vehIndex)

    def getCurrentShellIndex(self):
        return self.__selectedShellIndex

    def isTopModulesFromStock(self):
        topModules = self.__getTopModules()
        stockModules = self.__getStockModules()
        return all((bool(item in stockModules) for item in topModules))

    def isTopModulesSelected(self):
        topModules = self.__getTopModules()
        selectedModules = cmp_helpers.getVehicleModules(self.__vehicle)
        return all((bool(item in selectedModules) for item in topModules))

    def isCamouflageSet(self):
        return cmp_helpers.isCamouflageSet(self.__vehicle)

    def applyNewParameters(self):
        self.comparisonBasket.applyNewParameters(self.__vehIndex, self.__vehicle, self.__perks, self.getCurrentShellIndex())

    def isDifferentWithInitialBasketVeh(self):
        basketVehicle = self.getBasketVehCmpData()
        if basketVehicle.isInInventory():
            equipment = basketVehicle.getInvEquipment()
            strCD = basketVehicle.getInvVehStrCD()
        else:
            equipment = basketVehicle.getStockEquipment()
            strCD = basketVehicle.getStockVehStrCD()
        return self.__isHasDifferences(strCD, equipment, basketVehicle.getInventoryShellIndex(), basketVehicle.invHasCamouflage(), basketVehicle.getInvBattleBooster(), self.getInitialPerks())

    def isCurrentVehicleModified(self):
        basketVehicle = self.getBasketVehCmpData()
        return self.__isHasDifferences(basketVehicle.getVehicleStrCD(), basketVehicle.getEquipment(), basketVehicle.getSelectedShellIndex(), basketVehicle.hasCamouflage(), basketVehicle.getBattleBooster(), basketVehicle.getPerks())

    def __isHasDifferences(self, strCD, equipment, selShellIndex, hasCamouflage, battleBooster, perks):
        if not cmp_helpers.isEquipmentSame(equipment, self.__vehicle.consumables.installed.getIntCDs(default=None)):
            return True
        elif selShellIndex != self.__selectedShellIndex:
            return True
        currVehHasCamouflage = cmp_helpers.isCamouflageSet(self.__vehicle)
        if hasCamouflage != currVehHasCamouflage:
            return True
        currVehBattleBoosters = self.__vehicle.battleBoosters.installed
        if currVehBattleBoosters.getCapacity() > 0 and not battleBooster == currVehBattleBoosters[0]:
            return True
        if currVehHasCamouflage:
            targetVehicle = Vehicle(self.__vehicle.descriptor.makeCompactDescr())
            cmp_helpers.removeVehicleCamouflages(targetVehicle)
        else:
            targetVehicle = self.__vehicle
        if strCD != targetVehicle.descriptor.makeCompactDescr():
            return True
        else:
            return True if self.__perks != perks else False

    def setModules(self, modules):
        if modules:
            notFittedReasons = []
            oldGunIntCD = self.__vehicle.gun.intCD
            vehicle_adjusters.installModulesSet(self.__vehicle, list(modules[:]), notFittedReasons)
            if notFittedReasons:
                for notFitReason in notFittedReasons:
                    LOG_DEBUG('Module has not been installed properly, reason: {}'.format(notFitReason))

            if oldGunIntCD != self.__vehicle.gun.intCD:
                firstShellIndex = 0
                newShellIndex = -1
                if self.__updateSelectedShell(firstShellIndex):
                    newShellIndex = firstShellIndex
                self.__notifyViews('onShellsUpdated', updateShells=True, selectedIndex=newShellIndex)
            else:
                newGunToInstall = findFirst(lambda module: module.itemTypeID == GUI_ITEM_TYPE.GUN, modules, None)
                if newGunToInstall is not None:
                    self.__vehicle.descriptor.activeGunShotIndex = self.__selectedShellIndex
            self.__notifyViews('onModulesUpdated')
        return

    def selectTopModules(self, select):
        if select:
            modules = self.__getTopModules()
        else:
            modules = self.__getStockModules()
        self.setModules(modules)

    def selectShell(self, slotIndex):
        if self.__updateSelectedShell(slotIndex):
            self.__notifyViews('onShellsUpdated', selectedIndex=slotIndex)

    def setPerks(self, perks):
        if self.__perks != perks:
            self.__perks = perks
            cmp_helpers.setPerksController(self.__vehicle, perks)
            self.__notifyViews('onPerksUpdated')

    def selectCamouflage(self, select):
        cmp_helpers.applyCamouflage(self.__vehicle, select)
        self.__notifyViews('onCamouflageUpdated')

    def resetToDefault(self):
        self.__vehicle = self.getInitialVehicleData()
        self.__vehItem.setItem(self.__vehicle)
        basketShellIndex = self.getBasketVehCmpData().getInventoryShellIndex()
        self.__updateSelectedShell(basketShellIndex)
        self.setPerks(self.getInitialPerks())
        self.__notifyViews('onResetToDefault')

    def installOptionalDevice(self, newId, slotIndex):
        isInstalled, _ = vehicle_adjusters.installOptionalDevice(self.__vehicle, newId, slotIndex)
        if isInstalled:
            self.__notifyViews('onOptDeviceUpdated')

    def swapOptionalDevice(self, leftID, rightID):
        isSwapped, _ = vehicle_adjusters.swapOptionalDevice(self.__vehicle, leftID, rightID)
        if isSwapped:
            self.__notifyViews('onOptDeviceUpdated')

    def removeOptionalDevice(self, slotIndex):
        self.__launchOptDeviceRemoving(slotIndex)

    def installEquipment(self, newId, slotIndex):
        self.__installEquipment(newId, slotIndex)
        self.__notifyViews('onEquipmentUpdated')

    def removeEquipment(self, slotIndex):
        self.__installEquipment(None, slotIndex)
        self.__notifyViews('onEquipmentUpdated')
        return

    def swapEquipment(self, leftID, rightID):
        vehicle_adjusters.swapEquipment(self.__vehicle, leftID, rightID)
        self.__notifyViews('onEquipmentUpdated')

    def installBattleBooster(self, newId):
        self.__installBattleBooster(newId)
        self.__notifyViews('onBattleBoosterUpdated')

    def removeBattleBooster(self):
        self.__installBattleBooster(None)
        self.__notifyViews('onBattleBoosterUpdated')
        return

    def closeView(self, forcedBackAlias=None):
        event = g_entitiesFactories.makeLoadEvent(SFViewLoadParams(forcedBackAlias or self.__backAlias))
        self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(VehicleCompareConfiguratorMain, self)._populate()
        self.comparisonBasket.onSwitchChange += self.__onBasketStateChanged
        basketVehicleData = self.getBasketVehCmpData()
        self.__vehicle = Vehicle(basketVehicleData.getVehicleStrCD())
        self.__vehItem = CompareInteractingItem(self.__vehicle)
        cmp_helpers.setPerksController(self.__vehicle, basketVehicleData.getPerks())
        equipment = basketVehicleData.getEquipment()
        for slotIndex, equipmentSlot in enumerate(equipment):
            self.__installEquipment(equipmentSlot, slotIndex)

        cmp_helpers.applyCamouflage(self.__vehicle, basketVehicleData.hasCamouflage())
        battleBooster = basketVehicleData.getBattleBooster()
        if battleBooster is not None:
            vehicle_adjusters.installBattleBoosterOnVehicle(self.__vehicle, battleBooster.intCD)
        self.__perks = basketVehicleData.getPerks()
        self.__updateSelectedShell(basketVehicleData.getSelectedShellIndex())
        self.as_showViewS(VEHICLE_COMPARE_CONSTANTS.VEHICLE_CONFIGURATOR_VIEW)
        self.comparisonBasket.isLocked = True
        return

    def _dispose(self):
        self.comparisonBasket.onSwitchChange -= self.__onBasketStateChanged
        self.__vehItem.clear()
        self.__vehItem = None
        self.__views = None
        self.comparisonBasket.isLocked = False
        super(VehicleCompareConfiguratorMain, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(VehicleCompareConfiguratorMain, self)._onRegisterFlashComponent(viewPy, alias)
        if isinstance(viewPy, VehicleCompareConfiguratorBaseView):
            self.__views[alias] = viewPy
            viewPy.setContainer(self)

    @process
    def __launchOptDeviceRemoving(self, slotIndex):
        installedDevice = self.__vehicle.optDevices.installed[slotIndex]
        if installedDevice is not None:
            result = yield _CmpOptDeviceRemover(self.__vehicle, installedDevice, slotIndex).request()
            if result.success:
                self.__notifyViews('onOptDeviceUpdated')
            else:
                processMsg(result)
        return

    def __getTopModules(self):
        if self.__topModules is None:
            self.__topModules = cmp_helpers.getVehicleTopModules(self.__vehicle)
        return self.__topModules

    def __getStockModules(self):
        if self.__stockModules is None:
            self.__stockModules = tuple(reversed(cmp_helpers.getVehicleModules(Vehicle(self.getBasketVehCmpData().getStockVehStrCD()))))
        return self.__stockModules

    def __installEquipment(self, intCD, slotIndex):
        vehicle_adjusters.installEquipment(self.__vehicle, intCD, slotIndex)

    def __installBattleBooster(self, intCD):
        vehicle_adjusters.installBattleBoosterOnVehicle(self.__vehicle, intCD)

    def __updateSelectedShell(self, slotIndex):
        slotIndex = int(slotIndex)
        if self.__selectedShellIndex != slotIndex:
            vehicle_adjusters.changeShell(self.__vehicle, slotIndex)
            self.__selectedShellIndex = slotIndex
            return True
        return False

    def __onBasketStateChanged(self):
        if not self.comparisonBasket.isEnabled():
            self.closeView(VIEW_ALIAS.LOBBY_HANGAR)

    def __notifyViews(self, event, *args, **kwargs):
        for component in self.__views.itervalues():
            notifier = getattr(component, event, None)
            if notifier and callable(notifier):
                notifier(*args, **kwargs)

        return
