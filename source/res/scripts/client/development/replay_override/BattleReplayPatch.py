# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/development/replay_override/BattleReplayPatch.py
import ResMgr
from Vehicle import Vehicle
from items import vehicles
from BattleReplay import BattleReplay
import ArenaType
from Avatar import PlayerAvatar

class BattleReplayPatch:
    vehicleName = ''
    locationName = ''
    vehicleDescrSource = None
    avatarOnBecomePlayerSource = None
    battleReplayPlaySource = None

    def __init__(self):
        pass

    def patch(self):
        self.readXML()
        self.createVehiclePatch()
        self.createLocationPatch()

    @staticmethod
    def readXML():
        settingsFileName = 'scripts/client/development/replay_override/config.xml'
        settings = ResMgr.openSection(settingsFileName)
        if settings is not None:
            overridables = settings['ReplayOverridables']
            if overridables is not None:
                vehicle = overridables['Vehicle']
                if vehicle is not None:
                    BattleReplayPatch.vehicleName = vehicle.asString
                location = overridables['Location']
                if location is not None:
                    BattleReplayPatch.locationName = location.asString
        return

    @staticmethod
    def createVehiclePatch():
        BattleReplayPatch.vehicleDescrSource = Vehicle.getDescr
        Vehicle.getDescr = overrideVehicleDescr

    @staticmethod
    def createLocationPatch():
        BattleReplayPatch.battleReplayPlaySource = BattleReplay.play
        BattleReplay.play = overridePlay
        BattleReplayPatch.avatarOnBecomePlayerSource = PlayerAvatar.onBecomePlayer
        PlayerAvatar.onBecomePlayer = overrideOnBecomePlayer

    @staticmethod
    def needToOverrideVehicleInReplay():
        if BattleReplay.isPlaying:
            if vehicles.g_list.isVehicleExisting(BattleReplayPatch.vehicleName):
                return True
        return False

    @staticmethod
    def needToOverrideLocationInReplay():
        if BattleReplay.isPlaying:
            if BattleReplayPatch.locationName in ArenaType.g_geometryNamesToIDs:
                return True
        return False


def overrideVehicleDescr(self, respawnCompactDescr):
    if BattleReplayPatch.needToOverrideVehicleInReplay():
        descr = vehicles.VehicleDescr(typeName=BattleReplayPatch.vehicleName)
        return descr
    elif BattleReplayPatch.vehicleDescrSource is not None:
        return BattleReplayPatch.vehicleDescrSource(self, respawnCompactDescr)
    else:
        return 0
        return


def overrideOnBecomePlayer(self):
    if BattleReplayPatch.needToOverrideLocationInReplay():
        self.arenaTypeID = ArenaType.g_geometryNamesToIDs[BattleReplayPatch.locationName]
    if BattleReplayPatch.avatarOnBecomePlayerSource is not None:
        BattleReplayPatch.avatarOnBecomePlayerSource(self)
    return


def overridePlay(self, fileName=None):
    result = False
    if BattleReplayPatch.battleReplayPlaySource is not None:
        result = BattleReplayPatch.battleReplayPlaySource(self, fileName)
    if BattleReplayPatch.needToOverrideLocationInReplay():
        self._BattleReplay__replayCtrl.setLocationNameToOverride(BattleReplayPatch.locationName)
    return result
