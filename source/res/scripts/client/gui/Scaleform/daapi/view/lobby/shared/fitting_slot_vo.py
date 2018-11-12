# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/fitting_slot_vo.py
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.utils import EXTRA_MODULE_INFO
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from helpers import dependency
from items import ITEM_TYPES
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore

class _SlotVOConstants(object):
    UNRESOLVED_LIST_INDEX = -1
    MODULE_LABEL_EMPTY = 'empty'
    MODULE_LABEL_EMPTY_BOOSTER = 'emptyBooster'
    MODULE_LABEL_EMPTY_ABILITY = 'emptyAbilitySlot'


class FittingSlotVO(dict):

    def __init__(self, modulesData, vehicle, slotType, slotId=None, tooltipType=None):
        super(FittingSlotVO, self).__init__()
        if slotType == FITTING_TYPES.VEHICLE_TURRET and not vehicle.hasTurrets:
            ttType = ''
        else:
            ttType = tooltipType or TOOLTIPS_CONSTANTS.PREVIEW_MODULE
        vehicleModule = self._prepareModule(modulesData, vehicle, slotType, slotId)
        if slotType == FITTING_TYPES.VEHICLE_CHASSIS:
            if vehicleModule and vehicleModule.isWheeledChassis():
                slotType = FITTING_TYPES.VEHICLE_WHEELED_CHASSIS
        self['tooltip'] = ''
        self['name'] = ''
        self['tooltipType'] = ttType
        self['slotType'] = slotType
        self['removable'] = True
        if vehicleModule is None:
            self['id'] = _SlotVOConstants.UNRESOLVED_LIST_INDEX
            self['tooltipType'] = TOOLTIPS_CONSTANTS.COMPLEX
            if slotType == FITTING_TYPES.OPTIONAL_DEVICE:
                self['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_DEVICE_EMPTY
                self['moduleLabel'] = _SlotVOConstants.MODULE_LABEL_EMPTY
            elif slotType == FITTING_TYPES.BOOSTER:
                self['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_BATTLEBOOSTER_EMPTY
                self['moduleLabel'] = _SlotVOConstants.MODULE_LABEL_EMPTY_BOOSTER
            elif slotType == FITTING_TYPES.BATTLE_ABILITY:
                self['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_BATTLEABILITY_EMPTY
                self['moduleLabel'] = _SlotVOConstants.MODULE_LABEL_EMPTY_ABILITY
            else:
                self['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_EQUIPMENT_EMPTY
                self['moduleLabel'] = _SlotVOConstants.MODULE_LABEL_EMPTY
        else:
            self['id'] = vehicleModule.intCD
            self['removable'] = vehicleModule.isRemovable
            self['moduleLabel'] = vehicleModule.getGUIEmblemID()
            self['name'] = vehicleModule.userName
        self._setNewCounter(vehicleModule, vehicle)
        return

    def _prepareModule(self, modulesData, vehicle, slotType, slotId):
        if slotId is not None:
            vehicleModule = findFirst(lambda item: item.isInstalled(vehicle, slotId), modulesData)
            self['slotIndex'] = slotId
        else:
            vehicleModule = modulesData[0]
            self['slotIndex'] = 0
            self['level'] = vehicleModule.level
            self[EXTRA_MODULE_INFO] = vehicleModule.getExtraIconInfo(vehicle.descriptor)
        return vehicleModule

    def _setNewCounter(self, vehicleModule, vehicle):
        if vehicleModule is None:
            return
        else:
            if vehicleModule.itemTypeID == ITEM_TYPES.vehicleGun and vehicleModule.isAutoReloadable(vehicle.descriptor):
                uiStorage = dependency.instance(ISettingsCore).serverSettings.getUIStorage()
                if not uiStorage.get(UI_STORAGE_KEYS.AUTO_RELOAD_MARK_IS_SHOWN):
                    self['counter'] = 1
            return


class HangarFittingSlotVO(FittingSlotVO):

    def _prepareModule(self, modulesData, vehicle, slotType, slotId):
        if slotId is not None:
            module = findFirst(lambda item: item.isInstalled(vehicle, slotId), modulesData)
            self['slotIndex'] = slotId
            if slotType == FITTING_TYPES.OPTIONAL_DEVICE:
                for battleBooster in vehicle.equipment.battleBoosterConsumables:
                    if battleBooster is not None and battleBooster.isOptionalDeviceCompatible(module):
                        self['highlight'] = True
                        break

                if module is not None and module.isDeluxe():
                    self['bgHighlightType'] = SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS
                else:
                    self['bgHighlightType'] = SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT
            elif slotType == FITTING_TYPES.BOOSTER and module is not None:
                affectsAtTTC = module.isAffectsOnVehicle(vehicle)
                self['affectsAtTTC'] = affectsAtTTC
                if affectsAtTTC:
                    if module.isCrewBooster():
                        isPerkReplace = not module.isAffectedSkillLearnt(vehicle)
                        bgType = SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER_CREW_REPLACE if isPerkReplace else SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER
                        self['bgHighlightType'] = bgType
                    else:
                        self['highlight'] = affectsAtTTC
                        self['bgHighlightType'] = SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER
            elif slotType == FITTING_TYPES.BATTLE_ABILITY:
                self['level'] = 0 if module is None else module.level
        else:
            module = super(HangarFittingSlotVO, self)._prepareModule(modulesData, vehicle, slotType, slotId)
        return module
