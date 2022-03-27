# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/rts_bw_ctrl.py
import typing
from collections import namedtuple
import aih_constants
import BigWorld
import GenericComponents
import CGF
import BattleReplay
from AvatarInputHandler import aih_global_binding
from RTSShared import COMMAND_NAME
from Event import Event, EventManager
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.commander.common import BaseHighlightType, ALLY_INVADERS_RADIUS_EPS
from gui.battle_control.controllers.commander.cursor import getRTSMCursorPosition
from gui.battle_control.controllers.commander.interfaces import IRTSBWController
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from PlayerEvents import g_playerEvents
from scene import StaticControlPointFeature
from rts.base_highlight import BaseHighlightComponent
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from Triggers import CylinderAreaComponent
if typing.TYPE_CHECKING:
    from typing import List, Optional, Set
    from gui.battle_control.controllers.commander.interfaces import IProxyVehiclesManager
CURSOR_DEFAULT = 'arrow'
CURSOR_LOF = 'commanderLineOfFire'
CURSOR_ATTACK = 'commanderAttack'
CURSOR_DEFEND = 'commanderDefend'
CURSOR_ATTACK_VEHICLE = 'commanderAttackVehicle'
CURSOR_APPEND_ORDER = 'commanderAppendOrder'
CURSOR_FALLBACK_ORDER = 'commanderFallbackOrder'
CURSOR_FORCE_ORDER = 'commanderForceOrder'
BaseInfo = namedtuple('BaseInfo', ('baseID',
 'team',
 'transform',
 'radius'))

class MouseInfo(object):

    def __init__(self, mouseWheel=True, mouseScroll=True, mouseLeft=True, mouseRight=True, mouseDoubleRight=True):
        self.mouseWheelEnabled = mouseWheel
        self.mouseScrollEnabled = mouseScroll
        self.mouseLeftEnabled = mouseLeft
        self.mouseRightEnabled = mouseRight
        self.mouseDoubleRightEnabled = mouseDoubleRight


class RTSBWController(CallbackDelayer, IRTSBWController):
    __aihCtrlModeName = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.CTRL_MODE_NAME)
    __dynamicObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RTSBWController, self).__init__()
        self.__helper = BigWorld.WGCommanderHelper()
        self.__controlPoints = None
        self.__baseInfo = None
        self.__isMouseOverUI = True
        self.__isMouseOverUIMinimap = False
        self.__isMinimapDefendMode = False
        self.__isMinimapAttackMode = False
        self.__isAppendMode = False
        self.__currentCursor = None
        self.__capturingControlPoints = set()
        self.__mouseInfo = MouseInfo()
        self.__isActive = False
        self.__eventManager = EventManager()
        self.onControlPointsReady = Event(self.__eventManager)
        self.onTeamBaseStateChanged = Event(self.__eventManager)
        return

    @property
    def controlPoint(self):
        return self.__baseInfo

    @property
    def controlPoints(self):
        return self.__controlPoints

    @property
    def capturingControlPoints(self):
        return self.__capturingControlPoints

    def getControllerID(self):
        return BATTLE_CTRL_ID.RTS_BW_CTRL

    def startControl(self, *_):
        g_playerEvents.onAvatarReady += self.__onAvatarReady
        g_playerEvents.onAvatarBecomeNonPlayer += self.__onAvatarBecomeNonPlayer

    def stopControl(self):
        self.__onDisabled()
        self.__isActive = False
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__onAvatarBecomeNonPlayer
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        self.__eventManager.clear()

    def setMouseInfo(self, info):
        self.__mouseInfo = info

    def setMouseWheelEnabled(self, enabled):
        self.__mouseInfo.mouseWheelEnabled = enabled

    def setMouseRightEnabled(self, enabled):
        self.__mouseInfo.mouseRightEnabled = enabled

    def setMouseScrollEnabled(self, enabled):
        self.__mouseInfo.mouseScrollEnabled = enabled

    def setMouseDoubleRightEnabled(self, enabled):
        self.__mouseInfo.mouseDoubleRightEnabled = enabled

    def getMouseInfo(self):
        return self.__mouseInfo

    def setMouseOverUI(self, isOverUI):
        self.__isMouseOverUI = isOverUI

    def isMouseOverUIMinimap(self):
        return self.__isMouseOverUIMinimap

    def setMouseOverUIMinimap(self, isOverUIMinimap):
        self.__isMouseOverUIMinimap = isOverUIMinimap
        BigWorld.wgHandleMouseOverMinimap(self.__isMouseOverUIMinimap)
        if self.__isMouseOverUIMinimap:
            self.__sessionProvider.dynamic.rtsCommander.vehicles.setFocusVehicleToNone()

    def isMouseOverUIMinimapEntry(self):
        return self.__isMinimapAttackMode or self.__isMinimapDefendMode

    def setMinimapDefendMode(self, defend):
        self.__isMinimapDefendMode = defend

    def setMinimapAttackMode(self, attack):
        self.__isMinimapAttackMode = attack

    def toggleAppendDisplay(self, isAppendMode):
        self.__isAppendMode = isAppendMode

    def getTeamBaseInvaders(self, baseID, team):
        invaders = []
        surrounding = []
        vehicles = [ v for v in BigWorld.player().vehicles if v.publicInfo['team'] != team and v.isAlive() and not self.__sessionProvider.getCtx().isObserver(v.id) and not v.isSupply() ]
        for baseInfo in self.__controlPoints:
            if baseInfo.baseID == baseID and baseInfo.team == team:
                baseRadius = baseInfo.radius
                surroundingRadius = baseRadius + ALLY_INVADERS_RADIUS_EPS
                for veh in vehicles:
                    distance = veh.position.distTo(baseInfo.transform.translation)
                    if distance < baseRadius:
                        invaders.append(veh.id)
                    if distance < surroundingRadius:
                        surrounding.append(veh.id)

                break

        return (invaders, surrounding)

    def __onAvatarReady(self):
        self.__controlPoints = self.__loadBaseHighlight()
        self.onControlPointsReady(self.__controlPoints)
        self.delayCallback(0.0, self.__update)
        BigWorld.player().arena.onTeamBasePointsUpdate += self.__onTeamBasePointsUpdate

    def __onAvatarBecomeNonPlayer(self):
        BigWorld.player().arena.onTeamBasePointsUpdate -= self.__onTeamBasePointsUpdate
        self.stopCallback(self.__update)

    def __update(self):
        wasActive = self.__isActive
        isEnabled = self.__isEnabled()
        if wasActive != isEnabled:
            self.__isActive = isEnabled
            if wasActive:
                self.__onDisabled()
        if isEnabled:
            self.__updateCollision()
            self.__updateCursor()
            self.__updateBaseHighLight()

    def __isEnabled(self):
        return self.__aihCtrlModeName in aih_constants.CTRL_MODE_NAME.COMMANDER_MODES

    def __onDisabled(self):
        self.__currentCursor = CURSOR_DEFAULT
        avatar = BigWorld.player()
        if avatar is None or not avatar.spaceID:
            return
        else:
            query = CGF.Query(avatar.spaceID, BaseHighlightComponent)
            for baseComponent in query:
                baseComponent.setHovered(False)

            return

    def __updateCollision(self):
        if not self.__sessionProvider.dynamic.rtsCommander.vehicles.hasSelection:
            return
        else:
            spaceID = BigWorld.player().spaceID
            x, y = getRTSMCursorPosition()
            collideResult = self.__helper.collide2d(spaceID, x, y)
            if collideResult and not self.isMouseOverUIMinimap():
                feature = _getStaticControlPointFeature(spaceID)
                self.__baseInfo = feature.collide(collideResult.closestPoint)
            else:
                self.__baseInfo = None
            return

    def __updateCursor(self):
        cursorId = CURSOR_DEFAULT
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        vehicles = rtsCommander.vehicles
        minimapInteraction = self.__isMouseOverUIMinimap or self.isMouseOverUIMinimapEntry()
        if vehicles.hasSelection:
            if not self.__isMouseOverUI or minimapInteraction:
                canQueueMove = vehicles.canQueueCommand(COMMAND_NAME.MOVE)
                isAppendAvailable = canQueueMove and self.__sessionProvider.dynamic.rtsCommander.isAppendModeEnabled and self.__isAppendMode
                if rtsCommander.isRetreatModeActive:
                    cursorId = CURSOR_FALLBACK_ORDER
                elif rtsCommander.isForceOrderModeActive:
                    cursorId = CURSOR_FORCE_ORDER
                elif self.isMouseOverUIMinimapEntry() and canQueueMove:
                    if self.__isMinimapDefendMode:
                        cursorId = CURSOR_DEFEND
                    elif self.__isMinimapAttackMode:
                        cursorId = CURSOR_ATTACK
                elif not self.__isMouseOverUIMinimap:
                    replayCtrl = BattleReplay.g_replayCtrl
                    if not replayCtrl.isPlaying and BigWorld.player().inputHandler.ctrl.isTrajectoriesVisible:
                        cursorId = CURSOR_LOF
                    elif vehicles.getAliveNearCursor(lambda e: e.isEnemy) is not None:
                        cursorId = CURSOR_ATTACK_VEHICLE
                    elif self.__baseInfo and vehicles.getAliveNearCursor(lambda e: e.isAlly) is None and canQueueMove:
                        _, baseTeamId = self.__baseInfo
                        cursorId = CURSOR_DEFEND if baseTeamId == BigWorld.player().team else CURSOR_ATTACK
                if cursorId == CURSOR_DEFAULT and isAppendAvailable:
                    cursorId = CURSOR_APPEND_ORDER
            return cursorId == self.__currentCursor and None
        else:
            self.__helper.setCursor(BigWorld.ALL_CURSORS[cursorId])
            self.__currentCursor = None if self.__isMouseOverUI and not minimapInteraction else cursorId
            return

    def __loadBaseHighlight(self):
        basesInfo = []
        player = BigWorld.player()
        feature = _getStaticControlPointFeature(player.spaceID)
        for controlPoint in feature.gameObjects():
            controlPointComponent = controlPoint.findComponentByType(BigWorld.WgControlPointComponent)
            baseId = controlPointComponent.baseId
            teamId = controlPointComponent.teamId
            baseType = BaseHighlightType.ALLY if teamId == player.team else BaseHighlightType.ENEMY
            ssmPaths = self.__dynamicObjectsCache.getConfig(self.__sessionProvider.arenaVisitor.getArenaGuiType()).getBaseHighlightSsmPaths()
            ssmPath = ssmPaths[baseType]
            controlPoint.createComponent(GenericComponents.AnimatorComponent, ssmPath, 0, 1, -1, True, '')
            highligter = controlPoint.createComponent(BaseHighlightComponent)
            highligter.id = baseId
            highligter.teamID = teamId
            highligter.animator = CGF.ComponentLink(controlPoint, GenericComponents.AnimatorComponent)
            transform = controlPoint.findComponentByType(GenericComponents.TransformComponent).worldTransform
            radius = controlPoint.findComponentByType(CylinderAreaComponent).radius
            basesInfo.append(BaseInfo(baseId, teamId, transform, radius))

        return basesInfo

    def __updateBaseHighLight(self):
        baseId, baseTeamId = (None, None)
        if self.__baseInfo is not None and self.__currentCursor in (CURSOR_DEFEND, CURSOR_ATTACK):
            baseId, baseTeamId = self.__baseInfo
        query = CGF.Query(BigWorld.player().spaceID, BaseHighlightComponent)
        for baseComponent in query:
            baseComponent.setHovered(baseId == baseComponent.id and baseTeamId == baseComponent.teamID)

        return

    def __onTeamBasePointsUpdate(self, team, baseID, points, *_):
        if points == 0:
            self.__capturingControlPoints.discard(baseID)
        else:
            self.__capturingControlPoints.add(baseID)
        invaders = []
        vehicles = [ v for v in BigWorld.player().vehicles if v.publicInfo['team'] != team and v.isAlive() and not self.__sessionProvider.getCtx().isObserver(v.id) and not v.isSupply() ]
        for baseInfo in self.__controlPoints:
            if baseInfo.baseID == baseID and baseInfo.team == team:
                checkDistance = baseInfo.radius + ALLY_INVADERS_RADIUS_EPS
                for veh in vehicles:
                    if veh.position.distTo(baseInfo.transform.translation) < checkDistance:
                        invaders.append(veh.id)

                break

        self.onTeamBaseStateChanged(team, baseID, points, invaders)


def _getStaticControlPointFeature(spaceID):
    return BigWorld.getScene(spaceID).getInstance(StaticControlPointFeature)
