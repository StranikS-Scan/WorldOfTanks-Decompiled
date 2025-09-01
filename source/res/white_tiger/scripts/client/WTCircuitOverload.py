# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTCircuitOverload.py
import BigWorld
import Math
import logging
from typing import TYPE_CHECKING
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger_common.wt_constants import WT_FIRE_NOTIFICATION_CIRCUIT_OVERLOAD_BOSS, WT_FIRE_NOTIFICATION_CIRCUIT_OVERLOAD_HARRIER
from white_tiger.gui.wt_event_helpers import isBoss
from white_tiger.helpers.prefab_helpers import PrefabHandlerComponent
if TYPE_CHECKING:
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
_logger = logging.getLogger(__name__)

class WTCircuitOverload(PrefabHandlerComponent, DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _onAvatarReady(self):
        self.createGameObject()

    def onAppearanceReady(self):
        self.setAppearanceReady()

    def createGameObject(self):
        if not self.prefabPath:
            _logger.error('WTCircuitOverload._onAvatarReady: no "prefabPath" specified!')
            return
        vehicle = self.entity
        avatar = BigWorld.player()
        msgCtrl = self.__guiSessionProvider.shared.messages
        vehicleInfo = self.__guiSessionProvider.getCtx().getVehicleInfo(vehicle.id)
        name = vehicleInfo.vehicleType.shortName
        if avatar.vehicle:
            if isBoss(avatar.vehicle.typeDescriptor.type.tags):
                key = WT_FIRE_NOTIFICATION_CIRCUIT_OVERLOAD_BOSS
            else:
                key = WT_FIRE_NOTIFICATION_CIRCUIT_OVERLOAD_HARRIER
        msgCtrl.onShowPlayerMessageByKey(key, {'name': name})
        self.loadGameObject(self.entity, self.prefabPath, vehicle.entityGameObject, Math.Vector3(0, 0, 0))

    def _onGameObjectLoaded(self, gameObject):
        self._gameObject = gameObject

    def onDestroy(self):
        self.destroyGameObject()
        super(WTCircuitOverload, self).onDestroy()
