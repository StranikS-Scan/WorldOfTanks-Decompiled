# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/vehicle_common.py
import BigWorld
from visual_script import ASPECT
from visual_script.dependency import dependencyImporter
from visual_script.tunable_event_block import TunableEventBlock
TriggersManager = dependencyImporter('TriggersManager')
edgeCases = {'track': ('leftTrack', 'rightTrack'),
 'radioman': ('radioman1', 'radioman2'),
 'gunner': ('gunner1', 'gunner2'),
 'loader': ('loader1', 'loader2'),
 'wheel': ('wheel0', 'wheel1', 'wheel2', 'wheel3', 'wheel4', 'wheel5', 'wheel6', 'wheel7')}

def getPartNames(originalPartName):
    return edgeCases.get(originalPartName, (originalPartName,))


def getPartName(originalPartName):
    for name, names in edgeCases.items():
        if originalPartName in names:
            return name

    return originalPartName


def getPartState(originalPartName):
    available = getPartNames(originalPartName)
    deviceStates = BigWorld.player().deviceStates
    states = [ deviceStates.get(name, 'normal') for name in available ]
    if 'destroyed' in states:
        return 2
    return 1 if 'critical' in states else 0


class TriggerListener(TriggersManager.ITriggerListener):

    def __init__(self, *args, **kwargs):
        super(TriggerListener, self).__init__()

    def destroy(self):
        self.unsubscribe()

    def subscribe(self):
        TriggersManager.g_manager.addListener(self)

    def unsubscribe(self):
        TriggersManager.g_manager.delListener(self)

    def onTriggerActivated(self, params):
        triggerType = params.get('type')
        if triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_OBSERVED:
            self.onPlayerDetected(True)
        elif triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_SHOOT:
            aimingInfo = params['aimingInfo']
            self.onPlayerShoot(aimingInfo)
        elif triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_MISSED:
            self.onPlayerShotMissed()
        elif triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_IN_FIRE:
            self.onPlayerVehicleFireEvent(True)
        elif triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_TANKMAN_SHOOTED:
            tankmanName = params['tankmanName']
            isHealed = params['isHealed']
            self.onPlayerVehicleTankmanEvent(tankmanName, not isHealed)
        elif triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_DEVICE_CRITICAL:
            deviceName = params['deviceName']
            isCritical = params['isCriticalNow']
            isRepaired = params['isRepaired']
            self.onPlayerVehicleDeviceEvent(deviceName, isCritical, not isRepaired)
        elif triggerType == TriggersManager.TRIGGER_TYPE.VEHICLE_VISUAL_VISIBILITY_CHANGED:
            isVisible = params['isVisible']
            targetId = params['vehicleId']
            vehicle = BigWorld.entities.get(targetId)
            if vehicle is not None and vehicle.publicInfo['team'] != BigWorld.player().team:
                if isVisible:
                    self.onPlayerDetectEnemy([vehicle], [])
                else:
                    self.onPlayerDetectEnemy([], [vehicle])
        elif triggerType == TriggersManager.TRIGGER_TYPE.AREA:
            self.onPlayerEnterTrigger(params['name'], True)
        elif triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_MOVE:
            self.onPlayerMove(params['moveCommands'])
        return

    def onTriggerDeactivated(self, params):
        triggerType = params.get('type')
        if triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_OBSERVED:
            self.onPlayerDetected(False)
        elif triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_IN_FIRE:
            self.onPlayerVehicleFireEvent(False)
        elif triggerType == TriggersManager.TRIGGER_TYPE.AREA:
            self.onPlayerEnterTrigger(params['name'], False)

    def onPlayerShoot(self, aimInfo):
        pass

    def onPlayerShotMissed(self):
        pass

    def onPlayerDetectEnemy(self, new, lost):
        pass

    def onPlayerDetected(self, isDetected):
        pass

    def onPlayerVehicleFireEvent(self, isStart):
        pass

    def onPlayerVehicleTankmanEvent(self, tankmanName, isHit):
        pass

    def onPlayerVehicleDeviceEvent(self, deviceName, isCritical, isHit):
        pass

    def onPlayerEnterTrigger(self, trigger, enter):
        pass

    def onPlayerMove(self, modeCommands):
        pass

    def onAutoAim(self, isOn):
        pass


class TunablePlayerVehicleEventBlock(TunableEventBlock, TriggerListener):

    def onStartScript(self):
        self.subscribe()

    def onFinishScript(self):
        self.unsubscribe()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]
