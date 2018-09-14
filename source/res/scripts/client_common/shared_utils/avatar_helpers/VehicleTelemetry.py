# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/shared_utils/avatar_helpers/VehicleTelemetry.py
import cPickle
import zlib
import math
import os.path
import datetime
import ResMgr
from debug_utils import *
from constants import ENABLE_DEBUG_DYNAMICS_INFO
from physics_shared import G

class VehicleTelemetry:

    def __init__(self, avatar):
        assert avatar is not None
        self.avatar = avatar
        self.dynamicsLog = None
        self.dynamicsLogKey = None
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
            self.avatar.base.setDevelopmentFeature('toggle_vehicle_debug_info', flag, '')
            self.__physicsDebugInfoEnabled = shouldEnable
            return

    try:
        DYNAMICS_LOG_DIR = ResMgr.appDirectory() + 'dynamics_log'
    except AttributeError:
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
        vname = self.avatar.getVehicleAttached().typeDescriptor.name
        vname = vname.replace(':', VehicleTelemetry.NAME_DELIMITER)
        sname = scenarioName.split('.', 1)[0]
        stamp = datetime.datetime.now().strftime('%y%m%d%H%M%S')
        logName = VehicleTelemetry.NAME_DELIMITER.join((vname, sname, stamp))
        return logName

    def recordVehicleDynamics(self, scenarioName, isRapidMode=True):
        if not self.avatar.inWorld:
            LOG_WARNING('Avatar.base is not available yet on Avatar client')
            LOG_CODEPOINT_WARNING()
            return
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
            self.__closeDynamicsLog()
        name = VehicleTelemetry.NAME_DELIMITER.join((self.logName, key))
        self.logPath = os.path.join(VehicleTelemetry.DYNAMICS_LOG_DIR, name)
        assert not os.path.exists(self.logPath)
        self.dynamicsLog = open(self.logPath, 'w')
        self.refTime = refTime
        self.refDist = refDist
        self.__writeHeader(name)

    HEADER_TMPL = '\n# vehicle : %(Veh)s\n# engine  : %(Eng)s\n# chassis : %(Css)s\n# scenario: %(Scn)s\n# section : %(Sec)s\n# physics : %(Phy)s\n#   t        s        Vz       Vx       Az       Ax       X        Y        Z        yaw      w        wcc      p        r\n'.lstrip('\r\n')

    def __writeHeader(self, name):
        descr = self.avatar.getVehicleAttached().typeDescriptor
        parts = name.split(VehicleTelemetry.NAME_DELIMITER)
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

    LOG_TMPL = ' '.join(('%(t)8.3f %(s)8.3f', '%(Vz)8.3f %(Vx)8.3f', '%(Az)8.3f %(Ax)8.3f', '%(X)8.3f %(Y)8.3f %(Z)8.3f', '%(y)8.3f %(w)8.3f %(q)8.3f', '%(p)8.3f %(r)8.3f', '%(h)4d', '%(ltr)8.3f %(rtr)8.3f', '%(ltp)8.3f %(rtp)8.3f', '%(lte)8.3f %(rte)8.3f', '%(hle)8.3f', '%(dhh)8.3f %(dlt)8.3f %(drt)8.3f', '%(hdm)8.3f %(hrc)8.3f', '%(lthp)8.3f %(rthp)8.3f', '%(Vy)8.3f %(Ay)8.3f', '%(ltslp)8.3f %(rtslp)8.3f', '%(ltbf)8.3f %(rtbf)8.3f', '%(roll)8.3f', '\n'))

    def __logDynamics(self, paramNamesMap, snapshots):
        nmap = paramNamesMap
        for sh in snapshots:
            t = sh[nmap['time']] - self.refTime
            if t < 0:
                print 'Nt:', sh[nmap['time']], self.refTime
            s = sh[nmap['path']] - self.refDist
            vel = sh[nmap['vel']]
            acc = sh[nmap['acc']]
            pos = sh[nmap['pos']]
            pitch = -math.degrees(sh[nmap['dir']][1])
            roll = math.degrees(sh[nmap['dir']][2])
            yaw = math.degrees(sh[nmap['dir']][0])
            wel = math.degrees(sh[nmap['wel']].y)
            wcc = math.degrees(sh[nmap['wac']].y)
            binormal = (acc * vel).length
            r = abs(vel.length ** 3 / binormal) if abs(binormal) > 0 else 0
            r = min(500, r)
            vel *= 3.6
            acc *= 1 / G
            line = VehicleTelemetry.LOG_TMPL % {'t': t,
             's': s,
             'Vz': vel.z,
             'Vx': vel.x,
             'Az': acc.z,
             'Ax': acc.x,
             'X': pos.x,
             'Y': pos.y,
             'Z': pos.z,
             'y': yaw,
             'w': wel,
             'q': wcc,
             'p': pitch,
             'roll': roll,
             'r': r,
             'h': int(self.avatar.getVehicleAttached().health),
             'ltr': sh[nmap['lTrackReaction']] if nmap.has_key('lTrackReaction') else 0.0,
             'rtr': sh[nmap['rTrackReaction']] if nmap.has_key('rTrackReaction') else 0.0,
             'ltp': sh[nmap['lTrackPressure']] if nmap.has_key('lTrackPressure') else 0.0,
             'rtp': sh[nmap['rTrackPressure']] if nmap.has_key('rTrackPressure') else 0.0,
             'lte': sh[nmap['lTrackEnergy']] if nmap.has_key('lTrackEnergy') else 0.0,
             'rte': sh[nmap['rTrackEnergy']] if nmap.has_key('rTrackEnergy') else 0.0,
             'hle': sh[nmap['hullEnergy']] if nmap.has_key('hullEnergy') else 0.0,
             'dhh': sh[nmap['dmg_hh']] if nmap.has_key('dmg_hh') else 0.0,
             'dlt': sh[nmap['dmg_lt']] if nmap.has_key('dmg_lt') else 0.0,
             'drt': sh[nmap['dmg_rt']] if nmap.has_key('dmg_rt') else 0.0,
             'lthp': sh[nmap['lthp']] if nmap.has_key('lthp') else 0.0,
             'rthp': sh[nmap['rthp']] if nmap.has_key('rthp') else 0.0,
             'hdm': sh[nmap['hull_dmgmp']] if nmap.has_key('hull_dmgmp') else 0.0,
             'hrc': sh[nmap['hull_react']] if nmap.has_key('hull_react') else 0.0,
             'Vy': vel.y,
             'Ay': acc.y,
             'ltslp': sh[nmap['trackScrolling']][0] if nmap.has_key('trackScrolling') else -20.0,
             'rtslp': sh[nmap['trackScrolling']][1] if nmap.has_key('trackScrolling') else -30.0,
             'ltbf': sh[nmap['ltbf']] if nmap.has_key('ltbf') else 0.0,
             'rtbf': sh[nmap['rtbf']] if nmap.has_key('rtbf') else 0.0}
            self.dynamicsLog.write(line)
            self.dynamicsLog.flush()

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
