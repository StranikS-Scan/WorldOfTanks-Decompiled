# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/personal_death_zones_gui_ctrl.py
import BigWorld
import weakref
from Event import EventManager, Event
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import PersonalDeathZone

class PersonalDeathZonesGUIController(IBattleController):

    def __init__(self):
        super(PersonalDeathZonesGUIController, self).__init__()
        self.__eManager = EventManager()
        self.onPlayerEnteredDeathZone = Event(self.__eManager)
        self.onPlayerLeftDeathZone = Event(self.__eManager)
        self._deathZones = dict()

    def startControl(self, *args):
        pass

    def stopControl(self):
        self.onPlayerEnteredDeathZone.clear()
        self.onPlayerLeftDeathZone.clear()
        self._deathZones.clear()

    def getControllerID(self):
        return BATTLE_CTRL_ID.PERSONAL_DEATH_ZONES_GUI_CTRL

    @property
    def enteredDeathZones(self):
        return self._deathZones

    def onPlayerEntered(self, deathZone):
        self._deathZones[deathZone.id] = weakref.proxy(deathZone)
        self._updateWarningNotification()
        self.onPlayerEnteredDeathZone(deathZone)

    def onPlayerLeft(self, deathZone):
        if self._deathZones.pop(deathZone.id, None):
            self._updateWarningNotification()
            self.onPlayerLeftDeathZone(deathZone)
        return

    def _updateWarningNotification(self):
        zone = min(self._deathZones.itervalues(), key=lambda d: d.adjustedDelay) if self._deathZones else None
        zoneViewStateParams = (zone is not None, zone.delay if zone else 0, zone.launchTime if zone else 0)
        BigWorld.player().updatePersonalDeathZoneWarningNotification(*zoneViewStateParams)
        return
