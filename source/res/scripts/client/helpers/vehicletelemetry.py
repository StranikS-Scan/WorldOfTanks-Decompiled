# Embedded file name: scripts/client/helpers/VehicleTelemetry.py
import cPickle
import zlib
import math
import threading
import os.path
import datetime
from debug_utils import *
from constants import ENABLE_DEBUG_DYNAMICS_INFO
from physics_shared import G

class VehicleTelemetry:

    def __init__(self, avatar):
        raise avatar is not None or AssertionError
        self.avatar = avatar
        self.dynamicsLog = None
        self.dynamicsLogKey = None
        self.__physicsDebugInfoEnabled = ENABLE_DEBUG_DYNAMICS_INFO
        self.__physicsDebugInfo = None
        self.__completionFlag = None
        return

    physicsDebugInfo = property(lambda self: self.__physicsDebugInfo)

    def enableVehiclePhysicsTelemetry(self, enabled = None):
        shouldEnable = enabled if enabled is not None else not self.__physicsDebugInfoEnabled
        flag = 1 if shouldEnable else 0
        self.avatar.base.setDevelopmentFeature('toggle_vehicle_debug_info', flag, '')
        self.__physicsDebugInfoEnabled = shouldEnable
        return

    DYNAMICS_LOG_DIR = 'dynamics_log'

    def __checkDynLogDir(self):
        if not os.path.exists(VehicleTelemetry.DYNAMICS_LOG_DIR):
            LOG_WARNING('DYNAMICS_LOG_DIR not found, creating ...', VehicleTelemetry.DYNAMICS_LOG_DIR)
            os.mkdir(VehicleTelemetry.DYNAMICS_LOG_DIR)

    def __getScenarioFilePath(self, scenarioName):
        self.__checkDynLogDir()
        scenarioPath = os.path.join(VehicleTelemetry.DYNAMICS_LOG_DIR, scenarioName)
        if not os.path.exists(scenarioPath):
            LOG_ERROR('SCENARIO file not found:', scenarioPath)
            return None
        else:
            return scenarioPath

    NAME_DELIMITER = '$'

    def __generateDynamicsLogName(self, scenarioName):
        vname = self.avatar.vehicle.typeDescriptor.name
        vname = vname.replace(':', VehicleTelemetry.NAME_DELIMITER)
        sname = scenarioName.split('.', 1)[0]
        stamp = datetime.datetime.now().strftime('%y%m%d%H%M%S')
        logName = VehicleTelemetry.NAME_DELIMITER.join((vname, sname, stamp))
        return logName

    def recordVehicleDynamics(self, scenarioName, isRapidMode = True):
        cmd = ''
        scenarioPath = self.__getScenarioFilePath(scenarioName)
        if not scenarioPath:
            return
        scenario = open(scenarioPath, 'r')
        try:
            cmd = scenario.read()
        finally:
            scenario.close()

        self.logName = self.__generateDynamicsLogName(scenarioName)
        cmd = cmd.strip()
        zippedArg = zlib.compress(cPickle.dumps((isRapidMode, cmd)), 9)
        self.__completionFlag = False
        self.avatar.base.setDevelopmentFeature('record_vehicle_dynamics', 0, zippedArg)

    def isSimulationComplete(self):
        return self.__completionFlag

    def __openDynamicsLog(self, key, refTime, refDist):
        if self.dynamicsLog:
            self.closeDynamicsLog()
        name = VehicleTelemetry.NAME_DELIMITER.join((self.logName, key))
        self.logPath = os.path.join(VehicleTelemetry.DYNAMICS_LOG_DIR, name)
        raise not os.path.exists(self.logPath) or AssertionError
        self.dynamicsLog = open(self.logPath, 'w')
        self.refTime = refTime
        self.refDist = refDist
        self.__writeHeader(name)

    HEADER_TMPL = '\n# vehicle : %(Veh)s\n# engine  : %(Eng)s\n# chassis : %(Css)s\n# scenario: %(Scn)s\n# section : %(Sec)s\n# physics : %(Phy)s\n#   t        s        Vz       Vx       Az       Ax       x        y        z        p        w        r\n'.lstrip('\r\n')

    def __writeHeader(self, name):
        descr = self.avatar.vehicle.typeDescriptor
        parts = name.split(VehicleTelemetry.NAME_DELIMITER)
        print parts
        header = VehicleTelemetry.HEADER_TMPL % {'Veh': descr.name,
         'Eng': descr.engine['name'],
         'Css': descr.chassis['name'],
         'Scn': parts[2],
         'Sec': parts[-2],
         'Phy': parts[-1]}
        self.dynamicsLog.write(header)

    def __closeDynamicsLog(self):
        if self.dynamicsLog:
            self.dynamicsLog.close()
            self.dynamicsLog = None
            os.rename(self.logPath, self.logPath + '.log')
        self.refTime = None
        self.refDist = None
        return

    def __onStop(self):
        self.__closeDynamicsLog()
        self.__completionFlag = True

    LOG_TMPL = ' '.join(('%(t)8.3f %(s)8.3f', '%(Vz)8.3f %(Vx)8.3f', '%(Az)8.3f %(Ax)8.3f', '%(x)8.3f %(y)8.3f %(z)8.3f', '%(p)8.3f %(w)8.3f %(r)8.3f', '\n'))

    def __logDynamics(self, paramNamesMap, snapshots):
        nmap = paramNamesMap
        for sh in snapshots:
            t = sh[nmap['time']] - self.refTime
            s = sh[nmap['path']] - self.refDist
            vel = sh[nmap['vel']]
            acc = sh[nmap['acc']]
            pos = sh[nmap['pos']]
            p = -math.degrees(sh[nmap['dir']][1])
            w = sh[nmap['wel']].y
            binormal = (acc * vel).length
            r = abs(vel.length ** 3 / binormal) if abs(binormal) > 0 else 0
            vel *= 3.6
            acc *= 1 / G
            line = VehicleTelemetry.LOG_TMPL % {'t': t,
             's': s,
             'Vz': vel.z,
             'Vx': vel.x,
             'Az': acc.z,
             'Ax': acc.x,
             'x': pos.x,
             'y': pos.y,
             'z': pos.z,
             'p': p,
             'w': w,
             'r': r}
            self.dynamicsLog.write(line)

    def receivePhysicsDebugInfo(self, info):
        infoDict = cPickle.loads(zlib.decompress(info))
        cmd = infoDict['cmd']
        if cmd == 'telemetry':
            if self.dynamicsLog:
                self.__logDynamics(infoDict['paramNamesMap'], infoDict['snapshots'])
            self.__physicsDebugInfo = infoDict
        elif cmd == 'comment':
            if self.dynamicsLog:
                line = '#%(text)s\n' % infoDict
                self.dynamicsLog.write(line)
        elif cmd == 'openLog':
            self.__openDynamicsLog(infoDict['key'], infoDict['time'], infoDict['path'])
        elif cmd == 'closeLog':
            self.__closeDynamicsLog()
        elif cmd == 'stop':
            self.__onStop()
        else:
            LOG_ERROR('Invalid PhysicsDebugInfo has been received:', infoDict)
