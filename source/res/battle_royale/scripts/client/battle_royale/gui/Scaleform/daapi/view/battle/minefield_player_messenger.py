# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/minefield_player_messenger.py
from battle_royale.gui.battle_control.controllers.progression_ctrl import IProgressionListener
from Event import EventsSubscriber
from gui.battle_control.view_components import IViewComponentsCtrlListener
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from items import vehicles
from battle_royale.gui.constants import BattleRoyaleEquipments
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID

class MinefieldPlayerMessenger(IProgressionListener, IViewComponentsCtrlListener):
    MINEFIELD_INSTALLED_ID = 'MINEFIELD_INSTALLED'
    MINEFIELD_DESTROYED_ID = 'MINEFIELD_DESTROYED'
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(MinefieldPlayerMessenger, self).__init__()
        self.__eventsSubscriber = EventsSubscriber()
        self.__eventsSubscriber.subscribeToEvent(self.__sessionProvider.shared.feedback.onPlayerFeedbackReceived, self._onPlayerFeedbackReceived)
        self.__equipmentCtrl = self.__sessionProvider.shared.equipments
        self.__eventsSubscriber.subscribeToEvent(self.__equipmentCtrl.onCombatEquipmentUsed, self.__onCombatEquipmentUsed)

    def detachedFromCtrl(self, ctrlID):
        super(MinefieldPlayerMessenger, self).detachedFromCtrl(ctrlID)
        self.__eventsSubscriber.unsubscribeFromAllEvents()
        self.__equipmentCtrl = None
        return

    def __onCombatEquipmentUsed(self, shooterID, eqID):
        equipment = vehicles.g_cache.equipments().get(eqID)
        if equipment is None:
            return
        else:
            playerVehID = self.__sessionProvider.getArenaDP().getPlayerVehicleID(True)
            if playerVehID == shooterID and equipment.name == BattleRoyaleEquipments.MINE_FIELD:
                self.__sessionProvider.shared.messages.onShowPlayerMessageByKey(self.MINEFIELD_INSTALLED_ID)
            return

    def _onPlayerFeedbackReceived(self, events):
        for e in events:
            if e.getType() == FEEDBACK_EVENT_ID.EQUIPMENT_TIMER_EXPIRED:
                itemName = self.__equipmentCtrl.getEquipmentNameByID(e.getTargetID())
                if itemName == BattleRoyaleEquipments.MINE_FIELD:
                    self.__sessionProvider.shared.messages.onShowPlayerMessageByKey(self.MINEFIELD_DESTROYED_ID)
                    break
