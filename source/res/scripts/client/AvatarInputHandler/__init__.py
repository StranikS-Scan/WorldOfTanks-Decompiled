# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/__init__.py
# Compiled at: 2018-12-11 23:56:21
import weakref
import BigWorld, Math, ResMgr
import game
import Keys, GUI
from Event import Event
from debug_utils import *
from gui.Scaleform.CursorDelegator import g_cursorDelegator
from post_processing.post_effect_controllers import g_postProcessingEvents
import control_modes
import constants
import cameras
import BattleReplay
from constants import ARENA_PERIOD, AIMING_MODE
_INPUT_HANDLER_CFG = 'gui/avatar_input_handler.xml'
_CTRLS_FIRST = 'arcade'
_CTRLS_DESC_MAP = {'arcade': ('ArcadeControlMode', 'arcadeMode', False),
 'strategic': ('StrategicControlMode', 'strategicMode', False),
 'sniper': ('SniperControlMode', 'sniperMode', False),
 'postmortem': ('PostMortemControlMode', 'postMortemMode', False),
 'debug': ('DebugControlMode', None, True),
 'cat': ('CatControlMode', None, True)}

class AvatarInputHandler(object):
    aim = property(lambda self: self.__curCtrl.getAim())
    ctrl = property(lambda self: self.__curCtrl)
    ctrls = property(lambda self: self.__ctrls)
    isSPG = property(lambda self: self.__isSPG)
    isATSPG = property(lambda self: self.__isATSPG)

    def __init__(self):
        sec = self._readCfg()
        self.onCameraChanged = Event()
        self.onPostmortemVehicleChanged = Event()
        self.__isArenaStarted = False
        self.__isStarted = False
        self.__targeting = _Targeting()
        self.__ctrls = dict()
        self.__killerVehicleID = None
        self.__isAutorotation = True
        self.__prevModeAutorotation = None
        self.__isSPG = False
        self.__isATSPG = False
        self.__setupCtrls(sec)
        self.__curCtrl = self.__ctrls[_CTRLS_FIRST]
        self.__detachCount = 0
        return

    def prerequisites(self):
        out = []
        for ctrl in self.__ctrls.itervalues():
            out += ctrl.prerequisites()

        return out

    def handleKeyEvent(self, event):
        cursorDetached = self.__detachCount < 0
        isDown, key, mods, isRepeat = game.convertKeyEvent(event)
        if isRepeat:
            return False
        if self.__isStarted and cursorDetached:
            return BigWorld.player().handleKey(isDown, key, mods)
        if not self.__isStarted or cursorDetached:
            return False
        if self.__curCtrl.handleKeyEvent(isDown, key, mods, event):
            return True
        return BigWorld.player().handleKey(isDown, key, mods)

    def handleMouseEvent(self, dx, dy, dz):
        if not self.__isStarted or self.__detachCount < 0:
            return False
        return self.__curCtrl.handleMouseEvent(dx, dy, dz)

    def detachCursor(self, isDetached):
        if not self.__isStarted:
            return
        self.__detachCount += -1 if isDetached else 1
        assert self.__detachCount <= 0
        if self.__detachCount == -1 and isDetached:
            self.__targeting.enable(False)
            g_cursorDelegator.activateCursor()
            self.setAimingMode(False, AIMING_MODE.USER_DISABLED)
        elif not self.__detachCount:
            self.__targeting.enable(True)
            g_cursorDelegator.detachCursor()

    def updateShootingStatus(self, canShoot):
        if self.__detachCount < 0:
            return
        return self.__curCtrl.updateShootingStatus(canShoot)

    def getDesiredShotPoint(self):
        if self.__detachCount < 0:
            return None
        else:
            g_postProcessingEvents.onFocalPlaneChanged()
            return self.__curCtrl.getDesiredShotPoint()

    def showGunMarker(self, flag):
        self.__curCtrl.showGunMarker(flag)

    def showGunMarker2(self, flag):
        self.__curCtrl.showGunMarker2(flag)

    def updateGunMarker(self, pos, dir, size, relaxTime, collData):
        aim = self.__curCtrl.getAim()
        if aim is not None:
            aim.updateMarkerPos(pos, relaxTime)
        self.__curCtrl.updateGunMarker(pos, dir, size, relaxTime, collData)
        return

    def updateGunMarker2(self, pos, dir, size, relaxTime, collData):
        self.__curCtrl.updateGunMarker2(pos, dir, size, relaxTime, collData)

    def setAimingMode(self, enable, mode):
        self.__curCtrl.setAimingMode(enable, mode)

    def setAutorotation(self, bValue):
        if self.__curCtrl.getFixedAutorotation() is not None:
            return
        elif not BigWorld.player().isOnArena:
            return
        else:
            if self.__isAutorotation != bValue:
                self.__isAutorotation = bValue
                BigWorld.player().enableOwnVehicleAutorotation(self.__isAutorotation)
            return

    def getAutorotation(self):
        return self.__isAutorotation

    def switchAutorotation(self):
        if self.__curCtrl.getFixedAutorotation() is not None:
            return
        elif not BigWorld.player().isOnArena:
            return
        else:
            self.__isAutorotation = not self.__isAutorotation
            BigWorld.player().enableOwnVehicleAutorotation(self.__isAutorotation)
            return

    def activatePostmortem(self):
        try:
            params = self.__curCtrl.postmortemCamParams
        except:
            params = None

        self.onControlModeChanged('postmortem', postmortemParams=params, bPostmortemDelay=True)
        return

    def setKillerVehicleID(self, killerVehicleID):
        self.__killerVehicleID = killerVehicleID

    def getKillerVehicleID(self):
        return self.__killerVehicleID

    def start(self):
        game.g_guiResetters.add(self.__onRecreateDevice)
        import aims
        aims.clearState()
        ownVehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        self.__isSPG = 'SPG' in ownVehicle.typeDescriptor.type.tags
        self.__isATSPG = 'AT-SPG' in ownVehicle.typeDescriptor.type.tags
        for control in self.__ctrls.itervalues():
            control.create()

        g_cursorDelegator.detachCursor()
        if not self.__curCtrl.isManualBind():
            BigWorld.player().positionControl.bindToVehicle(True)
        self.__curCtrl.enable(ctrlState=control_modes.dumpStateEmpty())
        self.onCameraChanged('arcade')
        tmp = self.__curCtrl.getFixedAutorotation()
        if tmp is not None:
            self.__isAutorotation = tmp
            self.__prevModeAutorotation = True
        else:
            self.__isAutorotation = True
            self.__prevModeAutorotation = None
        BigWorld.player().enableOwnVehicleAutorotation(self.__isAutorotation)
        self.__targeting.enable(True)
        self.__isStarted = True
        self.__isGUIVisible = True
        self.__killerVehicleID = None
        arena = BigWorld.player().arena
        arena.onPeriodChange += self.__onArenaStarted
        self.__onArenaStarted(arena.period)
        return

    def stop(self):
        self.__isStarted = False
        for control in self.__ctrls.itervalues():
            control.destroy()

        BigWorld.player().positionControl.bindToVehicle(False)
        self.onCameraChanged = None
        self.__targeting.enable(False)
        self.__killerVehicleID = None
        game.g_guiResetters.remove(self.__onRecreateDevice)
        BigWorld.player().arena.onPeriodChange -= self.__onArenaStarted
        return

    def onControlModeChanged(self, eMode, **args):
        if not self.__isArenaStarted and eMode != 'postmortem':
            return
        else:
            player = BigWorld.player()
            ctrl = BattleReplay.g_replayCtrl
            if ctrl.isRecording:
                ctrl.setControlMode(eMode)
            ctrlState = self.__curCtrl.dumpState()
            self.__curCtrl.disable()
            prevCtrl = self.__curCtrl
            self.__curCtrl = self.__ctrls[eMode]
            if player is not None:
                if not prevCtrl.isManualBind() and self.__curCtrl.isManualBind():
                    player.positionControl.bindToVehicle(False)
                if prevCtrl.isManualBind() and not self.__curCtrl.isManualBind():
                    player.positionControl.bindToVehicle(True)
                if not prevCtrl.isManualBind() and not self.__curCtrl.isManualBind():
                    if prevCtrl is self.__curCtrl:
                        player.positionControl.bindToVehicle(False)
                        player.positionControl.bindToVehicle(True)
            if player is not None:
                curFixed = self.__curCtrl.getFixedAutorotation()
                if curFixed is not None:
                    if prevCtrl.getFixedAutorotation() is None:
                        self.__prevModeAutorotation = self.__isAutorotation
                    if self.__isAutorotation != curFixed:
                        self.__isAutorotation = curFixed
                        BigWorld.player().enableOwnVehicleAutorotation(self.__isAutorotation)
                elif prevCtrl.getFixedAutorotation() is not None:
                    if self.__prevModeAutorotation is None:
                        self.__prevModeAutorotation = True
                    if self.__isAutorotation != self.__prevModeAutorotation:
                        self.__isAutorotation = self.__prevModeAutorotation
                        BigWorld.player().enableOwnVehicleAutorotation(self.__isAutorotation)
                    self.__prevModeAutorotation = None
            cameras.SniperCamera._USE_SWINGING = BigWorld.wg_isSniperModeSwingingEnabled()
            self.__curCtrl.enable(ctrlState=ctrlState, **args)
            self.onCameraChanged(eMode)
            self.__targeting.onRecreateDevice()
            aim = self.aim
            GUI.mcursor().position = aim.offset() if aim is not None else (0, 0)
            self.__curCtrl.setGUIVisible(self.__isGUIVisible)
            return

    def getTargeting(self):
        return self.__targeting

    def setGUIVisible(self, isVisible):
        self.__isGUIVisible = isVisible
        self.__curCtrl.setGUIVisible(isVisible)

    def onMinimapClicked(self, worldPos):
        self.__curCtrl.onMinimapClicked(worldPos)

    def setReloading(self, duration, startTime=None):
        self.__curCtrl.setReloading(duration, startTime)
        if self.aim is not None:
            self.aim.setReloading(duration, startTime)
        return

    def attachBattleWindow(self, parentUI):
        weakRef = weakref.ref(parentUI)
        for ctrl in self.__ctrls.itervalues():
            aim = ctrl.getAim()
            if aim:
                aim.attachTankIndicator(weakRef)
                aim.attachCruiseCtrl(weakRef)

    def _readCfg(self):
        sec = ResMgr.openSection(_INPUT_HANDLER_CFG)
        if sec is None:
            LOG_ERROR('can not open <%s>.' % _INPUT_HANDLER_CFG)
            return
        else:
            self.__checkSections(sec)
            return sec

    def __setupCtrls(self, section):
        for name, desc in _CTRLS_DESC_MAP.items():
            if not desc[2] or desc[2] and constants.HAS_DEV_RESOURCES:
                if name not in self.__ctrls:
                    self.__ctrls[name] = getattr(control_modes, desc[0])(section[desc[1]] if desc[1] else None, self)

        return

    def __checkSections(self, section):
        for name, desc in _CTRLS_DESC_MAP.items():
            if desc[1] is None or desc[2] and not constants.HAS_DEV_RESOURCES:
                continue
            if not section.has_key(desc[1]):
                LOG_ERROR('Invalid section <%s> in <%s>.' % (desc[1], _INPUT_HANDLER_CFG))

        return

    def __onArenaStarted(self, period, *args):
        self.__isArenaStarted = True if period == ARENA_PERIOD.BATTLE else False
        self.__curCtrl.showGunMarker(self.__isArenaStarted)

    def __onRecreateDevice(self):
        self.__curCtrl.onRecreateDevice()
        self.__targeting.onRecreateDevice()


class _Targeting():

    def __init__(self):
        target = BigWorld.target
        target.selectionFovDegrees = 1.0
        target.deselectionFovDegrees = 80.0
        target.maxDistance = 710.0
        target.skeletonCheckEnabled = True
        BigWorld.target.isEnabled = False
        self.__mouseMatProv = BigWorld.MouseTargettingMatrix()

    def isEnabled(self):
        return BigWorld.target.isEnabled

    def getTargetEntity(self):
        return BigWorld.target.entity

    def enable(self, flag):
        if flag and not BigWorld.target.isEnabled:
            BigWorld.target.isEnabled = True
            BigWorld.target.source = self.__mouseMatProv
        elif not flag:
            BigWorld.target.isEnabled = False
            BigWorld.target.clear()
            BigWorld.target.source = None
        return

    def onRecreateDevice(self):
        if BigWorld.target.isEnabled:
            BigWorld.target.clear()
