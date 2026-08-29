# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleInvisibilityModB.py
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import playInvisibilityModBSound
from white_tiger.gui.gui_constants import FEEDBACK_EVENT_ID

class WTVehicleInvisibilityModB(DynamicScriptComponent):

    def __init__(self):
        super(WTVehicleInvisibilityModB, self).__init__()
        self._guiFeedback = self.entity.guiSessionProvider.shared.feedback
        self.__allyIDs = None
        return

    def set_isAbilityActive(self, prev):
        if self.isAbilityActive:
            arena = BigWorld.player().arena
            self.__allyIDs = self.__getAllies(arena, self.entity.team)
            self.__showMarker(True)
            arena.onVehicleKilled += self.__onKilled
            playInvisibilityModBSound()
        else:
            BigWorld.player().arena.onVehicleKilled -= self.__onKilled
            self.__showMarker(False)
            self.__allyIDs = None
        return

    def onDestroy(self):
        self.__allyIDs = None
        super(WTVehicleInvisibilityModB, self).onDestroy()
        return

    def __onKilled(self, victimID, *args):
        if victimID in self.__allyIDs:
            self.__updateMarkerVisibility(victimID, False)

    def __showMarker(self, isShown):
        for aid in self.__allyIDs:
            self.__updateMarkerVisibility(aid, isShown)

    def __updateMarkerVisibility(self, id, isShown):
        self._guiFeedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.WT_INVISIBILITY_MARK, id, {'isShown': isShown})

    def __getAllies(self, arena, team):
        return [ vId for vId, v in arena.vehicles.iteritems() if v['team'] == team ]
