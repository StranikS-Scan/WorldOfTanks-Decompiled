# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/AmmunitionPanel.py
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.shared.fitting_slot_vo import FittingSlotVO
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.game_control import getFalloutCtrl
from gui.shared.gui_items.Vehicle import Vehicle
from gui.Scaleform.daapi.view.meta.AmmunitionPanelMeta import AmmunitionPanelMeta
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE_INDICES, GUI_ITEM_TYPE_NAMES
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared import g_itemsCache
from gui.shared.events import LoadViewEvent
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from helpers import i18n
from gui.shared import event_dispatcher as shared_events

class AmmunitionPanel(AmmunitionPanelMeta):
    __FITTING_SLOTS = (GUI_ITEM_TYPE_NAMES[2],
     GUI_ITEM_TYPE_NAMES[3],
     GUI_ITEM_TYPE_NAMES[4],
     GUI_ITEM_TYPE_NAMES[5],
     GUI_ITEM_TYPE_NAMES[7],
     GUI_ITEM_TYPE_NAMES[9],
     GUI_ITEM_TYPE_NAMES[11])
    __ARTEFACTS_SLOTS = (GUI_ITEM_TYPE_NAMES[9], GUI_ITEM_TYPE_NAMES[11])
    OPTIONAL_DEVICE_SLOTS_COUNT = 3

    def update(self):
        self._update()

    def showTechnicalMaintenance(self):
        self.fireEvent(LoadViewEvent(VIEW_ALIAS.TECHNICAL_MAINTENANCE), EVENT_BUS_SCOPE.LOBBY)

    def showCustomization(self):
        self.fireEvent(LoadViewEvent(VIEW_ALIAS.LOBBY_CUSTOMIZATION), EVENT_BUS_SCOPE.LOBBY)

    def toRentContinue(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            canBuyOrRent, _ = vehicle.mayRentOrBuy(g_itemsCache.items.stats.money)
            if vehicle.isRentable and vehicle.rentalIsOver and canBuyOrRent:
                shared_events.showVehicleBuyDialog(vehicle)

    def showModuleInfo(self, itemCD):
        if itemCD is not None and int(itemCD) > 0:
            shared_events.showModuleInfo(itemCD, g_currentVehicle.item.descriptor)
        return

    def _populate(self):
        super(AmmunitionPanel, self)._populate()
        g_clientUpdateManager.addCallbacks({'inventory': self.__inventoryUpdateCallBack})
        self.__falloutCtrl = getFalloutCtrl()
        self.__falloutCtrl.onSettingsChanged += self._updateFalloutSettings
        self.update()

    def _dispose(self):
        self.__falloutCtrl.onSettingsChanged -= self._updateFalloutSettings
        self.__falloutCtrl = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(AmmunitionPanel, self)._dispose()
        return

    def _updateFalloutSettings(self):
        self._update()

    def _update(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            statusId, msg, msgLvl = g_currentVehicle.getHangarMessage()
            rentAvailable = False
            if statusId == Vehicle.VEHICLE_STATE.RENTAL_IS_ORVER:
                canBuyOrRent, _ = vehicle.mayRentOrBuy(g_itemsCache.items.stats.money)
                rentAvailable = vehicle.isRentable and canBuyOrRent
            isBackground = statusId == Vehicle.VEHICLE_STATE.NOT_PRESENT
            msgString = makeHtmlString('html_templates:vehicleStatus', msgLvl, {'message': i18n.makeString(msg)})
            self.__updateDevices(vehicle)
            self.as_updateVehicleStatusS({'message': msgString,
             'rentAvailable': rentAvailable,
             'isBackground': isBackground})

    def __inventoryUpdateCallBack(self, *args):
        self.update()

    def __updateAmmo(self):
        shells = []
        stateWarning = False
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            stateWarning = vehicle.isBroken or not vehicle.isAmmoFull or not g_currentVehicle.isAutoLoadFull() or not g_currentVehicle.isAutoEquipFull()
            for shell in vehicle.shells:
                shells.append({'id': str(shell.intCD),
                 'type': shell.type,
                 'label': ITEM_TYPES.shell_kindsabbreviation(shell.type),
                 'icon': '../maps/icons/ammopanel/ammo/%s' % shell.descriptor['icon'][0],
                 'count': shell.count,
                 'tooltip': '',
                 'tooltipType': TOOLTIPS_CONSTANTS.HANGAR_SHELL})

        self.as_setAmmoS(shells, stateWarning)

    def __updateDevices(self, vehicle):
        devices = []
        self.__updateAmmo()
        self.as_setModulesEnabledS(True)
        self.as_setVehicleHasTurretS(vehicle.hasTurrets)
        for slotType in AmmunitionPanel.__FITTING_SLOTS:
            data = g_itemsCache.items.getItems(GUI_ITEM_TYPE_INDICES[slotType], REQ_CRITERIA.CUSTOM(lambda item: item.isInstalled(vehicle))).values()
            if slotType in AmmunitionPanel.__ARTEFACTS_SLOTS:
                for slotId in xrange(self.OPTIONAL_DEVICE_SLOTS_COUNT):
                    devices.append(FittingSlotVO(data, vehicle, slotType, slotId, TOOLTIPS_CONSTANTS.HANGAR_MODULE))

            devices.append(FittingSlotVO(data, vehicle, slotType, tooltipType=TOOLTIPS_CONSTANTS.HANGAR_MODULE))

        self.as_setDataS({'devices': devices})
