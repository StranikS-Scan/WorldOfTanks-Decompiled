# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/markPreview/MarkModulesPanel.py
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.shared.fitting_slot_vo import FittingSlotVO
from gui.Scaleform.daapi.view.meta.ModulesPanelMeta import ModulesPanelMeta
from gui.shared.gui_items import GUI_ITEM_TYPE_INDICES, GUI_ITEM_TYPE_NAMES
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared import g_itemsCache
from items import ITEM_TYPES
from gui.shared import event_dispatcher as shared_events
_MODULE_SLOTS = (GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleGun],
 GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleTurret],
 GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleEngine],
 GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleChassis],
 GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleRadio])

class MarkModulesPanel(ModulesPanelMeta):

    def __init__(self):
        super(MarkModulesPanel, self).__init__()
        vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.MARK1)
        if vehicles:
            self.__mark1Vehicle = vehicles.values()[0]
        else:
            self.__mark1Vehicle = None
            LOG_ERROR('Mark1 Vehicle is not found. Check list.xml and tag <markI>')
        return

    def _populate(self):
        super(MarkModulesPanel, self)._populate()
        self.update()

    def _dispose(self):
        super(MarkModulesPanel, self)._dispose()

    def update(self, *args):
        self._update()

    def showModuleInfo(self, itemCD):
        if itemCD is not None and int(itemCD) > 0 and self.__mark1Vehicle is not None:
            shared_events.showModuleInfo(itemCD, self.__mark1Vehicle.intCD)
        return

    def _update(self):
        if self.__mark1Vehicle:
            self.as_setModulesEnabledS(True)
            devices = []
            self.as_setModulesEnabledS(True)
            self.as_setVehicleHasTurretS(self.__mark1Vehicle.hasTurrets)
            for slotType in _MODULE_SLOTS:
                data = g_itemsCache.items.getItems(GUI_ITEM_TYPE_INDICES[slotType], REQ_CRITERIA.CUSTOM(lambda item: item.isInstalled(self.__mark1Vehicle))).values()
                devices.append(FittingSlotVO(data, self.__mark1Vehicle, slotType))

            self.as_setDataS({'devices': devices})
