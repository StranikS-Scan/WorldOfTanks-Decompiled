# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/fitting_slot_vo.py
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.utils import EXTRA_MODULE_INFO

class _SlotVOConstants(object):
    UNRESOLVED_LIST_INDEX = -1
    MODULE_LABEL_EMPTY = 'empty'


class FittingSlotVO(dict):

    def __init__(self, modulesData, vehicle, moduleType, tooltipType=None, isDisabledTooltip=False):
        super(FittingSlotVO, self).__init__()
        if moduleType == FITTING_TYPES.VEHICLE_TURRET and not vehicle.hasTurrets:
            ttType = ''
        else:
            ttType = tooltipType or TOOLTIPS_CONSTANTS.PREVIEW_MODULE
        vehicleModule = self._prepareModule(modulesData, vehicle)
        if moduleType == FITTING_TYPES.VEHICLE_CHASSIS:
            if vehicleModule and vehicleModule.isWheeledChassis():
                moduleType = FITTING_TYPES.VEHICLE_WHEELED_CHASSIS
        self['tooltip'] = ''
        self['name'] = ''
        self['tooltipType'] = ttType
        self['slotType'] = moduleType
        self['removable'] = True
        if vehicleModule is None:
            self['id'] = _SlotVOConstants.UNRESOLVED_LIST_INDEX
            self['tooltipType'] = TOOLTIPS_CONSTANTS.COMPLEX
            if not isDisabledTooltip:
                self['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_EQUIPMENT_EMPTY
            else:
                self['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_EQUIPMENT_DISABLED
            self['moduleLabel'] = _SlotVOConstants.MODULE_LABEL_EMPTY
        else:
            self['id'] = vehicleModule.intCD
            self['removable'] = vehicleModule.isRemovable
            self['moduleLabel'] = vehicleModule.getGUIEmblemID()
            self['name'] = vehicleModule.userName
        return

    def _prepareModule(self, modulesData, vehicle):
        vehicleModule = modulesData[0]
        self['slotIndex'] = 0
        self['level'] = vehicleModule.level
        self[EXTRA_MODULE_INFO] = vehicleModule.getExtraIconInfo(vehicle.descriptor)
        return vehicleModule
