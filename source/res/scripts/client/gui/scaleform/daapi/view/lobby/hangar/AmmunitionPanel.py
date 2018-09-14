# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/AmmunitionPanel.py
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.shared.fitting_slot_vo import FittingSlotVO
from gui.Scaleform.daapi.view.meta.AmmunitionPanelMeta import AmmunitionPanelMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.shared import event_dispatcher as shared_events
from gui.shared import g_itemsCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import LoadViewEvent
from gui.shared.gui_items import GUI_ITEM_TYPE_INDICES, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import i18n, dependency
from skeletons.gui.game_control import IFalloutController
OPTIONAL_DEVICE_SLOTS_COUNT = 3
ARTEFACTS_SLOTS = (GUI_ITEM_TYPE_NAMES[9], GUI_ITEM_TYPE_NAMES[11])
FITTING_MODULES = (GUI_ITEM_TYPE_NAMES[2],
 GUI_ITEM_TYPE_NAMES[3],
 GUI_ITEM_TYPE_NAMES[4],
 GUI_ITEM_TYPE_NAMES[5],
 GUI_ITEM_TYPE_NAMES[7])
FITTING_SLOTS = FITTING_MODULES + (GUI_ITEM_TYPE_NAMES[9], GUI_ITEM_TYPE_NAMES[11])

def getFittingSlotsData(vehicle, slotsRange, VoClass=None):
    devices = []
    VoClass = VoClass or FittingSlotVO
    for slotType in slotsRange:
        data = g_itemsCache.items.getItems(GUI_ITEM_TYPE_INDICES[slotType], REQ_CRITERIA.CUSTOM(lambda item: item.isInstalled(vehicle))).values()
        if slotType in ARTEFACTS_SLOTS:
            for slotId in xrange(OPTIONAL_DEVICE_SLOTS_COUNT):
                devices.append(VoClass(data, vehicle, slotType, slotId, TOOLTIPS_CONSTANTS.HANGAR_MODULE))

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
         'icon': '../maps/icons/ammopanel/ammo/%s' % shell.descriptor['icon'][0],
         'count': shell.count,
         'tooltip': '',
         'tooltipType': TOOLTIPS_CONSTANTS.HANGAR_SHELL})

    return outcome


class AmmunitionPanel(AmmunitionPanelMeta):
    falloutCtrl = dependency.descriptor(IFalloutController)

    def update(self):
        self._update()

    def showTechnicalMaintenance(self):
        self.fireEvent(LoadViewEvent(VIEW_ALIAS.TECHNICAL_MAINTENANCE), EVENT_BUS_SCOPE.LOBBY)

    def showCustomization(self):
        self.fireEvent(LoadViewEvent(VIEW_ALIAS.LOBBY_CUSTOMIZATION), EVENT_BUS_SCOPE.LOBBY)

    def toRentContinue(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            canBuyOrRent, _ = vehicle.mayObtainForMoney(g_itemsCache.items.stats.money)
            if vehicle.isRentable and vehicle.rentalIsOver and canBuyOrRent:
                shared_events.showVehicleBuyDialog(vehicle)

    def showModuleInfo(self, itemCD):
        if itemCD is not None and int(itemCD) > 0:
            shared_events.showModuleInfo(itemCD, g_currentVehicle.item.descriptor)
        return

    def _populate(self):
        super(AmmunitionPanel, self)._populate()
        g_clientUpdateManager.addCallbacks({'inventory': self.__inventoryUpdateCallBack})
        self.falloutCtrl.onSettingsChanged += self._updateFalloutSettings
        self.update()

    def _dispose(self):
        self.falloutCtrl.onSettingsChanged -= self._updateFalloutSettings
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(AmmunitionPanel, self)._dispose()

    def _updateFalloutSettings(self):
        self._update()

    def _update(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            statusId, msg, msgLvl = g_currentVehicle.getHangarMessage()
            rentAvailable = False
            if statusId == Vehicle.VEHICLE_STATE.RENTAL_IS_ORVER:
                canBuyOrRent, _ = vehicle.mayObtainForMoney(g_itemsCache.items.stats.money)
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
        self.as_setDataS({'devices': getFittingSlotsData(vehicle, FITTING_SLOTS)})
