# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/SupplyResurrectComponent.py
import BigWorld
import CGF
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from supply_shared import Supply
SUPPLY_TYPE_TO_PREFAB = {Supply.FLAMER: 'content/CGFPrefabs/Frontline/FlamerHeal.prefab',
 Supply.PILLBOX: 'content/CGFPrefabs/Frontline/PillboxHeal.prefab',
 Supply.MORTAR: 'content/CGFPrefabs/Frontline/MortarHeal.prefab'}

class SupplyResurrectComponent(DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(SupplyResurrectComponent, self).__init__()
        self.__gameObject = None
        self.__updateTimerCb = None
        self.start()
        supplyType = Supply.getSupplyType(self.entity.typeDescriptor.type.tags)
        if supplyType is not None:
            CGF.loadGameObject(SUPPLY_TYPE_TO_PREFAB[supplyType], self.entity.spaceID, self.entity.position, self._healAnimGO)
        return

    def onDestroy(self):
        self.stop()
        super(SupplyResurrectComponent, self).onDestroy()

    def start(self):
        if self.__updateTimerCb is None:
            self.__updateTimerCb = BigWorld.callback(0.2, self.__updateTimer)
        return

    def __updateTimer(self):
        self.__updateTimerCb = None
        duration = self.finishTimeRepair - BigWorld.serverTime()
        self.__guiSessionProvider.shared.feedback.invalidateFLSupplyRepairTimer(self.entity.id, duration)
        return

    def stop(self):
        self.__guiSessionProvider.shared.feedback.invalidateFLSupplyRepairTimer(self.entity.id, 0)
        if self.__updateTimerCb:
            BigWorld.cancelCallback(self.__updateTimerCb)
            self.__updateTimerCb = None
        if self.__gameObject is not None:
            CGF.removeGameObject(self.__gameObject)
        return

    def _healAnimGO(self, go):
        self.__gameObject = go
