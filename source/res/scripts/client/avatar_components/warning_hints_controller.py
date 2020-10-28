# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/warning_hints_controller.py
import Event
from helpers import dependency
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from skeletons.gui.battle_session import IBattleSessionProvider

class WarningHintsController(object):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.onAuraVictimNotification = Event.Event()
        self.onAuraVictimMarkerIcon = Event.Event()

    def onBecomePlayer(self):
        pass

    def onBecomeNonPlayer(self):
        pass

    def handleKey(self, isDown, key, mods):
        pass

    def showAuraSoulsWarningHint(self):
        self.onAuraVictimNotification(show=True)
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.LOSE_SOULS_IN_AURA, True)

    def showAuraHealthWarningHint(self):
        self.onAuraVictimNotification(show=True)
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.FIRE_WITH_MESSAGE, True)

    def hideAuraWarningHint(self):
        self.onAuraVictimNotification(show=False)
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.FIRE_WITH_MESSAGE, False)
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.LOSE_SOULS_IN_AURA, False)

    def showAuraVictimMarkerIcon(self, vehicleId):
        self.onAuraVictimMarkerIcon(show=True, vehicleId=vehicleId)

    def hideAuraVictimMarkerIcon(self, vehicleId):
        self.onAuraVictimMarkerIcon(show=False, vehicleId=vehicleId)
