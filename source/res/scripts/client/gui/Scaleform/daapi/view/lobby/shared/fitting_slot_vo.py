# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/fitting_slot_vo.py
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.utils import EXTRA_MODULE_INFO, CLIP_ICON_PATH, HYDRAULIC_ICON_PATH
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from shared_utils import findFirst

class _SlotVOConstants(object):
    UNRESOLVED_LIST_INDEX = -1
    MODULE_LABEL_EMPTY = 'empty'
    MODULE_LABEL_EMPTY_BOOSTER = 'emptyBooster'


class FittingSlotVO(dict):
    """
    class presents VO for displaying installed optional devices or modules in AmmunitionPanel and ModulesPanel
    """

    def __init__(self, modulesData, vehicle, slotType, slotId=None, tooltipType=None):
        """
        Args:
            modulesData: list of modules, installed in current slot type. There is always one element for vehicle
                         modules and zero to three for optional devices and equipments. If there's no corresponding
                         artifact in slot, empty icon is displayed
            vehicle: vehicle for which slot is display
            slotType: type of slot from FITTING_TYPES
            slotId: id of slot, None for modules and 0..2 for optional devices and equipments
            tooltipType: GUI constant defining tooltip type, one of TOOLTIPS_CONSTANTS
        """
        super(FittingSlotVO, self).__init__()
        if slotType == FITTING_TYPES.VEHICLE_TURRET and not vehicle.hasTurrets:
            ttType = ''
        else:
            ttType = tooltipType or TOOLTIPS_CONSTANTS.PREVIEW_MODULE
        self['tooltip'] = ''
        self['tooltipType'] = ttType
        self['slotType'] = slotType
        self['removable'] = True
        module = self._prepareModule(modulesData, vehicle, slotType, slotId)
        if module is None:
            self['id'] = _SlotVOConstants.UNRESOLVED_LIST_INDEX
            self['tooltipType'] = TOOLTIPS_CONSTANTS.COMPLEX
            if slotType == FITTING_TYPES.OPTIONAL_DEVICE:
                self['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_DEVICE_EMPTY
                self['moduleLabel'] = _SlotVOConstants.MODULE_LABEL_EMPTY
            elif slotType == FITTING_TYPES.BOOSTER:
                self['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_BATTLEBOOSTER_EMPTY
                self['moduleLabel'] = _SlotVOConstants.MODULE_LABEL_EMPTY_BOOSTER
            else:
                self['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_EQUIPMENT_EMPTY
                self['moduleLabel'] = _SlotVOConstants.MODULE_LABEL_EMPTY
        else:
            self['id'] = module.intCD
            self['removable'] = module.isRemovable
            self['moduleLabel'] = module.getGUIEmblemID()
        return

    def _prepareModule(self, modulesData, vehicle, slotType, slotId):
        if slotId is not None:
            module = findFirst(lambda item: item.isInstalled(vehicle, slotId), modulesData)
            self['slotIndex'] = slotId
        else:
            module = modulesData[0]
            self['slotIndex'] = 0
            self['level'] = module.level
            if slotType == 'vehicleGun' and module.isClipGun(vehicle.descriptor):
                self[EXTRA_MODULE_INFO] = CLIP_ICON_PATH
            elif slotType == 'vehicleChassis' and module.isHydraulicChassis():
                self[EXTRA_MODULE_INFO] = HYDRAULIC_ICON_PATH
        return module


class HangarFittingSlotVO(FittingSlotVO):

    def _prepareModule(self, modulesData, vehicle, slotType, slotId):
        if slotId is not None:
            module = findFirst(lambda item: item.isInstalled(vehicle, slotId), modulesData)
            self['slotIndex'] = slotId
            if slotType == FITTING_TYPES.OPTIONAL_DEVICE:
                if vehicle.battleBooster is not None and vehicle.battleBooster.isOptionalDeviceCompatible(module):
                    self['highlight'] = True
                if module is not None and module.isDeluxe():
                    self['bgHighlightType'] = SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS
                else:
                    self['bgHighlightType'] = SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT
        elif slotType == FITTING_TYPES.BOOSTER:
            module = vehicle.battleBooster
            if module is not None:
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
        else:
            module = super(HangarFittingSlotVO, self)._prepareModule(modulesData, vehicle, slotType, slotId)
        return module
