# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/aims.py
# Compiled at: 2018-11-29 14:33:44
import BigWorld, GUI, Math, ResMgr
from debug_utils import *
from gui.Scaleform.ColorSchemeManager import _ColorSchemeManager
from helpers import i18n
from helpers.func_utils import *
from gui import DEPTH_OF_Aim
from gui.Scaleform.Flash import Flash
from functools import partial
import math, weakref
from Vehicle import Vehicle
from account_helpers.AccountSettings import AccountSettings

def createAim(type):
    if type == 'strategic':
        return StrategicAim((0, 0.0))
    if type == 'arcade':
        return ArcadeAim((0, 0.15), False)
    if type == 'sniper':
        return ArcadeAim((0, 0.0), True)
    if type == 'postmortem':
        return PostMortemAim((0, 0.0))
    LOG_ERROR('Undefined aim type. <%s>' % type)


class Aim(Flash):
    _UPDATE_INTERVAL = 0.03
    __FLASH_CLASS = 'WGAimFlash'

    def __init__(self, mode, offset):
        Flash.__init__(self, 'crosshair_panel_{0:>s}.swf'.format(mode), self.__FLASH_CLASS)
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_Aim
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.movie.backgroundAlpha = 0
        self.flashSize = GUI.screenResolution()
        self._offset = offset
        self._isLoaded = False
        self.__timeInterval = _TimeInterval(Aim._UPDATE_INTERVAL, '_update', weakref.proxy(self))
        self.__isColorBlind = AccountSettings.getSettings('isColorBlind')

    def prerequisites(self):
        return []

    def create(self):
        AccountSettings.onSettingsChanging += self.applySettings
        self.__tankIndicatorCtrl = _TankIndicatorCtrl()
        self.__tankIndicatorCtrl.create()
        self.__cruiseCtrl = _CruiseCtrl()
        self.__cruiseCtrl.create()

    def destroy(self):
        AccountSettings.onSettingsChanging -= self.applySettings
        self.__tankIndicatorCtrl.destroy()
        self.__tankIndicatorCtrl = None
        self.__cruiseCtrl.destroy()
        self.__cruiseCtrl = None
        self.close()
        self.__timeInterval.stop()
        return

    def applySettings(self, type):
        global _g_aimState
        if type == 'cursors':
            settings = dict(AccountSettings.getSettings('cursors'))
            subSetting = settings['centralTag']
            self._flashCall('setCenterType', [subSetting['alpha'], subSetting['type']])
            subSetting = settings['net']
            self._flashCall('setNetType', [subSetting['alpha'], subSetting['type']])
            subSetting = settings['reloader']
            self._flashCall('setReloaderType', [subSetting['alpha'], subSetting['type']])
            subSetting = settings['condition']
            self._flashCall('setConditionType', [subSetting['alpha'], subSetting['type']])
        if type == 'isColorBlind':
            self.__isColorBlind = AccountSettings.getSettings('isColorBlind')
            state = _g_aimState['target']
            if state['isFriend'] is not None:
                self._flashCall('updateColor', [self.getTargetColor(state['isFriend'])])
        return

    def enable(self):
        self.active(True)
        self.applySettings('cursors')
        self.__timeInterval.start()
        _g_aimState['target']['id'] = None
        self.__tankIndicatorCtrl.enable()
        self.__cruiseCtrl.enable()
        self._enable(_g_aimState, _g_aimState['isFirstInit'])
        _g_aimState['isFirstInit'] = False
        self.onRecreateDevice()
        return

    def disable(self):
        self.active(False)
        _g_aimState['target']['id'] = None
        self.__timeInterval.stop()
        self.__tankIndicatorCtrl.disable()
        self.__cruiseCtrl.disable()
        self._disable()
        return

    def updateMarkerPos(self, pos, relaxTime):
        self.component.updateMarkerPos(pos, relaxTime)

    def onRecreateDevice(self):
        screen = GUI.screenResolution()
        self.component.size = screen
        self._flashCall('onRecreateDevice', [screen[0],
         screen[1],
         self._offset[0],
         self._offset[1]])

    def setVisible(self, isVisible):
        self.component.visible = isVisible

    def offset(self, value=None):
        if value is not None:
            self._offset = value
            self.onRecreateDevice()
        else:
            return self._offset
        return

    def attachTankIndicator(self, parentUI):
        self.__tankIndicatorCtrl.attachUI(parentUI)

    def attachCruiseCtrl(self, parentUI):
        self.__cruiseCtrl.attachUI(parentUI)

    def updateTankState(self, type, newState):
        _g_aimState['tankIndicator'][type] = 'critical' if newState == 'repaired' else newState
        self.__tankIndicatorCtrl.updateState(type, newState)

    def setTarget(self, target):
        state = _g_aimState['target']
        vInfo = dict(target.publicInfo)
        state['id'] = target.id
        state['startTime'] = None
        clanAbbrev = BigWorld.player().arena.vehicles.get(target.id, {}).get('clanAbbrev', '')
        state['name'] = i18n.convert('%s[%s]' % (vInfo['name'], clanAbbrev) if len(clanAbbrev) > 0 else vInfo['name'])
        state['vType'] = i18n.convert(target.typeDescriptor.type.userString)
        state['isFriend'] = vInfo['team'] == BigWorld.player().team
        self._setTarget(state['name'], state['vType'], state['isFriend'])
        return

    def clearTarget(self):
        state = _g_aimState['target']
        state['id'] = None
        state['startTime'] = BigWorld.time()
        self._clearTarget(0)
        return

    def getTargetColor(self, isFriend):
        colorScheme = _ColorSchemeManager.getSubScheme('aim_target_ally' if isFriend else 'aim_target_enemy', isColorBlind=self.__isColorBlind)
        return _ColorSchemeManager._makeRGB(colorScheme)

    def setReloading(self, duration, startTime=None):
        state = _g_aimState['reload']
        _isReloading = state.get('isReloading', False)
        _startTime = state.get('startTime', 0)
        _duration = state.get('duration', 0)
        isReloading = duration != 0
        state['isReloading'] = isReloading
        state['correction'] = None
        if _isReloading and duration > 0 and _duration > 0 and _startTime > 0:
            current = BigWorld.time()
            state['correction'] = {'timeRemaining': duration,
             'startTime': current,
             'startPosition': (current - _startTime) / _duration}
            self._correctReloadingTime(duration)
        else:
            state['duration'] = duration
            state['startTime'] = BigWorld.time() if isReloading else None
            self._setReloading(duration, 0, isReloading)
        return

    def setHealth(self, current):
        state = _g_aimState['health']
        state['cur'] = current
        if state['max'] is None:
            state['max'] = float(BigWorld.player().vehicleTypeDescriptor.maxHealth)
        self._setHealth(state['cur'], state['max'])
        return

    def setAmmoStock(self, shotsLeft):
        _g_aimState['ammoStock'] = shotsLeft
        self._setAmmoStock(shotsLeft)

    def setCruiseMode(self, newMode):
        _g_aimState['cruiseCtrl']['mode'] = newMode
        self.__cruiseCtrl.setCruiseMode(newMode)

    def showHit(self, gYaw, isBeak):
        _g_aimState['hitIndicators'].append({'gYaw': gYaw,
         'startTime': BigWorld.time(),
         'isBeak': isBeak})
        self._showHit(_g_aimState['hitIndicators'][-1:][0])

    def isGunReload(self):
        return _g_aimState['reload']['isReloading']

    def resetVehicleMatrix(self):
        pass

    def _enable(self, state, isFirstInit):
        pass

    def _disable(self):
        pass

    def _showHit(self, hitDesc):
        pass

    def _setTarget(self, name, vType, isFriend):
        self._flashCall('setTarget', [name, vType, self.getTargetColor(isFriend)])

    def _clearTarget(self, startTime):
        self._flashCall('clearTarget', [startTime])

    def _setReloading(self, duration, startTime=None, isReloading=True, correction=None):
        if correction is not None:
            params = self._getCorrectionReloadingParams(correction)
            if params is not None:
                self._flashCall('setReloading', params)
        else:
            self._flashCall('setReloading', [duration,
             startTime,
             isReloading,
             None])
        return

    def _correctReloadingTime(self, duration):
        self._flashCall('correctReloadingTime', [duration])

    def _getCorrectionReloadingParams(self, correction):
        cTimeRemaining = correction.get('timeRemaining', 0)
        cStartTime = correction.get('startTime', 0)
        cStartPosition = correction.get('startPosition', 0)
        if not cTimeRemaining > 0:
            LOG_WARNING('timeRemaining - invalid value ', cTimeRemaining)
            return None
        else:
            delta = BigWorld.time() - cStartTime
            currentPosition = cStartPosition + delta / cTimeRemaining * (1 - cStartPosition)
            return [cTimeRemaining - delta,
             cStartTime,
             True,
             currentPosition * 100.0]

    def _setHealth(self, cur, max):
        self._flashCall('setHealth', [cur / max])

    def _setAmmoStock(self, shotsLeft):
        self._flashCall('setAmmoStock', [shotsLeft, shotsLeft < 3])

    def _update(self):
        player = BigWorld.player()
        vehicle = BigWorld.entity(player.playerVehicleID)
        if vehicle is not None and vehicle.isStarted:
            speed, _ = player.getOwnVehicleSpeeds()
            _g_aimState['cruiseCtrl']['speed'] = speed
            self.__cruiseCtrl.updateSpeed(speed)
        targetID = _g_aimState['target']['id']
        if targetID is not None:
            targ = BigWorld.entity(targetID)
            if targ is None:
                self.clearTarget()
                LOG_ERROR('Invalid target ID')
            else:
                state = _g_aimState['target']
                state['dist'] = int((targ.position - BigWorld.player().getOwnVehiclePosition()).length)
                state['health'] = math.ceil(100.0 * max(0, targ.health) / targ.typeDescriptor.maxHealth)
        return

    def _flashCall(self, funcName, args=None):
        self.call('Aim.' + funcName, args)


class StrategicAim(Aim):

    def __init__(self, offset, isPostMortem=False):
        Aim.__init__(self, 'strategic', offset)

    def _enable(self, state, isFirstInit):
        if isFirstInit:
            return
        else:
            ts = state['target']
            if ts['startTime'] is not None:
                self._setTarget(ts['name'], ts['vType'], ts['isFriend'])
                Aim._flashCall(self, 'updateTarget', [ts['dist'], ts['health']])
                self._clearTarget(BigWorld.time() - ts['startTime'])
            hs = state['health']
            self._setHealth(hs['cur'], hs['max'])
            rs = state['reload']
            if rs['startTime'] is not None:
                self._setReloading(rs['duration'], startTime=BigWorld.time() - rs['startTime'], correction=rs['correction'])
            else:
                self._setReloading(rs['duration'], 0, False)
            self._setAmmoStock(state['ammoStock'])
            return

    def _update(self):
        Aim._update(self)
        Aim._flashCall(self, 'updateTarget', [_g_aimState['target']['dist'], _g_aimState['target']['health']])


class PostMortemAim(Aim):

    def __init__(self, offset):
        Aim.__init__(self, 'postmortem', offset)
        self.__msgCaption = i18n.makeString('#ingame_gui:player_messages/postmortem_caption')

    def create(self):
        Aim.create(self)
        self.__vID = None
        return

    def destroy(self):
        Aim.destroy(self)

    def changeVehicle(self, vID):
        self.__vID = vID

    def _update(self):
        Aim._update(self)
        if self.__vID is not None:
            vehicle = BigWorld.entity(self.__vID)
            if vehicle is not None:
                name = vehicle.publicInfo['name']
                type = vehicle.typeDescriptor.type.userString
                healthPercent = math.ceil(100.0 * max(0, vehicle.health) / vehicle.typeDescriptor.maxHealth)
                self.__setText(name, type, healthPercent)
        Aim._flashCall(self, 'updateTarget', [_g_aimState['target']['dist'], _g_aimState['target']['health']])
        return

    def __setText(self, name, type, health):
        text = i18n.convert(self.__msgCaption % {'name': name,
         'type': type,
         'health': health})
        Aim._flashCall(self, 'updatePlayerInfo', [text])


class ArcadeAim(Aim):

    def __init__(self, offset, isSniper):
        Aim.__init__(self, 'sniper' if isSniper else 'arcade', offset)
        self.__isSniper = isSniper

    def create(self):
        Aim.create(self)
        self.proxy = weakref.proxy(self)
        self.__damageCtrl = _DamageIndicatorCtrl(self._offset)

    def destroy(self):
        Aim.destroy(self)
        self.__damageCtrl.disable()
        self.__damageCtrl = None
        return

    def _enable(self, state, isFirstInit):
        self.__damageCtrl.enable()
        if isFirstInit:
            return
        else:
            ts = state['target']
            if ts['startTime'] is not None:
                self._setTarget(ts['name'], ts['vType'], ts['isFriend'])
                Aim._flashCall(self, 'updateTarget', [ts['dist'], ts['health']])
                self._clearTarget(BigWorld.time() - ts['startTime'])
            hs = state['health']
            self._setHealth(hs['cur'], hs['max'])
            rs = state['reload']
            if rs['startTime'] is not None:
                self._setReloading(rs['duration'], startTime=BigWorld.time() - rs['startTime'], correction=rs['correction'])
            else:
                self._setReloading(rs['duration'], 0, False)
            self._setAmmoStock(state['ammoStock'])
            return

    def _disable(self):
        self.__damageCtrl.disable()

    def setVisible(self, isVisible):
        Aim.setVisible(self, isVisible)
        self.__damageCtrl.setVisible(isVisible)

    def onRecreateDevice(self):
        Aim.onRecreateDevice(self)
        self.__damageCtrl.onRecreateDevice()

    def _showHit(self, hitDesc):
        self.__damageCtrl.add(hitDesc)

    def _update(self):
        Aim._update(self)
        Aim._flashCall(self, 'updateTarget', [_g_aimState['target']['dist'], _g_aimState['target']['health']])


class _DamageIndicatorCtrl():
    _HIT_INDICATOR_MAX_ON_SCREEN = 5

    def __init__(self, offset):
        self.proxy = weakref.proxy(self)
        self.__worldToClip = None
        self.__isVisible = True
        self.__offset = offset
        self.__hits = list()
        return

    def enable(self):
        for hitDesc in _g_aimState['hitIndicators'][:]:
            self.add(hitDesc)

    def disable(self):
        for hitDesc in _g_aimState['hitIndicators']:
            if hitDesc.get('comp', None) is not None:
                hitDesc['comp'].close()
                BigWorld.cancelCallback(hitDesc['callbackID'])
                hitDesc['comp'] = None
                hitDesc['callbackID'] = None

        return

    def setVisible(self, isVisible):
        self.__isVisible = isVisible
        for hitDesc in _g_aimState['hitIndicators']:
            if hitDesc.get('comp', None) is not None:
                hitDesc['comp'].component.visible = isVisible

        return

    def add(self, hitDesc):
        duration = _DamageIndicator.TOTAL_FRAMES / float(_DamageIndicator.FRAME_RATE)
        globalYaw = hitDesc['gYaw']
        startTime = hitDesc['startTime']
        isBeak = hitDesc['isBeak']
        timePass = BigWorld.time() - startTime
        if timePass >= duration:
            self._remove(startTime)
            return
        if len(_g_aimState['hitIndicators']) >= self._HIT_INDICATOR_MAX_ON_SCREEN:
            self._remove(min((desc['startTime'] for desc in _g_aimState['hitIndicators'])))
        hitInd = _DamageIndicator()
        hitInd.setup(globalYaw, self.__offset)
        hitInd.active(True)
        hitInd.component.visible = self.__isVisible
        hitInd.call('DamageIndicator.setBreakFlagAndAnimFrame', [isBeak, timePass * _DamageIndicator.FRAME_RATE])
        callbackID = BigWorld.callback(duration, partial(callMethod, self.proxy, '_remove', startTime))
        hitDesc['comp'] = hitInd
        hitDesc['callbackID'] = callbackID

    def onRecreateDevice(self):
        for desc in _g_aimState['hitIndicators']:
            desc['comp'].setup(desc['gYaw'], self.__offset)

    def _remove(self, startTime):
        removedDesc = None
        for desc in _g_aimState['hitIndicators']:
            if desc['startTime'] == startTime:
                removedDesc = desc
                break

        if removedDesc is not None:
            if removedDesc.get('comp', None) is not None:
                removedDesc['comp'].close()
            _g_aimState['hitIndicators'].remove(removedDesc)
        return


class _DamageIndicator(Flash):
    __SWF_FILE_NAME = 'DamageIndicator.swf'
    __FLASH_CLASS = 'WGHitIndicatorFlash'
    __FLASH_MC_NAME = 'damageMC'
    __FLASH_SIZE = (680, 680)
    TOTAL_FRAMES = 90
    FRAME_RATE = 24

    def __init__(self):
        Flash.__init__(self, self.__SWF_FILE_NAME, self.__FLASH_CLASS, [self.__FLASH_MC_NAME])
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_Aim
        self.movie.backgroundAlpha = 0.0
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.flashSize = self.__FLASH_SIZE

    def setup(self, gYaw, offset):
        self.component.position.x = offset[0]
        self.component.position.y = offset[1]
        self.component.wg_globalYaw = gYaw

    def __del__(self):
        pass


class _TankIndicatorCtrl():

    def __init__(self):
        self.__cfg = {}
        self.__ui = None
        self.__interval = _TimeInterval(0.05, '_TankIndicatorCtrl__waitingVehicle', weakref.proxy(self))
        self.__enabled = False
        return

    def create(self):
        vDesc = BigWorld.player().vehicleTypeDescriptor
        vTags = vDesc.type.tags
        yawLimits = vDesc.turret['yawLimits']
        if 'SPG' in vTags:
            type = 'SPG'
        elif 'AT-SPG' in vTags:
            type = 'AT-SPG'
        else:
            type = 'Tank'
        if type in ('SPG', 'AT-SPG') and yawLimits is None:
            type = 'Tank'
        self.__cfg['type'] = type
        self.__cfg['yawLimits'] = yawLimits
        self.__cfg['hullMat'] = None
        self.__cfg['turretMat'] = None
        self.__cfg['isDestroyed'] = False
        return

    def attachUI(self, parentUI):
        cfg = self.__cfg
        if cfg['isDestroyed']:
            return
        else:
            self.__ui = parentUI
            ui = self.__ui()
            self.__flashCall('setType', [cfg['type']])
            mc = getattr(ui.component, 'tankIndicator', None)
            if mc is not None:
                if self.__enabled:
                    self.__setCfg(mc, cfg)
                return
            mc = GUI.WGTankIndicatorFlash(ui.movie, '_root.damagePanel.tankIndicator')
            mc.wg_inputKeyMode = 2
            self.__setCfg(mc, cfg)
            for state in _g_aimState['tankIndicator']:
                self.__flashCall('updateState', [state[0], state[1]])

            ui.component.addChild(mc, 'tankIndicator')
            return

    def destroy(self):
        ui = self.__ui() if self.__ui is not None else None
        if ui is not None:
            res = getattr(ui.component, 'tankIndicator', None)
            if res is not None:
                setattr(ui.component, 'tankIndicator', None)
        else:
            self.__cfg['isDestroyed'] = True
        return

    def enable(self):
        self.__enabled = True
        vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        if vehicle is None:
            self.__interval.start()
            return
        else:
            if _g_aimState['tankIndicator'] is not None:
                for type, state in _g_aimState['tankIndicator'].iteritems():
                    self.updateState(type, state)

            self.__setup(vehicle.appearance)
            return

    def disable(self):
        self.__enabled = False
        self.__interval.stop()

    def updateState(self, type, newState):
        ui = self.__ui() if self.__ui is not None else None
        if ui is not None:
            self.__flashCall('updateState', [type, newState])
        return

    def __setCfg(self, mc, cfg):
        yawLimits = cfg['yawLimits']
        if yawLimits is not None:
            mc.wg_turretYawConstraints = yawLimits
            self.__flashCall('setGunConstraints', [math.degrees(-yawLimits[0]), math.degrees(yawLimits[1])])
        if cfg['hullMat'] is not None and cfg['turretMat'] is not None:
            mc.wg_hullMatProv = cfg['hullMat']
            mc.wg_turretMatProv = cfg['turretMat']
        return

    def __waitingVehicle(self):
        vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        if vehicle is None:
            return
        else:
            self.__interval.stop()
            self.__setup(vehicle.appearance)
            return

    def __setup(self, appearance):
        hullMat = BigWorld.player().getOwnVehicleMatrix()
        turretMat = appearance.turretMatrix
        ui = self.__ui() if self.__ui is not None else None
        if ui is not None:
            tankIndicator = self.__ui().component.tankIndicator
            tankIndicator.wg_hullMatProv = hullMat
            tankIndicator.wg_turretMatProv = turretMat
        else:
            self.__cfg['hullMat'] = hullMat
            self.__cfg['turretMat'] = turretMat
        return

    def __flashCall(self, funcName, args=None):
        self.__ui().call('battle.tankIndicator.' + funcName, args)


class _CruiseCtrl():

    def __init__(self):
        self.__ui = None
        self.__enabled = False
        return

    def create(self):
        pass

    def attachUI(self, parentUI):
        self.__ui = parentUI
        if not self.__enabled:
            return
        self.__flashCall('setCruiseMode', [_g_aimState['cruiseCtrl']['mode']])
        self.__flashCall('updateSpeed', [_g_aimState['cruiseCtrl']['speed']])

    def destroy(self):
        self.__ui = None
        return

    def enable(self):
        self.__enabled = True

    def disable(self):
        self.__enabled = False

    def setCruiseMode(self, newMode):
        if self.__ui and self.__ui():
            self.__flashCall('setCruiseMode', [newMode])

    def updateSpeed(self, speed):
        if self.__ui and self.__ui():
            self.__flashCall('updateSpeed', [int(speed * 3.6)])

    def __flashCall(self, funcName, args=None):
        self.__ui().call('battle.cruiseCtrl.' + funcName, args)


class _TimeInterval():

    def __init__(self, interval, funcName, scopeProxy=None):
        self.__cbId = None
        self.__interval = interval
        self.__funcName = funcName
        self.__scopeProxy = scopeProxy
        return

    def start(self):
        if self.__cbId is not None:
            LOG_ERROR('To start a new time interval You should before stop already the running time interval.')
            return
        else:
            self.__cbId = BigWorld.callback(self.__interval, self.__update)
            return

    def stop(self):
        if self.__cbId is not None:
            BigWorld.cancelCallback(self.__cbId)
            self.__cbId = None
        return

    def __update(self):
        self.__cbId = None
        if self.__scopeProxy is not None:
            funcObj = getattr(self.__scopeProxy, self.__funcName, None)
            if funcObj is not None:
                funcObj()
        self.__cbId = BigWorld.callback(self.__interval, self.__update)
        return


def clearState():
    global _g_aimState
    _g_aimState = {'isFirstInit': True,
     'target': {'id': None,
                'dist': 0,
                'health': 0,
                'startTime': None,
                'name': None,
                'vType': None,
                'isFriend': None},
     'reload': {},
     'tankIndicator': {},
     'hitIndicators': [],
     'cruiseCtrl': {'mode': 0,
                    'speed': 0},
     'ammoStock': 0,
     'health': {'cur': None,
                'max': None}}
    return


_g_aimState = None
