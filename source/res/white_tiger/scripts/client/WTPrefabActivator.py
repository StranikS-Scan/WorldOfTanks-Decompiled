# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTPrefabActivator.py
import logging
from items import vehicles
from script_component.DynamicScriptComponent import DynamicScriptComponent
from white_tiger.helpers.PrefabHelper import AppearancePrefabHandler
_logger = logging.getLogger(__name__)

class WTPrefabActivator(DynamicScriptComponent):

    def __init__(self):
        super(WTPrefabActivator, self).__init__()
        self._prefabHandler = AppearancePrefabHandler(self._isAbilityActive)

    @staticmethod
    def getEquipment(equipmentID):
        equipment = vehicles.g_cache.equipments().get(equipmentID)
        if not equipment:
            _logger.warning('No equipment found for id %r', equipmentID)
            return None
        else:
            return equipment

    def onDestroy(self):
        if self._prefabHandler:
            self._prefabHandler.destroy()
        self._prefabHandler = None
        super(WTPrefabActivator, self).onDestroy()
        return

    def _onAvatarReady(self):
        if self._isAbilityActive():
            self._prefabHandler.load(self.entity.appearance, WTPrefabActivator.getEquipment(self.equipmentID).usagePrefab, lambda : None)

    def _isAbilityActive(self):
        raise NotImplementedError()

    def _updatePrefab(self):
        if self._isAbilityActive():
            self._prefabHandler.load(self.entity.appearance, WTPrefabActivator.getEquipment(self.equipmentID).usagePrefab, lambda : None)
        else:
            self._prefabHandler.unload()
