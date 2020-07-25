# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/fitting_slot_vo.py
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.utils import EXTRA_MODULE_INFO
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from helpers import dependency
from items import ITEM_TYPES
from skeletons.account_helpers.settings_core import ISettingsCore

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
        self._setNewCounter(vehicleModule, vehicle)
        return

    def _prepareModule(self, modulesData, vehicle):
        vehicleModule = modulesData[0]
        self['slotIndex'] = 0
        self['level'] = vehicleModule.level
        self[EXTRA_MODULE_INFO] = vehicleModule.getExtraIconInfo(vehicle.descriptor)
        return vehicleModule

    def _setNewCounter(self, vehicleModule, vehicle):
        if vehicleModule is None:
            return
        else:
            if vehicleModule.itemTypeID == ITEM_TYPES.vehicleGun:
                if vehicleModule.isAutoReloadable(vehicle.descriptor):
                    uiStorage = dependency.instance(ISettingsCore).serverSettings.getUIStorage()
                    if not uiStorage.get(UI_STORAGE_KEYS.AUTO_RELOAD_MARK_IS_SHOWN):
                        self['counter'] = 1
                if vehicleModule.isDualGun(vehicle.descriptor):
                    uiStorage = dependency.instance(ISettingsCore).serverSettings.getUIStorage()
                    if not uiStorage.get(UI_STORAGE_KEYS.DUAL_GUN_MARK_IS_SHOWN):
                        if 'counter' in self:
                            self['counter'] += 3
                        else:
                            self['counter'] = 3
            if vehicleModule.itemTypeID == ITEM_TYPES.vehicleEngine:
                if vehicleModule.hasTurboshaftEngine():
                    uiStorage = dependency.instance(ISettingsCore).serverSettings.getUIStorage()
                    if not uiStorage.get(UI_STORAGE_KEYS.TURBOSHAFT_MARK_IS_SHOWN):
                        self['counter'] = self.get('counter', 0) + 1
            return
