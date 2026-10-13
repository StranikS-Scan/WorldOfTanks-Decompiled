# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/shared/events.py
from __future__ import absolute_import
from gui.shared.event_bus import SharedEvent

class CapturePointEvent(SharedEvent):
    INIT_CAPTURABLE_POINT = 'fortRush/initCapturablePoint'
    CAPTURABLE_POINT_UPDATE = 'fortRush/capturableBaseUpdate'

    def __init__(self, eventType, capturablePointName=None, totalInvaders=None, invadersTeam=None, ownersTeam=None, isContested=None, captureProgressPercent=None, state=None, transform=None, numberOfAttackers=None, isNeutralizing=None, uid=-1):
        super(CapturePointEvent, self).__init__(eventType)
        self.capturablePointName = capturablePointName
        self.totalInvaders = totalInvaders
        self.invadersTeam = invadersTeam
        self.ownersTeam = ownersTeam
        self.isContested = isContested
        self.captureProgressPercent = captureProgressPercent
        self.state = state
        self.transform = transform
        self.numberOfAttackers = numberOfAttackers
        self.isNeutralizing = isNeutralizing
        self.uid = uid


class CaptureInvaderEvent(SharedEvent):
    INVADER_ADDED = 'fortRush/captureInvaderAdded'
    INVADER_REMOVED = 'fortRush/captureInvaderRemoved'

    def __init__(self, eventType, vehicleID, baseName=''):
        super(CaptureInvaderEvent, self).__init__(eventType)
        self.vehicleID = vehicleID
        self.baseName = baseName


class RespawnCtrlEvent(SharedEvent):
    SHOW_SPAWN_POINTS = 'game/showSpawnPoints'
    HIDE_SPAWN_POINTS = 'game/hideSpawnPoints'
