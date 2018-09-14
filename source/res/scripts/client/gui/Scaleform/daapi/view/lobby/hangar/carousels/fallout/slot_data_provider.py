# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/fallout/slot_data_provider.py
from gui.shared.formatters import icons
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import Vehicle
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from helpers import i18n, int2roman

def _getStatusString(vState):
    if vState == Vehicle.VEHICLE_STATE.IN_PREMIUM_IGR_ONLY:
        status = i18n.makeString('#menu:tankCarousel/vehicleStates/{}'.format(vState), icon=icons.premiumIgrSmall())
    elif vState not in (Vehicle.VEHICLE_STATE.FALLOUT_BROKEN, Vehicle.VEHICLE_STATE.FALLOUT_MIN):
        status = i18n.makeString('#menu:tankCarousel/vehicleStates/{}'.format(vState))
    else:
        status = ''
    return status


class SlotDataProvider(SortableDAAPIDataProvider):

    def __init__(self, falloutCtrl, itemsCache):
        super(SlotDataProvider, self).__init__()
        self._list = []
        self._itemsCache = itemsCache
        self._falloutCtrl = falloutCtrl

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return None

    def clear(self):
        self._list = []

    def fini(self):
        self.clear()
        self._dispose()

    def buildList(self):
        self.clear()
        config = self._falloutCtrl.getConfig()
        for slotIdx, vehicleInvId in enumerate(self._falloutCtrl.getSelectedSlots()):
            vehicle = self._itemsCache.items.getVehicle(vehicleInvId)
            isSlotRequired = slotIdx in self._falloutCtrl.getRequiredSlots()
            if self._falloutCtrl.mustSelectRequiredVehicle():
                status = i18n.makeString(FALLOUT.MULTISELECTIONSLOT_DOMINATION_REQUIREDVEHICLENOTACTIVATED, level=int2roman(config.vehicleLevelRequired))
            else:
                status = i18n.makeString(FALLOUT.MULTISELECTIONSLOT_DOMINATION_VEHICLENOTACTIVATED)
            if isSlotRequired:
                style = text_styles.alert
            else:
                style = text_styles.standard
            data = {'indexStr': i18n.makeString(FALLOUT.MULTISELECTIONSLOT_INDEX, index=slotIdx + 1),
             'isActivated': False,
             'formattedStatusStr': style(status),
             'stateLevel': '',
             'showAlert': isSlotRequired,
             'alertTooltip': TOOLTIPS.MULTISELECTION_ALERT}
            if vehicle is not None:
                vState, vStateLvl = vehicle.getState()
                data.update({'isActivated': True,
                 'formattedStatusStr': _getStatusString(vState),
                 'inventoryId': vehicle.invID,
                 'vehicleName': vehicle.shortUserName,
                 'vehicleIcon': vehicle.iconSmall,
                 'vehicleType': vehicle.type,
                 'vehicleLevel': vehicle.level,
                 'isElite': vehicle.isElite,
                 'stat': vState,
                 'stateLevel': vStateLvl,
                 'showAlert': False})
            self._list.append(data)

        self.refresh()
        return

    def _dispose(self):
        self._itemsCache = None
        self._falloutCtrl = None
        super(SlotDataProvider, self)._dispose()
        return
