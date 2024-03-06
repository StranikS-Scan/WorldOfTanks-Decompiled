# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/battle_control/controllers/equipment_items.py
from constants import EQUIPMENT_STAGES
import ResMgr
from gui.battle_control.controllers.consumables.equipment_ctrl import _ReplayItem, _InspireItem, _RegenerationKitItem, _ActivationError, _StealthRadarItem
from gui.shared.system_factory import registerEquipmentItem
_EQUIPMENT_CONFIG_PATH = 'frontline/scripts/item_defs/vehicles/common/equipments/epic_equipments.xml'

def getEquipmentWorkingResult(item, result, error):
    return (False, _ActivationError('equipmentIsWorking', {'name': item.getDescriptor().userString})) if error is None and item.getStage() == EQUIPMENT_STAGES.DEPLOYING else (result, error)


class _FLStealthRadarItem(_StealthRadarItem):

    def canActivate(self, entityName=None, avatar=None):
        result, error = super(_FLStealthRadarItem, self).canActivate(entityName, avatar)
        return getEquipmentWorkingResult(self, result, error)


class _FLInspireItem(_InspireItem):

    def canActivate(self, entityName=None, avatar=None):
        result, error = super(_FLInspireItem, self).canActivate(entityName, avatar)
        return getEquipmentWorkingResult(self, result, error)


class _FLRegenerationKit(_RegenerationKitItem):

    def canActivate(self, entityName=None, avatar=None):
        result, error = super(_FLRegenerationKit, self).canActivate(entityName, avatar)
        return getEquipmentWorkingResult(self, result, error)


def registerFLEquipmentsItems():
    config = ResMgr.openSection(_EQUIPMENT_CONFIG_PATH)
    equipmentList = {'inspire': _FLInspireItem,
     'fl_regenerationKit': _FLRegenerationKit,
     'stealth_radar': _FLStealthRadarItem}
    for eKey in config.keys():
        for eName, eClass in equipmentList.items():
            if eName in eKey:
                registerEquipmentItem(eKey, eClass, _ReplayItem)
