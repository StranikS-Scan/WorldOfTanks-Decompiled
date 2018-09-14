# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/fitting_slot_vo.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.utils import EXTRA_MODULE_INFO, CLIP_ICON_PATH
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from shared_utils import findFirst

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
        if slotId is not None:
            module = findFirst(lambda item: item.isInstalled(vehicle, slotId), modulesData)
            self['slotIndex'] = slotId
        else:
            module = modulesData[0]
            self['slotIndex'] = 0
            self['level'] = module.level
            if slotType == 'vehicleGun' and module.isClipGun(vehicle.descriptor):
                self[EXTRA_MODULE_INFO] = CLIP_ICON_PATH
        if module is None:
            self['id'] = -1
            self['tooltipType'] = TOOLTIPS_CONSTANTS.COMPLEX
            self['moduleLabel'] = 'empty'
            if slotType == FITTING_TYPES.OPTIONAL_DEVICE:
                self['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_DEVICE_EMPTY
            else:
                self['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_EQUIPMENT_EMPTY
        else:
            self['id'] = module.intCD
            self['removable'] = module.isRemovable
            self['moduleLabel'] = module.getGUIEmblemID()
        return
