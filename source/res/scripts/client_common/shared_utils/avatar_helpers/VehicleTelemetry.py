# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/shared_utils/avatar_helpers/VehicleTelemetry.py
import cPickle
import zlib
import math
import os.path
import datetime
import ResMgr
from debug_utils import LOG_WARNING, LOG_ERROR, LOG_CODEPOINT_WARNING
from constants import ENABLE_DEBUG_DYNAMICS_INFO
from physics_shared import G

class VehicleTelemetry(object):

    def __init__(self, avatar):
        self.avatar = avatar
        self.logName = None
        self.saveTextLog = False
        self.dynamicsLog = None
        self.dynamicsData = {}
        self.scenarioName = None
        self.recordStarted = False
        self.__physicsDebugInfoEnabled = ENABLE_DEBUG_DYNAMICS_INFO
        self.__physicsDebugInfo = None
        self.__completionFlag = None
        return

    physicsDebugInfo = property(lambda self: self.__physicsDebugInfo)

    def enableVehiclePhysicsTelemetry(self, enabled=None):
        if not self.avatar.inWorld:
            return
        else:
            shouldEnable = enabled if enabled is not None else not self.__physicsDebugInfoEnabled
            flag = 1 if shouldEnable else 0
            self.avatar.base.setDevelopmentFeature(0, 'toggle_vehicle_debug_info', flag, '')
            self.__physicsDebugInfoEnabled = shouldEnable
            return

    try:
        DYNAMICS_LOG_DIR = ResMgr.appDirectory() + '../dynamics_log'
    except AttributeError:
        DYNAMICS_LOG_DIR = 'dynamics_log'

    def __checkDynLogDir(self):
        if not os.path.exists(VehicleTelemetry.DYNAMICS_LOG_DIR):
            LOG_WARNING('DYNAMICS_LOG_DIR not found, creating ...', VehicleTelemetry.DYNAMICS_LOG_DIR)
            os.mkdir(VehicleTelemetry.DYNAMICS_LOG_DIR)

    NAME_DELIMITER = '$'

    def __generateDynamicsLogName(self):
        vehicleName = self.avatar.getVehicleAttached().typeDescriptor.name
        vehicleName = vehicleName.replace(':', VehicleTelemetry.NAME_DELIMITER)
        timestamp = datetime.datetime.now().strftime('%y%m%d%H%M%S')
        logName = VehicleTelemetry.NAME_DELIMITER.join((vehicleName, self.scenarioName, timestamp))
        return logName

    def recordVehicleDynamics(self, scenarioName, cmd, rapidModeSpeedup=1, saveTextLog=False):
        if not self.avatar.inWorld:
            LOG_WARNING('Avatar.base is not available yet on Avatar client')
            LOG_CODEPOINT_WARNING()
            return
        self.scenarioName = scenarioName
        self.saveTextLog = saveTextLog
        self.logName = self.__generateDynamicsLogName()
        cmd = cmd.strip()
        zippedArg = zlib.compress(cPickle.dumps((rapidModeSpeedup, cmd)), 9)
        self.__completionFlag = False
        self.avatar.base.setDevelopmentFeature(0, 'record_vehicle_dynamics', 0, zippedArg)

    def isSimulationComplete(self):
        return self.__completionFlag

    def __openDynamicsLog(self, refTime, refDist):
        self.__checkDynLogDir()
        if self.dynamicsLog:
            self.__closeDynamicsLog()
        self.logPath = os.path.join(VehicleTelemetry.DYNAMICS_LOG_DIR, self.logName)
        self.refTime = refTime
        self.refDist = refDist
        if self.saveTextLog:
            self.dynamicsLog = open(self.logPath, 'w')
            self.__writeHeader()

    HEADER_TEMPLATE = '# vehicle : {}\n# engine  : {}\n# chassis : {}\n# scenario: {}\n#  time    distance    Vz      Vx        Az       Ax      X        Y       Z         w        wcc     yaw      pitch     roll     r   health\n'

    def __writeHeader(self):
        descr = self.avatar.getVehicleAttached().typeDescriptor
        header = VehicleTelemetry.HEADER_TEMPLATE.format(descr.name, descr.engine.name, descr.chassis.name, self.scenarioName)
        self.dynamicsLog.write(header)

    def __closeDynamicsLog(self):
        if self.dynamicsLog:
            self.dynamicsLog.close()
            self.dynamicsLog = None
            os.rename(self.logPath, self.logPath + '.log')
        if self.dynamicsData:
            dataFileName = '{}.pkl'.format(self.logName)
            with open(os.path.join(VehicleTelemetry.DYNAMICS_LOG_DIR, dataFileName), 'wb') as dataFile:
                cPickle.dump(self.dynamicsData, dataFile, protocol=2)
        self.dynamicsData = {}
        self.refTime = None
        self.refDist = None
        self.recordStarted = False
        return

    def __onStop(self):
        self.__closeDynamicsLog()
        self.__completionFlag = True

    LOG_LINE_TEMPLATE = ' '.join(('{t:8.3f} {dist:8.3f}', '{Vz:8.3f} {Vx:8.3f}', '{Az:8.3f} {Ax:8.3f}', '{X:8.3f} {Y:8.3f} {Z:8.3f}', '{w:8.3f} {wcc:8.3f}', '{yaw:8.3f} {pitch:8.3f} {roll:8.3f}', '{r:8.3f} {health:4d}', '{ltr:8.3f} {rtr:8.3f}', '{ltp:8.3f} {rtp:8.3f}', '{lte:8.3f} {rte:8.3f}', '{hle:8.3f}', '{dhh:8.3f} {dlt:8.3f} {drt:8.3f}', '{hdm:8.3f} {hrc:8.3f}', '{lthp:8.3f} {rthp:8.3f}', '{Vy:8.3f} {Ay:8.3f}', '{ltslp:8.3f} {rtslp:8.3f}', '{ltbf:8.3f} {rtbf:8.3f}', '\n'))

    def __logDynamics(self, paramNamesMap, snapshots):
        namesMap = paramNamesMap

        def getSnapshotValue(snapshot, parameterName, default=0.0):
            return snapshot[namesMap[parameterName]] if namesMap.has_key(parameterName) else default

        snapshot = None
        for snapshot in snapshots:
            time = snapshot[namesMap['time']] - self.refTime
            if time < 0:
                print 'Nt:', snapshot[namesMap['time']], self.refTime
            dist = snapshot[namesMap['path']] - self.refDist
            velocity = snapshot[namesMap['vel']]
            acceleration = snapshot[namesMap['acc']]
            position = snapshot[namesMap['pos']]
            pitch = -math.degrees(snapshot[namesMap['dir']][1])
            roll = math.degrees(snapshot[namesMap['dir']][2])
            yaw = math.degrees(snapshot[namesMap['dir']][0])
            angularVelocity = math.degrees(snapshot[namesMap['wel']].y)
            angularAcceleration = math.degrees(snapshot[namesMap['wac']].y)
            binormal = (acceleration * velocity).length
            r = abs(velocity.length ** 3 / binormal) if abs(binormal) > 0 else 0
            r = min(500, r)
            velocity *= 3.6
            acceleration *= 1 / G
            data = {'t': time,
             'dist': dist,
             'Vz': velocity.z,
             'Vx': velocity.x,
             'Az': acceleration.z,
             'Ax': acceleration.x,
             'X': position.x,
             'Y': position.y,
             'Z': position.z,
             'w': angularVelocity,
             'wcc': angularAcceleration,
             'yaw': yaw,
             'pitch': pitch,
             'roll': roll,
             'r': r,
             'health': int(self.avatar.getVehicleAttached().health),
             'ltr': getSnapshotValue(snapshot, 'lTrackReaction'),
             'rtr': getSnapshotValue(snapshot, 'rTrackReaction'),
             'ltp': getSnapshotValue(snapshot, 'lTrackPressure'),
             'rtp': getSnapshotValue(snapshot, 'rTrackPressure'),
             'lte': getSnapshotValue(snapshot, 'lTrackEnergy'),
             'rte': getSnapshotValue(snapshot, 'rTrackEnergy'),
             'hle': getSnapshotValue(snapshot, 'hullEnergy'),
             'dhh': getSnapshotValue(snapshot, 'dmg_hh'),
             'dlt': getSnapshotValue(snapshot, 'dmg_lt'),
             'drt': getSnapshotValue(snapshot, 'dmg_rt'),
             'lthp': getSnapshotValue(snapshot, 'lthp'),
             'rthp': getSnapshotValue(snapshot, 'rthp'),
             'hdm': getSnapshotValue(snapshot, 'hull_dmgmp'),
             'hrc': getSnapshotValue(snapshot, 'hull_react'),
             'Vy': velocity.y,
             'Ay': acceleration.y,
             'ltslp': getSnapshotValue(snapshot, 'lTrackScrolling', default=-20.0),
             'rtslp': getSnapshotValue(snapshot, 'rTrackScrolling', default=-30.0),
             'ltbf': getSnapshotValue(snapshot, 'ltbf'),
             'rtbf': getSnapshotValue(snapshot, 'rtbf')}
            for key, value in data.iteritems():
                self.dynamicsData.setdefault(key, []).append(value)

            line = VehicleTelemetry.LOG_LINE_TEMPLATE.format(**data)
            if self.saveTextLog:
                self.dynamicsLog.write(line)
                self.dynamicsLog.flush()

        return

    def receivePhysicsDebugInfo(self, info, modifDict):
        infoDict = cPickle.loads(zlib.decompress(info))
        cmd = infoDict['cmd']
        if cmd == 'telemetry':
            nDict = {}
            for key, value in modifDict.iteritems():
                try:
                    index = infoDict['paramNamesMap'][key]
                    nDict[index] = value
                except Exception:
                    pass

            temp = []
            ind = 0
            for inValue in infoDict['snapshots'][0]:
                mValue = nDict.get(ind, None)
                if mValue is not None:
                    temp.append(mValue)
                else:
                    temp.append(inValue)
                ind += 1

            infoDict['snapshots'][0] = temp
            if self.recordStarted:
                self.__logDynamics(infoDict['paramNamesMap'], infoDict['snapshots'])
            self.__physicsDebugInfo = infoDict
        elif cmd == 'comment':
            if self.dynamicsLog:
                line = '#%(text)s\n' % infoDict
                self.dynamicsLog.write(line)
        elif cmd == 'openLog':
            self.recordStarted = True
            self.__openDynamicsLog(infoDict['time'], infoDict['path'])
        elif cmd == 'closeLog':
            self.__closeDynamicsLog()
        elif cmd == 'stop':
            self.__onStop()
        else:
            LOG_ERROR('Invalid PhysicsDebugInfo has been received:', infoDict)
        return
