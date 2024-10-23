# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VisualScriptEquipmentPublic.py
from constants import EQUIPMENT_STAGES as STAGES
from VisualScriptEquipment import VisualScriptEquipment
from helpers.fixed_dict import getVisualScriptEquipmentPublicState
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class VisualScriptEquipmentPublic(VisualScriptEquipment):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(VisualScriptEquipmentPublic, self).__init__()
        self.__isDestroyed = False

    def _onAvatarReady(self):
        super(VisualScriptEquipmentPublic, self)._onAvatarReady()
        self.set_equipmentStatePublic()

    def set_equipmentStatePublic(self, _=None):
        if self._context is None:
            return
        elif self.__isDestroyed and self.__sessionProvider.arenaVisitor.gui.isWhiteTigerBattle():
            return
        else:
            if not self.entity.isMyVehicle:
                state = getVisualScriptEquipmentPublicState(self.equipmentStatePublic)
                if state.stage != state.prevStage:
                    getattr(self._context, STAGES.toString(state.stage))()
            return

    def onDestroy(self):
        super(VisualScriptEquipmentPublic, self).onDestroy()
        self.__isDestroyed = True
