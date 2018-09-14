# Embedded file name: scripts/client/avatar_helpers/__init__.py
import BigWorld

def getAvatarDatabaseID():
    dbID = 0L
    player = BigWorld.player()
    arena = getattr(player, 'arena', None)
    if arena is not None:
        vehID = getattr(player, 'playerVehicleID', None)
        if vehID is not None and vehID in arena.vehicles:
            dbID = arena.vehicles[vehID]['accountDBID']
    return dbID
