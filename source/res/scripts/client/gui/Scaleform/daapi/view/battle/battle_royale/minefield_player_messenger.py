# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/minefield_player_messenger.py
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.progression_ctrl import IProgressionListener
from gui.battle_control.view_components import IViewComponentsCtrlListener
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from items import vehicles
from gui.battle_royale.constants import SteelHunterEquipmentNames
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID

class MinefieldPlayerMessenger(IProgressionListener, IViewComponentsCtrlListener):
    MINEFIELD_INSTALLED_ID = 'MINEFIELD_INSTALLED'
    MINEFIELD_DESTROYED_ID = 'MINEFIELD_DESTROYED'
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(MinefieldPlayerMessenger, self).__init__()
        arena = avatar_getter.getArena()
        if arena is not None:
            arena.onCombatEquipmentUsed += self.__onCombatEquipmentUsed
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onPlayerFeedbackReceived += self._onPlayerFeedbackReceived
        self.__equipmentCtrl = self.__sessionProvider.shared.equipments
        return

    def detachedFromCtrl(self, ctrlID):
        super(MinefieldPlayerMessenger, self).detachedFromCtrl(ctrlID)
        arena = avatar_getter.getArena()
        arena.onCombatEquipmentUsed -= self.__onCombatEquipmentUsed
        ctrl = self.__sessionProvider.shared.feedback
        ctrl.onPlayerFeedbackReceived -= self._onPlayerFeedbackReceived
        self.__equipmentCtrl = None
        return

    def __onCombatEquipmentUsed(self, shooterID, eqID):
        equipment = vehicles.g_cache.equipments().get(eqID)
        if equipment is None:
            return
        else:
            playerVehID = self.__sessionProvider.getArenaDP().getPlayerVehicleID(True)
            if playerVehID == shooterID and equipment.name == SteelHunterEquipmentNames.MINE_FIELD:
                self.__sessionProvider.shared.messages.onShowPlayerMessageByKey(self.MINEFIELD_INSTALLED_ID)
            return

    def _onPlayerFeedbackReceived(self, events):
        for e in events:
            if e.getType() == FEEDBACK_EVENT_ID.EQUIPMENT_TIMER_EXPIRED:
                itemName = self.__equipmentCtrl.getEquipmentNameByID(e.getTargetID())
                if itemName == SteelHunterEquipmentNames.MINE_FIELD:
                    self.__sessionProvider.shared.messages.onShowPlayerMessageByKey(self.MINEFIELD_DESTROYED_ID)
                    break
