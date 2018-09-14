# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview/ModulesPanel.py
from debug_utils import LOG_ERROR
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.lobby.shared.fitting_slot_vo import FittingSlotVO
from gui.Scaleform.daapi.view.meta.ModulesPanelMeta import ModulesPanelMeta
from gui.shared.gui_items import GUI_ITEM_TYPE_INDICES, GUI_ITEM_TYPE_NAMES
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared import g_itemsCache
from items import ITEM_TYPES
from gui.shared import event_dispatcher as shared_events
_MODULE_SLOTS = (GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleChassis],
 GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleTurret],
 GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleGun],
 GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleEngine],
 GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleRadio])

class ModulesPanel(ModulesPanelMeta):

    def _populate(self):
        super(ModulesPanel, self)._populate()
        g_currentPreviewVehicle.onComponentInstalled += self.update
        g_currentPreviewVehicle.onChanged += self.update
        self.update()

    def _dispose(self):
        g_currentPreviewVehicle.onComponentInstalled -= self.update
        g_currentPreviewVehicle.onChanged -= self.update
        super(ModulesPanel, self)._dispose()

    def update(self, *args):
        self._update()

    def showModuleInfo(self, itemCD):
        if itemCD is not None and int(itemCD) > 0:
            shared_events.showModuleInfo(itemCD, g_currentPreviewVehicle.item.descriptor)
        return

    def _update(self):
        if g_currentPreviewVehicle.isPresent():
            self.as_setModulesEnabledS(True)
            vehicle = g_currentPreviewVehicle.item
            devices = []
            self.as_setModulesEnabledS(True)
            self.as_setVehicleHasTurretS(vehicle.hasTurrets)
            for slotType in _MODULE_SLOTS:
                data = g_itemsCache.items.getItems(GUI_ITEM_TYPE_INDICES[slotType], REQ_CRITERIA.CUSTOM(lambda item: item.isInstalled(vehicle))).values()
                devices.append(FittingSlotVO(data, vehicle, slotType))

            self.as_setDataS({'devices': devices})
