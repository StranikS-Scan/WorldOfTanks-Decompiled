# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/shared/events.py
from gui.shared.event_bus import SharedEvent

class BotOwnershipEvent(SharedEvent):
    OWNERSHIP_STATE_CHANGED = 'grinch/onOwnershipStateChanged'

    def __init__(self, eventType, slavesLimit, slavesCount):
        super(BotOwnershipEvent, self).__init__(eventType)
        self.slavesLimit = slavesLimit
        self.slavesCount = slavesCount


class StackableEquipmentUpdateEvent(SharedEvent):
    STACKABLE_EQUIPMENT_UPDATED = 'grinch/onStackableEquipmentUpdated'

    def __init__(self, eventType, stacks, reloadTimeLeft, reloadTime):
        super(StackableEquipmentUpdateEvent, self).__init__(eventType)
        self.stacks = stacks
        self.reloadTimeLeft = reloadTimeLeft
        self.reloadTime = reloadTime


class FlareAbilityEvent(SharedEvent):
    FLARE_MARK = 'grinch/flareMarked'

    def __init__(self, eventType, vehicleID, isOn):
        super(FlareAbilityEvent, self).__init__(eventType)
        self.vehicleID = vehicleID
        self.isOn = isOn


class TurretDeployEvent(SharedEvent):
    TURRET_DEPLOY_TIME_CHANGED = 'grinch/onTurretDeployUpdated'

    def __init__(self, eventType, deployTimeLeft, vehicleID):
        super(TurretDeployEvent, self).__init__(eventType)
        self.deployTimeLeft = deployTimeLeft
        self.vehicleID = vehicleID


class RageAbilityEvent(SharedEvent):
    VEHICLE_STATUS_CHANGED = 'grinch/vehicleUndeadStatus'

    def __init__(self, eventType, vehicleUndeadStatus, vehicleID):
        super(RageAbilityEvent, self).__init__(eventType)
        self.vehicleUndeadStatus = vehicleUndeadStatus
        self.vehicleID = vehicleID


class HomebaseMarkerEvent(SharedEvent):
    HOMEBASE_MARKER_UPDATE = 'grinch/homebaseMarkerUpdate'

    def __init__(self, eventType, team, matrix):
        super(HomebaseMarkerEvent, self).__init__(eventType)
        self.team = team
        self.matrix = matrix
