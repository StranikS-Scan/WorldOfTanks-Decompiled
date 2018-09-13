# Embedded file name: scripts/client/AvatarInputHandler/aims.py
from functools import partial
import math
import weakref
import BigWorld
import GUI
import Math
import ResMgr
from debug_utils import *
from helpers import i18n
from helpers.func_utils import *
from gui import DEPTH_OF_Aim, GUI_SETTINGS
from gui.Scaleform.Flash import Flash
from gui.Scaleform.ColorSchemeManager import _ColorSchemeManager
from gui.BattleContext import g_battleContext
import BattleReplay

def createAim(type):
    if not GUI_SETTINGS.isGuiEnabled():
        from gui.development.no_gui.battle import Aim
        return Aim()
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
    _AIM_TYPES = ('arcade', 'sniper')

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
        self.mode = mode
        self.__timeInterval = _TimeInterval(Aim._UPDATE_INTERVAL, '_update', weakref.proxy(self))
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        self.__aimSettings = None
        self.__isColorBlind = g_settingsCore.getSetting('isColorBlind')
        return

    def prerequisites(self):
        return []

    def _isColorBlind(self):
        return self.__isColorBlind

    def create(self):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged += self.onSettingsChanged
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.replayContainsGunReloads:
            self._flashCall('setupReloadingCounter', [False])
            self.__cbIdSetReloading = BigWorld.callback(0.0, self.setReloadingFromReplay)
        else:
            self.__cbIdSetReloading = None
        return

    def destroy(self):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged -= self.onSettingsChanged
        self.close()
        if self.__cbIdSetReloading is not None:
            BigWorld.cancelCallback(self.__cbIdSetReloading)
            self.__cbIdSetReloading = None
        self.__timeInterval.stop()
        self.__timeInterval = None
        self.__aimSettings = None
        return

    def onSettingsChanged(self, diff = None):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        if self.mode in self._AIM_TYPES and (diff is None or self.mode in diff):
            self.__aimSettings = g_settingsCore.getSetting(self.mode)
            self.applySettings()
        if diff is not None:
            if 'isColorBlind' in diff:
                self.__isColorBlind = diff['isColorBlind']
        return

    def applySettings(self):
        if self.__aimSettings is not None:
            self._flashCall('initSettings', [self.__aimSettings['centralTag'],
             self.__aimSettings['centralTagType'],
             self.__aimSettings['net'],
             self.__aimSettings['netType'],
             self.__aimSettings['reloader'],
             0,
             self.__aimSettings['condition'],
             0,
             self.__aimSettings['cassette'],
             0,
             self.__aimSettings['reloaderTimer'],
             0])
        return

    def enable(self):
        global _g_aimState
        self.active(True)
        if self.__aimSettings is None:
            self.onSettingsChanged()
        self.__timeInterval.start()
        _g_aimState['target']['id'] = None
        self._enable(_g_aimState, _g_aimState['isFirstInit'])
        _g_aimState['isFirstInit'] = False
        self.onRecreateDevice()
        return

    def disable(self):
        self.active(False)
        _g_aimState['target']['id'] = None
        self.__timeInterval.stop()
        self._disable()
        return

    def updateMarkerPos(self, pos, relaxTime):
        self.component.updateMarkerPos(pos, relaxTime)

    def onRecreateDevice(self):
        screen = GUI.screenResolution()
        self.component.size = screen
        width = screen[0]
        height = screen[1]
        offsetX = self._offset[0]
        offsetY = self._offset[1]
        posX = 0.5 * width * (1.0 + offsetX)
        posX = round(posX) if width % 2 == 0 else int(posX)
        posY = 0.5 * height * (1.0 - offsetY)
        posY = round(posY) if height % 2 == 0 else int(posY)
        self._flashCall('onRecreateDevice', [posX, posY])

    def setVisible(self, isVisible):
        self.component.visible = isVisible

    def offset(self, value = None):
        if value is not None:
            self._offset = value
            self.onRecreateDevice()
        else:
            return self._offset
        return

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

    def getReloadingTimeLeft(self):
        state = _g_aimState['reload']
        correction = state.get('correction')
        startTime = state.get('startTime', 0)
        duration = state.get('duration', 0)
        if correction is not None:
            startTime = correction.get('startTime', 0)
            duration = correction.get('timeRemaining', 0)
        if startTime is not None:
            current = BigWorld.time()
            return duration - (current - startTime)
        else:
            return 0

    def getAmmoQuantityLeft(self):
        ammo = _g_aimState['ammo']
        if self.isCasseteClip():
            return ammo[1]
        else:
            return ammo[0]

    def isCasseteClip(self):
        clip = _g_aimState['clip']
        return clip[0] != 1 or clip[1] != 1

    def setReloading(self, duration, startTime = None, baseTime = None):
        state = _g_aimState['reload']
        _isReloading = state.get('isReloading', False)
        _startTime = state.get('startTime', 0)
        _duration = state.get('duration', 0)
        isReloading = duration != 0
        state['isReloading'] = isReloading
        state['correction'] = None
        state['baseTime'] = baseTime
        if _isReloading and duration > 0 and _duration > 0 and _startTime > 0:
            current = BigWorld.time()
            state['correction'] = {'timeRemaining': duration,
             'startTime': current,
             'startPosition': (current - _startTime) / _duration}
            self._flashCall('updateReloadingBaseTime', [baseTime, False])
            self._correctReloadingTime(duration)
        else:
            state['duration'] = duration
            state['startTime'] = BigWorld.time() if isReloading else None
            self._setReloading(duration, 0, isReloading, None, baseTime)
        return

    def setHealth(self, current):
        state = _g_aimState['health']
        state['cur'] = current
        if state['max'] is None:
            state['max'] = float(BigWorld.player().vehicleTypeDescriptor.maxHealth)
        self._setHealth(state['cur'], state['max'])
        return

    def setAmmoStock(self, quantity, quantityInClip, clipReloaded = False):
        _g_aimState['ammo'] = (quantity, quantityInClip)
        self._setAmmoStock(quantity, quantityInClip, clipReloaded=clipReloaded)

    def updateAmmoState(self, hasAmmo):
        self._flashCall('updateAmmoState', [hasAmmo])

    def getAmmoState(self, quantity, quantityInClip):
        clipCapacity, burst = _g_aimState['clip']
        state = 'normal'
        isLow = quantity < 3
        if clipCapacity > 1:
            state = self._getClipState(clipCapacity, burst, quantityInClip)
            isLow |= quantity <= clipCapacity
        return (isLow, state)

    def setClipParams(self, capacity, burst):
        _g_aimState['clip'] = (capacity, burst)
        if capacity > 1:
            self._setClipParams(capacity, burst)

    def showHit(self, gYaw, isDamage):
        _g_aimState['hitIndicators'].append({'gYaw': gYaw,
         'startTime': BigWorld.time(),
         'isDamage': isDamage})
        self._showHit(_g_aimState['hitIndicators'][-1:][0])

    def isGunReload(self):
        return _g_aimState['reload']['isReloading']

    def onCameraChange(self):
        if not self.isGunReload():
            baseTime = _g_aimState['reload'].get('baseTime', -1)
            self._flashCall('updateReloadingBaseTime', [baseTime, True])
        elif not _g_aimState['reload']['correction']:
            self._flashCall('clearPreviousCorrection', [])

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

    def setReloadingFromReplay(self):
        self._setReloadingAsPercent(100.0 * BattleReplay.g_replayCtrl.getGunReloadAmountLeft())
        self.__cbIdSetReloading = BigWorld.callback(0.0, self.setReloadingFromReplay)

    def _setReloading(self, duration, startTime = None, isReloading = True, correction = None, baseTime = None):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.replayContainsGunReloads:
            return
        else:
            if replayCtrl.isRecording:
                replayCtrl.setGunReloadTime(startTime, duration)
            if correction is not None:
                params = self._getCorrectionReloadingParams(correction)
                if params is not None:
                    self._flashCall('setReloading', params)
            else:
                self._flashCall('setReloading', [duration,
                 startTime,
                 isReloading,
                 None,
                 baseTime])
            return

    def _setReloadingAsPercent(self, percent):
        self._flashCall('setReloadingAsPercent', [percent])

    def _correctReloadingTime(self, duration):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.replayContainsGunReloads:
            self.setReloadingFromReplay()
            return
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
        if cur is not None and max is not None:
            self._flashCall('setHealth', [cur / max])
        return

    def _setAmmoStock(self, quantity, quantityInClip, clipReloaded = False):
        isLow, state = self.getAmmoState(quantity, quantityInClip)
        self._flashCall('setAmmoStock', [quantity,
         quantityInClip,
         isLow,
         state,
         clipReloaded])

    def _getClipState(self, capacity, burst, quantityInClip):
        state = 'normal'
        if burst > 1:
            total = math.ceil(float(capacity) / float(burst))
            current = math.ceil(float(quantityInClip) / float(burst))
        else:
            total = capacity
            current = quantityInClip
        if current <= 0.5 * total:
            state = 'critical' if current == 1 else 'warning'
        return state

    def _setClipParams(self, capacity, burst):
        self._flashCall('setClipParams', [capacity, burst])

    def _update(self):
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

    def _flashCall(self, funcName, args = None):
        self.call('Aim.' + funcName, args)


class StrategicAim(Aim):

    def __init__(self, offset, isPostMortem = False):
        Aim.__init__(self, 'strategic', offset)

    def create(self):
        Aim.create(self)
        self.__damageCtrl = _DamageIndicatorCtrl(self._offset)

    def onRecreateDevice(self):
        Aim.onRecreateDevice(self)
        self.__damageCtrl.onRecreateDevice()

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
            Aim._flashCall(self, 'updateDistance', [self._getAimDistance()])
            hs = state['health']
            self._setHealth(hs['cur'], hs['max'])
            rs = state['reload']
            if rs['startTime'] is not None:
                self._setReloading(rs['duration'], startTime=BigWorld.time() - rs['startTime'], correction=rs['correction'])
            else:
                self._setReloading(rs['duration'], 0, False)
            capacity, burst = state['clip']
            if capacity > 1:
                self._setClipParams(capacity, burst)
            self._setAmmoStock(*state['ammo'])
            return

    def _disable(self):
        self.__damageCtrl.disable()

    def _showHit(self, hitDesc):
        self.__damageCtrl.add(hitDesc)

    def _update(self):
        Aim._update(self)
        Aim._flashCall(self, 'updateDistance', [self._getAimDistance()])

    def _clearTarget(self, startTime):
        pass

    def _getAimDistance(self):
        x, y, z = BigWorld.player().gunRotator.markerInfo[0]
        v = BigWorld.player().getOwnVehiclePosition() - Math.Vector3(x, y, z)
        return int(v.length)


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

    def onSettingsChanged(self, diff = None):
        super(PostMortemAim, self).onSettingsChanged(diff)
        if diff is not None:
            if 'isColorBlind' in diff:
                self.updateAdjust()
        return

    def changeVehicle(self, vID):
        self.__vID = vID
        self.updateAdjust()
        if vID == BigWorld.player().playerVehicleID:
            self.updateAmmoState(True)

    def updateAdjust(self):
        scheme = _ColorSchemeManager.getSubScheme('vm_ally', self._isColorBlind())
        adjustTuple = _ColorSchemeManager._makeAdjustTuple(scheme)
        self._flashCall('updateAdjust', list(adjustTuple))

    def _update(self):
        Aim._update(self)
        if self.__vID is not None:
            vehicle = BigWorld.entity(self.__vID)
            if vehicle is not None:
                playerName = g_battleContext.getFullPlayerName(vID=self.__vID, showVehShortName=False)
                type = vehicle.typeDescriptor.type.userString
                healthPercent = math.ceil(100.0 * max(0, vehicle.health) / vehicle.typeDescriptor.maxHealth)
                self.__setText(playerName, type, healthPercent)
        Aim._flashCall(self, 'updateTarget', [_g_aimState['target']['dist']])
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
                Aim._flashCall(self, 'updateTarget', [ts['dist']])
                self._clearTarget(BigWorld.time() - ts['startTime'])
            hs = state['health']
            self._setHealth(hs['cur'], hs['max'])
            rs = state['reload']
            if rs['startTime'] is not None:
                self._setReloading(rs['duration'], startTime=BigWorld.time() - rs['startTime'], correction=rs['correction'])
            else:
                self._setReloading(rs['duration'], 0, False)
            capacity, burst = state['clip']
            if capacity > 1:
                self._setClipParams(capacity, burst)
            self._setAmmoStock(*state['ammo'])
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
        Aim._flashCall(self, 'updateTarget', [_g_aimState['target']['dist']])


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
        isDamage = hitDesc['isDamage']
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
        hitInd.call('DamageIndicator.setDamageFlagAndAnimFrame', [isDamage, timePass * _DamageIndicator.FRAME_RATE])
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


class _TimeInterval():

    def __init__(self, interval, funcName, scopeProxy = None):
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
     'hitIndicators': [],
     'ammo': (0, 0),
     'clip': (1, 1),
     'health': {'cur': None,
                'max': None}}
    return


_g_aimState = None
