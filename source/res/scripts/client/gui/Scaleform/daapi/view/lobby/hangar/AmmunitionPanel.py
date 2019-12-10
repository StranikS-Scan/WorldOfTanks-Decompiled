# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/AmmunitionPanel.py
import logging
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import AccountSettings
from account_helpers.AccountSettings import BOOSTERS_FOR_CREDITS_SLOT_COUNTER
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.shared.fitting_slot_vo import FittingSlotVO, HangarFittingSlotVO
from gui.Scaleform.daapi.view.meta.AmmunitionPanelMeta import AmmunitionPanelMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import event_dispatcher as shared_events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showNewYearVehiclesView
from gui.shared.events import LoadViewEvent
from gui.shared.gui_items import GUI_ITEM_TYPE_INDICES, GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.gui_items.vehicle_equipment import BATTLE_BOOSTER_LAYOUT_SIZE
from gui.shared.utils import decorators
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.functions import makeTooltip
from helpers import i18n, dependency, int2roman
from items.vehicles import NUM_OPTIONAL_DEVICE_SLOTS
from new_year.ny_constants import SyncDataKeys
from new_year.vehicle_branch import ApplyVehicleBranchStyleProcessor, getBonusByVehicle
from ny_common.settings import NY_CONFIG_NAME, NYVehBranchConsts
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
ARTEFACTS_SLOTS = (GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.OPTIONALDEVICE], GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.EQUIPMENT])
_BOOSTERS_SLOTS = (GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.BATTLE_BOOSTER],)
_ABILITY_SLOTS = (GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.BATTLE_ABILITY],)
FITTING_MODULES = (GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.CHASSIS],
 GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.TURRET],
 GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.GUN],
 GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.ENGINE],
 GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.RADIO])
_BONUS_ICONS = {'xpFactor': R.images.gui.maps.icons.new_year.vehicles_view.icons.icon_battle_exp_main(),
 'freeXPFactor': R.images.gui.maps.icons.new_year.vehicles_view.icons.icon_free_exp_main_screen(),
 'tankmenXPFactor': R.images.gui.maps.icons.new_year.vehicles_view.icons.icon_crew_exp_main()}
FITTING_SLOTS = FITTING_MODULES + ARTEFACTS_SLOTS
HANGAR_FITTING_SLOTS = FITTING_SLOTS + _BOOSTERS_SLOTS + _ABILITY_SLOTS
VEHICLE_FITTING_SLOTS = FITTING_SLOTS + _BOOSTERS_SLOTS
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getFittingSlotsData(vehicle, slotsRange, VoClass=None, itemsCache=None):
    devices = []
    VoClass = VoClass or FittingSlotVO
    for slotType in slotsRange:
        data = itemsCache.items.getItems(GUI_ITEM_TYPE_INDICES[slotType], REQ_CRITERIA.CUSTOM(lambda item: item.isInstalled(vehicle))).values()
        if slotType in ARTEFACTS_SLOTS:
            for slotId in xrange(NUM_OPTIONAL_DEVICE_SLOTS):
                devices.append(VoClass(data, vehicle, slotType, slotId, TOOLTIPS_CONSTANTS.HANGAR_MODULE))

        if slotType in _BOOSTERS_SLOTS:
            for slotId in xrange(BATTLE_BOOSTER_LAYOUT_SIZE):
                devices.append(VoClass(data, vehicle, slotType, slotId, tooltipType=TOOLTIPS_CONSTANTS.BATTLE_BOOSTER))

        if slotType in _ABILITY_SLOTS:
            for slotId, _ in enumerate(vehicle.equipment.battleAbilityConsumables.getIntCDs()):
                devices.append(VoClass(data, vehicle, slotType, slotId, tooltipType=TOOLTIPS_CONSTANTS.EPIC_SKILL_SLOT_INFO))

        devices.append(VoClass(data, vehicle, slotType, tooltipType=TOOLTIPS_CONSTANTS.HANGAR_MODULE))

    return devices


def getAmmo(shells):
    outcome = []
    for shell in shells:
        if shell.isHidden:
            continue
        outcome.append({'id': str(shell.intCD),
         'type': shell.type,
         'label': ITEM_TYPES.shell_kindsabbreviation(shell.type),
         'icon': '../maps/icons/ammopanel/ammo/%s' % shell.descriptor.icon[0],
         'count': shell.count,
         'tooltip': '',
         'tooltipType': TOOLTIPS_CONSTANTS.HANGAR_SHELL})

    return outcome


class AmmunitionPanel(AmmunitionPanelMeta, IGlobalListener):
    __slots__ = ('__hangarMessage',)
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)
    _nyController = dependency.descriptor(INewYearController)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(AmmunitionPanel, self).__init__()
        self.__hangarMessage = None
        g_currentVehicle.onChanged += self.__updateTankName
        return

    def update(self):
        self._update()

    def showTechnicalMaintenance(self):
        self.fireEvent(LoadViewEvent(VIEW_ALIAS.TECHNICAL_MAINTENANCE), EVENT_BUS_SCOPE.LOBBY)

    def showCustomization(self):
        self.service.showCustomization()

    def toggleNYCustomization(self, selected):
        self.__applyNewYearStyle()

    def toRentContinue(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            canBuyOrRent, _ = vehicle.mayObtainForMoney(self.itemsCache.items.stats.money)
            if vehicle.isRentable and vehicle.rentalIsOver and canBuyOrRent:
                shared_events.showVehicleBuyDialog(vehicle)

    def showChangeNation(self):
        if g_currentVehicle.isPresent() and g_currentVehicle.item.hasNationGroup:
            ItemsActionsFactory.doAction(ItemsActionsFactory.CHANGE_NATION, g_currentVehicle.item.intCD)

    def showModuleInfo(self, itemCD):
        if itemCD is not None and int(itemCD) > 0:
            shared_events.showModuleInfo(itemCD, g_currentVehicle.item.descriptor)
        return

    def onNYBonusPanelClicked(self):
        showNewYearVehiclesView()

    @staticmethod
    def _getVehicleIcon(vehicleType):
        vehTypeStr = vehicleType.replace('-', '_')
        backPortImage = backport.image(R.images.gui.maps.icons.new_year.vehicles_view.icons.dyn(vehTypeStr)())
        return "<img src='{0}'/>".format(backPortImage.replace('../', 'img://gui/'))

    def _populate(self):
        super(AmmunitionPanel, self)._populate()
        self.startGlobalListening()
        g_clientUpdateManager.addMoneyCallback(self.__moneyUpdateCallback)
        g_clientUpdateManager.addCallbacks({'inventory': self.__inventoryUpdateCallBack})
        self.update()
        self._nyController.onDataUpdated += self.__onNewYearDataUpdated
        self._nyController.onStateChanged += self.__onNewYearStateUpdated
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsUpdate
        AccountSettings.onSettingsChanging += self.__onAccountSettingsChanging

    def _dispose(self):
        self.stopGlobalListening()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__hangarMessage = None
        AccountSettings.onSettingsChanging -= self.__onAccountSettingsChanging
        self._nyController.onDataUpdated -= self.__onNewYearDataUpdated
        self._nyController.onStateChanged -= self.__onNewYearStateUpdated
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsUpdate
        g_currentVehicle.onChanged -= self.__updateTankName
        super(AmmunitionPanel, self)._dispose()
        return

    def _update(self, onlyMoneyUpdate=False):
        if g_currentVehicle.isPresent():
            hangarMessage = g_currentVehicle.getHangarMessage()
            if onlyMoneyUpdate and self.__hangarMessage == hangarMessage:
                return
            vehicle = g_currentVehicle.item
            self.__hangarMessage = hangarMessage
            statusId, msg, msgLvl = hangarMessage
            rentAvailable = False
            if statusId in (Vehicle.VEHICLE_STATE.RENTAL_IS_OVER, Vehicle.VEHICLE_STATE.RENTABLE_AGAIN):
                canBuyOrRent, _ = vehicle.mayObtainForMoney(self.itemsCache.items.stats.money)
                rentAvailable = vehicle.isRentable and canBuyOrRent
            if msgLvl == Vehicle.VEHICLE_STATE_LEVEL.RENTABLE:
                msgLvl = Vehicle.VEHICLE_STATE_LEVEL.INFO
            isBackground = statusId == Vehicle.VEHICLE_STATE.NOT_PRESENT
            self.__applyCustomizationNewCounter(vehicle)
            self.__applyBoosterNewCounter()
            isNYEnabled = self._nyController.isEnabled()
            vehicleName = g_currentVehicle.item.shortUserName if isNYEnabled else ''
            vehicleLevel = int2roman(vehicle.level) if isNYEnabled else ''
            msgString = makeHtmlString('html_templates:vehicleStatus', msgLvl, {'message': '{} {} {}'.format(vehicleLevel, vehicleName, i18n.makeString(msg))})
            self.__updateDevices(vehicle)
            self.__updateNewYear()
            self.as_updateVehicleStatusS({'message': msgString,
             'rentAvailable': rentAvailable,
             'isBackground': isBackground})
            isNewYearVehicle = self._nyController.getVehicleBranch().isVehicleInBranch(vehicle) and self._nyController.isVehicleBranchEnabled()
            bonusType, bonusValue = getBonusByVehicle(vehicle)
            bonusFormatted = backport.text(R.strings.ny.vehiclesView.bonusFormat(), bonus=int(bonusValue * 100))
            self.as_setNeyYearVehicleBonusS(isNewYearVehicle, backport.image(_BONUS_ICONS[bonusType]), bonusFormatted, backport.text(R.strings.ny.vehicleBonusPanel.dyn(bonusType)(), level=int2roman(vehicle.level), vehicle=self._getVehicleIcon(vehicle.type) + ' ' + vehicle.shortUserName), makeTooltip(header=backport.text(R.strings.tooltips.tankCarusel.newYearSlot.header()), body=backport.text(R.strings.tooltips.tankCarusel.newYearSlot.body())) if isNewYearVehicle else '')

    def __inventoryUpdateCallBack(self, *args):
        self.update()

    def __updateTankName(self):
        self.update()

    def __applyCustomizationNewCounter(self, vehicle):
        counter = vehicle.getC11nItemsNoveltyCounter(self.itemsCache.items) if vehicle.isCustomizationEnabled() else 0
        self.as_setCustomizationBtnCounterS(counter)

    def __applyBoosterNewCounter(self):
        counter = AccountSettings.getCounters(BOOSTERS_FOR_CREDITS_SLOT_COUNTER)
        self.as_setBoosterBtnCounterS(counter)

    def __moneyUpdateCallback(self, *_):
        self._update(onlyMoneyUpdate=True)

    def __updateDevices(self, vehicle):
        shells = []
        stateWarning = False
        if g_currentVehicle.isPresent():
            stateWarning = vehicle.isBroken or not vehicle.isAmmoFull or not g_currentVehicle.isAutoLoadFull() or not g_currentVehicle.isAutoEquipFull()
            shells = getAmmo(vehicle.shells)
        self.as_setAmmoS(shells, stateWarning)
        self.as_setModulesEnabledS(True)
        self.as_setVehicleHasTurretS(vehicle.hasTurrets)
        slotsRange = self.__getSlotsRange()
        devices = getFittingSlotsData(vehicle, slotsRange, VoClass=HangarFittingSlotVO)
        self.as_setDataS({'devices': devices})
        if slotsRange == HANGAR_FITTING_SLOTS and self.itemsCache.items.getItems(GUI_ITEM_TYPE.BATTLE_ABILITY, REQ_CRITERIA.UNLOCKED):
            showAlert = True
            for slot in devices:
                if slot['slotType'] in _ABILITY_SLOTS and slot['id'] != -1:
                    showAlert = False
                    break

            self.as_showBattleAbilitiesAlertS(showAlert)
        else:
            self.as_showBattleAbilitiesAlertS(False)

    def __updateNewYear(self):
        isEnabled = g_currentVehicle.isPresent() and g_currentVehicle.item.isCustomizationEnabled()
        self.as_setNYCustomizationSlotStateS(g_currentVehicle.hasNewYearOutfit(), isEnabled)

    def __getSlotsRange(self):
        return HANGAR_FITTING_SLOTS if self.prbDispatcher is not None and self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC) else VEHICLE_FITTING_SLOTS

    def __onAccountSettingsChanging(self, key, _):
        if key == BOOSTERS_FOR_CREDITS_SLOT_COUNTER:
            self.__applyBoosterNewCounter()

    def __onNewYearDataUpdated(self, keys):
        if SyncDataKeys.VEHICLE_BRANCH in keys:
            self._update()

    def __onNewYearStateUpdated(self):
        self._update()

    def __onServerSettingsUpdate(self, diff):
        if NY_CONFIG_NAME in diff and NYVehBranchConsts.CONFIG_NAME in diff[NY_CONFIG_NAME]:
            self._update()

    @decorators.process('newYear/setNewYearStyle')
    def __applyNewYearStyle(self):
        yield ApplyVehicleBranchStyleProcessor(g_currentVehicle.invID).request()
