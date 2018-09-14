# Embedded file name: scripts/client/AvatarInputHandler/aims.py
import math
import weakref
import GUI
import Math
from debug_utils import *
from gui.battle_control import g_sessionProvider
from helpers import i18n
from helpers.func_utils import *
from gui import DEPTH_OF_Aim, GUI_SETTINGS
from gui.Scaleform.Flash import Flash
from gui.Scaleform.ColorSchemeManager import _ColorSchemeManager
from gui.battle_control.consumables.ammo_ctrl import SHELL_SET_RESULT
from gui.shared.gui_items import Vehicle
from gui import makeHtmlString
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI

def _getScreenSize():
    return GUI.screenResolution()[:2]


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
    if type == 'falloutdeath':
        return FalloutDeathAim((0, 0.0))
    LOG_ERROR('Undefined aim type. <%s>' % type)


g_reloadingHandler = None

def getReloadingHandler():
    global g_reloadingHandler
    if g_reloadingHandler is None:
        g_reloadingHandler = ReloadingStateHandler()
    return g_reloadingHandler


class ReloadingStateHandler(object):

    def __init__(self):
        self.state = {}
        self.ammoStock = (0, 0)
        self.__currentAim = None
        return

    def setReloading(self, duration, startTime = None, baseTime = None):
        if self.__currentAim is not None:
            self.__currentAim.setReloading(duration, startTime, baseTime)
        return

    def setReloadingInPercent(self, percent, isReloading = True):
        if self.__currentAim is not None:
            self.__currentAim.setReloadingInPercent(percent, isReloading)
        return

    def setShellChanged(self, _):
        shell = g_sessionProvider.getAmmoCtrl().getCurrentShells()
        self.ammoStock = shell
        if self.__currentAim is not None:
            self.__currentAim._setAmmoStock(shell[0], shell[1])
        return

    def setAmmoStock(self, _, quantity, quantityInClip, clipReloaded):
        if not clipReloaded & SHELL_SET_RESULT.CURRENT:
            return
        else:
            self.ammoStock = (quantity, quantityInClip)
            if self.__currentAim is not None:
                self.__currentAim._setAmmoStock(quantity, quantityInClip, clipReloaded & SHELL_SET_RESULT.CASSETTE_RELOAD > 0)
            return

    def onAimChanged(self, aim):
        self.__currentAim = aim


class Aim(Flash):
    _UPDATE_INTERVAL = 0.03
    __FLASH_CLASS = 'WGAimFlash'
    _AIM_TYPES = ('arcade', 'sniper')
    EPSILON = 0.001

    def __init__(self, mode, offset):
        Flash.__init__(self, 'crosshair_panel_{0:>s}.swf'.format(mode), self.__FLASH_CLASS)
        self._posX = 0
        self._posY = 0
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_Aim
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.movie.backgroundAlpha = 0
        self._offset = offset
        self._isLoaded = False
        self.mode = mode
        self.__timeInterval = _TimeInterval(Aim._UPDATE_INTERVAL, '_update', weakref.proxy(self))
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        self.settingsCore = weakref.proxy(g_settingsCore)
        self.__aimSettings = None
        self.__isColorBlind = self.settingsCore.getSetting('isColorBlind')
        self.settingsCore.interfaceScale.onScaleChanged += self.__refreshScale
        self.settingsCore.interfaceScale.onScaleChanged += self.onRecreateDevice
        self.__refreshScale(self.settingsCore.interfaceScale.get())
        self._reloadingHndl = getReloadingHandler()
        return

    def prerequisites(self):
        return []

    def _isColorBlind(self):
        return self.__isColorBlind

    def create(self):
        self.settingsCore.onSettingsChanged += self.onSettingsChanged
        import BattleReplay
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            self._flashCall('setupReloadingCounter', [False])

    def destroy(self):
        self.settingsCore.onSettingsChanged -= self.onSettingsChanged
        self.settingsCore.interfaceScale.onScaleChanged -= self.__refreshScale
        self.settingsCore.interfaceScale.onScaleChanged -= self.onRecreateDevice
        self.close()
        self.__timeInterval.stop()
        self.__timeInterval = None
        self.__aimSettings = None
        return

    def onSettingsChanged(self, diff = None):
        if self.mode in self._AIM_TYPES and (diff is None or self.mode in diff):
            self.__aimSettings = self.settingsCore.getSetting(self.mode)
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
        self._reloadingHndl.onAimChanged(self)
        if self.__aimSettings is None:
            self.onSettingsChanged()
        self.__timeInterval.start()
        _g_aimState['target']['id'] = None
        g_sessionProvider.setAimOffset(self._offset)
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

    def onOffsetUpdate(self, screen, forced = False):
        width, height = screen
        offsetX, offsetY = self._offset[:2]
        scale = self.settingsCore.interfaceScale.get()
        posX = 0.5 * width * (1.0 + offsetX) / scale
        posX = round(posX) if width % 2 == 0 else int(posX)
        posY = 0.5 * height * (1.0 - offsetY) / scale
        posY = round(posY) if height % 2 == 0 else int(posY)
        if forced or self._posX != posX or self._posY != posY:
            self._posX = posX
            self._posY = posY
            self._flashCall('onRecreateDevice', [self._posX, self._posY])
            g_sessionProvider.setAimPositionUpdated(self.mode, self._posX, self._posY)

    def onRecreateDevice(self, scale = None):
        screen = _getScreenSize()
        self.component.size = screen
        self.onOffsetUpdate(screen, True)

    def setVisible(self, isVisible):
        self.component.visible = isVisible

    def offset(self, value = None):
        if value is not None and self.offsetChanged(value, self._offset):
            self._offset = value
            self.onOffsetUpdate(_getScreenSize())
        else:
            return self._offset
        return

    def offsetChanged(self, offset1, offset2):
        if type(offset1) is Math.Vector2 and type(offset2) is Math.Vector2:
            return abs(offset1.x - offset2.x) > Aim.EPSILON or abs(offset1.y - offset2.y) > Aim.EPSILON
        return abs(offset1[0] - offset2[0]) > Aim.EPSILON or abs(offset1[1] - offset2[1]) > Aim.EPSILON

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
        correction = self._reloadingHndl.state.get('correction')
        startTime = self._reloadingHndl.state.get('startTime', 0)
        duration = self._reloadingHndl.state.get('duration', 0)
        if correction is not None:
            startTime = correction.get('startTime', 0)
            duration = correction.get('timeRemaining', 0)
        if startTime is not None:
            current = BigWorld.time()
            return duration - (current - startTime)
        else:
            return 0

    def getAmmoQuantityLeft(self):
        ammo = self._reloadingHndl.ammoStock
        if self.isCasseteClip():
            return ammo[1]
        else:
            return ammo[0]

    def isCasseteClip(self):
        clip = _g_aimState['clip']
        return clip[0] != 1 or clip[1] != 1

    def setReloading(self, duration, startTime = None, baseTime = None):
        _isReloading = self._reloadingHndl.state.get('isReloading', False)
        _startTime = self._reloadingHndl.state.get('startTime', 0)
        _duration = self._reloadingHndl.state.get('duration', 0)
        isReloading = duration != 0
        self._reloadingHndl.state['isReloading'] = isReloading
        self._reloadingHndl.state['correction'] = None
        self._reloadingHndl.state['baseTime'] = baseTime
        if _isReloading and duration > 0 and _duration > 0 and _startTime > 0:
            current = BigWorld.time()
            self._reloadingHndl.state['correction'] = {'timeRemaining': duration,
             'startTime': current,
             'startPosition': (current - _startTime) / _duration}
            self._flashCall('updateReloadingBaseTime', [baseTime, False])
            self._correctReloadingTime(duration)
        else:
            self._reloadingHndl.state['duration'] = duration
            self._reloadingHndl.state['startTime'] = BigWorld.time() if isReloading else None
            self._setReloading(duration, 0, isReloading, None, baseTime)
        return

    def setHealth(self, current):
        state = _g_aimState['health']
        state['cur'] = current
        if state['max'] is None:
            state['max'] = float(BigWorld.player().vehicleTypeDescriptor.maxHealth)
        self._setHealth(state['cur'], state['max'])
        return

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
        if _g_aimState['clip'] != (capacity, burst):
            _g_aimState['clip'] = (capacity, burst)
            self._setClipParams(capacity, burst)

    def showHit(self, gYaw, isDamage):
        _g_aimState['hitIndicators'].append({'gYaw': gYaw,
         'startTime': BigWorld.time(),
         'isDamage': isDamage})
        self._showHit(_g_aimState['hitIndicators'][-1:][0])

    def isGunReload(self):
        return self._reloadingHndl.state.get('isReloading', False)

    def onCameraChange(self):
        self._reloadingHndl.onAimChanged(self)
        if not self.isGunReload():
            baseTime = self._reloadingHndl.state.get('baseTime', -1)
            self._flashCall('updateReloadingBaseTime', [baseTime, True])
        elif not self._reloadingHndl.state['correction']:
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

    def setReloadingInPercent(self, percent, isReloading = True):
        self._setReloadingAsPercent(percent, isReloading)

    def _setReloading(self, duration, startTime = None, isReloading = True, correction = None, baseTime = None):
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

    def _setReloadingAsPercent(self, percent, isReloading = True):
        self._flashCall('setReloadingAsPercent', [percent, isReloading])

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
        newDistance = None
        targetID = _g_aimState['target']['id']
        if targetID is not None:
            targ = BigWorld.entity(targetID)
            if targ is None:
                self.clearTarget()
                LOG_ERROR('Invalid target ID')
            else:
                state = _g_aimState['target']
                newDistance = int((targ.position - BigWorld.player().getOwnVehiclePosition()).length)
                if newDistance != state['dist']:
                    state['dist'] = newDistance
                else:
                    newDistance = None
        return newDistance

    def _flashCall(self, funcName, args = None):
        self.call('Aim.' + funcName, args)

    def __refreshScale(self, scale):
        self.movie._root._xscale = 100 * scale
        self.movie._root._yscale = 100 * scale


class StrategicAim(Aim):

    def __init__(self, offset, isPostMortem = False):
        Aim.__init__(self, 'strategic', offset)
        self._distance = 0

    def _enable(self, state, isFirstInit):
        if isFirstInit:
            return
        else:
            self._distance = self._getAimDistance()
            self._flashCall('updateDistance', [self._distance])
            hs = state['health']
            self._setHealth(hs['cur'], hs['max'])
            ammoCtrl = g_sessionProvider.getAmmoCtrl()
            if ammoCtrl.isGunReloadTimeInPercent():
                self.setReloadingInPercent(ammoCtrl.getGunReloadTime(), False)
            elif self._reloadingHndl.state['startTime'] is not None:
                self._setReloading(self._reloadingHndl.state['duration'], startTime=BigWorld.time() - self._reloadingHndl.state['startTime'], correction=self._reloadingHndl.state['correction'])
            else:
                self._setReloading(self._reloadingHndl.state['duration'], 0, False)
            capacity, burst = state['clip']
            self._setClipParams(capacity, burst)
            self._setAmmoStock(*self._reloadingHndl.ammoStock)
            return

    def _update(self):
        newDistance = self._getAimDistance()
        if newDistance != self._distance:
            self._distance = newDistance
            self._flashCall('updateDistance', [self._distance])

    def _clearTarget(self, startTime):
        pass

    def _getAimDistance(self):
        x, y, z = BigWorld.player().gunRotator.markerInfo[0]
        v = BigWorld.player().getOwnVehiclePosition() - Math.Vector3(x, y, z)
        return int(v.length)


class PostMortemAim(Aim):

    def __init__(self, offset):
        Aim.__init__(self, 'postmortem', offset)
        self.__msgCaption = i18n.makeString(INGAME_GUI.PLAYER_MESSAGES_POSTMORTEM_CAPTION)

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
        if self.__vID is not None:
            vehicle = BigWorld.entity(self.__vID)
            if vehicle is not None:
                playerName = g_sessionProvider.getCtx().getFullPlayerName(vID=self.__vID, showVehShortName=False)
                type = Vehicle.getUserName(vehicleType=vehicle.typeDescriptor.type, textPrefix=True)
                healthPercent = math.ceil(100.0 * max(0, vehicle.health) / vehicle.typeDescriptor.maxHealth)
                self.__setText(playerName, type, healthPercent)
        return

    def __setText(self, name, type, health):
        isPlayer = self.__vID == BigWorld.player().playerVehicleID
        caption = makeHtmlString('html_templates:battle/postmortemMessages', 'player' if isPlayer else 'ally', {'message': i18n.makeString(INGAME_GUI.PLAYER_MESSAGES_POSTMORTEM_CAPTION_SELF) if isPlayer else self.__msgCaption})
        Aim._flashCall(self, 'updatePlayerInfo', [caption % {'name': name,
          'type': type,
          'health': health}])


class ArcadeAim(Aim):

    def __init__(self, offset, isSniper):
        Aim.__init__(self, 'sniper' if isSniper else 'arcade', offset)
        self.__isSniper = isSniper

    def _enable(self, state, isFirstInit):
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
            ammoCtrl = g_sessionProvider.getAmmoCtrl()
            if ammoCtrl.isGunReloadTimeInPercent():
                self.setReloadingInPercent(ammoCtrl.getGunReloadTime(), False)
            elif self._reloadingHndl.state['startTime'] is not None:
                self._setReloading(self._reloadingHndl.state['duration'], startTime=BigWorld.time() - self._reloadingHndl.state['startTime'], correction=self._reloadingHndl.state['correction'])
            else:
                self._setReloading(self._reloadingHndl.state['duration'], 0, False)
            capacity, burst = state['clip']
            self._setClipParams(capacity, burst)
            self._setAmmoStock(*self._reloadingHndl.ammoStock)
            return

    def _update(self):
        distance = Aim._update(self)
        if distance is not None:
            Aim._flashCall(self, 'updateTarget', [distance])
        return


class FalloutDeathAim(Aim):

    def __init__(self, offset):
        super(FalloutDeathAim, self).__init__('falloutdeath', offset)
        self.__msgCaption = i18n.makeString('#ingame_gui:player_messages/postmortem_caption')

    def create(self):
        super(FalloutDeathAim, self).create()

    def destroy(self):
        super(FalloutDeathAim, self).destroy()

    def onSettingsChanged(self, diff = None):
        super(FalloutDeathAim, self).onSettingsChanged(diff)


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
     'hitIndicators': [],
     'clip': (1, 1),
     'health': {'cur': None,
                'max': None}}
    return


_g_aimState = None
