# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/AmmunitionPanel.py
import logging
from constants import QUEUE_TYPE
from gui.prb_control.entities.listener import IGlobalListener
from items.vehicles import NUM_OPTIONAL_DEVICE_SLOTS
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.shared.fitting_slot_vo import FittingSlotVO, HangarFittingSlotVO
from gui.Scaleform.daapi.view.meta.AmmunitionPanelMeta import AmmunitionPanelMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.shared import event_dispatcher as shared_events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import LoadViewEvent
from gui.shared.gui_items import GUI_ITEM_TYPE_INDICES, GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.vehicle_equipment import BATTLE_BOOSTER_LAYOUT_SIZE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import i18n, dependency
from skeletons.gui.shared import IItemsCache
from gui.prb_control.settings import CTRL_ENTITY_TYPE
ARTEFACTS_SLOTS = (GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.OPTIONALDEVICE], GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.EQUIPMENT])
_BOOSTERS_SLOTS = (GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.BATTLE_BOOSTER],)
_ABILITY_SLOTS = (GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.BATTLE_ABILITY],)
FITTING_MODULES = (GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.CHASSIS],
 GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.TURRET],
 GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.GUN],
 GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.ENGINE],
 GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.RADIO])
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
    itemsCache = dependency.descriptor(IItemsCache)

    def update(self):
        self._update()

    def showTechnicalMaintenance(self):
        self.fireEvent(LoadViewEvent(VIEW_ALIAS.TECHNICAL_MAINTENANCE), EVENT_BUS_SCOPE.LOBBY)

    def showCustomization(self):
        if not g_currentVehicle.hangarSpace.spaceInited or not g_currentVehicle.hangarSpace.isModelLoaded:
            _logger.warning('Space or vehicle is not presented, could not show customization view, return')
            return
        self.fireEvent(LoadViewEvent(VIEW_ALIAS.LOBBY_CUSTOMIZATION), EVENT_BUS_SCOPE.LOBBY)

    def toRentContinue(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            canBuyOrRent, _ = vehicle.mayObtainForMoney(self.itemsCache.items.stats.money)
            if vehicle.isRentable and vehicle.rentalIsOver and canBuyOrRent:
                shared_events.showVehicleBuyDialog(vehicle)

    def showModuleInfo(self, itemCD):
        if itemCD is not None and int(itemCD) > 0:
            shared_events.showModuleInfo(itemCD, g_currentVehicle.item.descriptor)
        return

    def showBattleAbilityView(self):
        self.fireEvent(LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_SKILL_ALIAS), EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(AmmunitionPanel, self)._populate()
        self.startGlobalListening()
        g_clientUpdateManager.addCallbacks({'inventory': self.__inventoryUpdateCallBack})
        self.update()

    def _dispose(self):
        self.stopGlobalListening()
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(AmmunitionPanel, self)._dispose()

    def _update(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            statusId, msg, msgLvl = g_currentVehicle.getHangarMessage()
            rentAvailable = False
            if statusId == Vehicle.VEHICLE_STATE.RENTAL_IS_OVER:
                canBuyOrRent, _ = vehicle.mayObtainForMoney(self.itemsCache.items.stats.money)
                rentAvailable = vehicle.isRentable and canBuyOrRent
            isBackground = statusId == Vehicle.VEHICLE_STATE.NOT_PRESENT
            msgString = makeHtmlString('html_templates:vehicleStatus', msgLvl, {'message': i18n.makeString(msg)})
            self.__updateDevices(vehicle)
            self.as_updateVehicleStatusS({'message': msgString,
             'rentAvailable': rentAvailable,
             'isBackground': isBackground})

    def __inventoryUpdateCallBack(self, *args):
        self.update()

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

    def __getSlotsRange(self):
        return HANGAR_FITTING_SLOTS if self.prbDispatcher is not None and self.prbDispatcher.getEntity().getCtrlType() == CTRL_ENTITY_TYPE.PREQUEUE and self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) else VEHICLE_FITTING_SLOTS
