# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/minimap/plugins.py
import logging
import math
from collections import defaultdict, namedtuple
from functools import partial
from enum import Enum
import BattleReplay
import BigWorld
import Keys
import Math
import aih_constants
from AvatarInputHandler import AvatarInputHandler
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import MINIMAP_IBC_HINT_SECTION, HINTS_LEFT
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.options import MinimapArtyHitSetting
from battleground.location_point_manager import g_locationPointManager
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES, ReplyState, MarkerType, LocationMarkerSubType, ONE_SHOT_COMMANDS_TO_REPLIES, INVALID_VEHICLE_POSITION
from constants import VISIBILITY, AOI
from debug_utils import LOG_WARNING, LOG_ERROR, LOG_DEBUG
from gui import GUI_SETTINGS, InputHandler
from gui.Scaleform.daapi.view.battle.shared.minimap import common
from gui.Scaleform.daapi.view.battle.shared.minimap import entries
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import ENTRY_SYMBOL_NAME, SettingsTypes
from gui.battle_control import avatar_getter, minimap_utils, matrix_factory
from gui.battle_control.arena_info.interfaces import IVehiclesAndPositionsController, IArenaVehiclesController
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, VEHICLE_LOCATION, VEHICLE_VIEW_STATE
from battle_royale.gui.battle_control.controllers.radar_ctrl import IRadarListener
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from ids_generators import SequenceIDGenerator
from shared_utils import findFirst
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.shared.formatters import normalizeHealthPercent
_logger = logging.getLogger(__name__)
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_FEATURES = settings.ADDITIONAL_FEATURES
_CTRL_MODE = aih_constants.CTRL_MODE_NAME
_LOCATION_SUBTYPE_TO_FLASH_SYMBOL_NAME = {LocationMarkerSubType.SPG_AIM_AREA_SUBTYPE: settings.ENTRY_SYMBOL_NAME.ARTY_MARKER,
 LocationMarkerSubType.GOING_TO_MARKER_SUBTYPE: settings.ENTRY_SYMBOL_NAME.LOCATION_MARKER,
 LocationMarkerSubType.PREBATTLE_WAYPOINT_SUBTYPE: settings.ENTRY_SYMBOL_NAME.LOCATION_MARKER,
 LocationMarkerSubType.ATTENTION_TO_MARKER_SUBTYPE: settings.ENTRY_SYMBOL_NAME.ATTENTION_MARKER,
 LocationMarkerSubType.SHOOTING_POINT_SUBTYPE: settings.ENTRY_SYMBOL_NAME.SHOOTING_POINT_MARKER,
 LocationMarkerSubType.NAVIGATION_POINT_SUBTYPE: settings.ENTRY_SYMBOL_NAME.NAVIGATION_POINT_MARKER}
_PING_FLASH_MINIMAP_SUBTYPES = {LocationMarkerSubType.GOING_TO_MARKER_SUBTYPE, LocationMarkerSubType.ATTENTION_TO_MARKER_SUBTYPE, LocationMarkerSubType.PREBATTLE_WAYPOINT_SUBTYPE}
_BASE_PING_RANGE = 63
_LOCATION_PING_RANGE = 30
_MINIMAP_MIN_SCALE_INDEX = 0
_MINIMAP_MAX_SCALE_INDEX = 5
_MINIMAP_LOCATION_MARKER_MIN_SCALE = 1.0
_MINIMAP_LOCATION_MARKER_MAX_SCALE = 0.72
_AOI_ESTIMATE_RADIUS = 450.0
_AOI_RADIUS_MARGIN = 50.0

class PersonalEntriesPlugin(common.SimplePlugin, IArenaVehiclesController):
    __slots__ = ('__isAlive', '__isObserver', '__playerVehicleID', '__viewPointID', '__animationID', '__deadPointID', '__cameraID', '__cameraIDs', '__yawLimits', '__circlesID', '__circlesVisibilityState', '__killerVehicleID', '__defaultViewRangeCircleSize')

    def __init__(self, parentObj):
        super(PersonalEntriesPlugin, self).__init__(parentObj)
        self.__isObserver = False
        self.__isAlive = False
        self.__playerVehicleID = 0
        self.__viewPointID = 0
        self.__animationID = 0
        self.__deadPointID = 0
        self.__cameraID = 0
        self.__cameraIDs = defaultdict(lambda : 0)
        self.__yawLimits = None
        self.__circlesID = None
        self.__circlesVisibilityState = 0
        self.__killerVehicleID = 0
        self.__defaultViewRangeCircleSize = None
        return

    def start(self):
        self.__playerVehicleID = self._arenaDP.getPlayerVehicleID()
        vInfo = self._arenaDP.getVehicleInfo()
        self.__isAlive = vInfo.isAlive()
        self.__isObserver = vInfo.isObserver()
        yawLimits = vInfo.vehicleType.turretYawLimits
        if yawLimits is not None and vInfo.isSPG():
            self.__yawLimits = (math.degrees(yawLimits[0]), math.degrees(yawLimits[1]))
        self.sessionProvider.addArenaCtrl(self)
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self.__onPostMortemSwitched
            ctrl.onVehicleStateUpdated += self._onVehicleStateUpdated
            ctrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapFeedbackReceived += self.__onMinimapFeedbackReceived
            ctrl.onVehicleFeedbackReceived += self._onVehicleFeedbackReceived
        handler = avatar_getter.getInputHandler()
        if isinstance(handler, AvatarInputHandler):
            handler.onPostmortemKillerVisionEnter += self.__onKillerVisionEnter
            handler.onPostmortemKillerVisionExit += self.__onKillerVisionExit
        super(PersonalEntriesPlugin, self).start()
        return

    def stop(self):
        self.sessionProvider.removeArenaCtrl(self)
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            ctrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
            ctrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapFeedbackReceived -= self.__onMinimapFeedbackReceived
            ctrl.onVehicleFeedbackReceived -= self._onVehicleFeedbackReceived
        handler = avatar_getter.getInputHandler()
        if isinstance(handler, AvatarInputHandler):
            handler.onPostmortemKillerVisionEnter -= self.__onKillerVisionEnter
            handler.onPostmortemKillerVisionExit -= self.__onKillerVisionExit
        super(PersonalEntriesPlugin, self).stop()
        return

    def initControlMode(self, mode, available):
        super(PersonalEntriesPlugin, self).initControlMode(mode, available)
        self.__cameraIDs.clear()
        iterator = self.__createCameraEntries(*available)
        for entryID, name, active in iterator:
            self.__cameraIDs[name] = entryID
            if active:
                self.__cameraID = entryID

        self.__updateViewPointEntry()
        self.__updateViewRangeCircle()
        self._updateDeadPointEntry()

    def updateControlMode(self, mode, vehicleID):
        super(PersonalEntriesPlugin, self).updateControlMode(mode, vehicleID)
        self.__updateCameraEntries()
        self.__updateViewPointEntry(vehicleID)
        self._updateDeadPointEntry()
        self._invalidateMarkup()

    def clearCamera(self):
        if self.__cameraID:
            self._setActive(self.__cameraID, False)
            self.__cameraID = 0
        if self.__viewPointID:
            self._setActive(self.__viewPointID, False)
            self._setActive(self.__animationID, False)

    def setSettings(self):
        if not self.__isAlive:
            self.__hideDirectionLine()
            return
        else:
            getter = self.settingsCore.getSetting
            if GUI_SETTINGS.showDirectionLine:
                value = getter(settings_constants.GAME.SHOW_VECTOR_ON_MAP)
                if not value:
                    self.__hideDirectionLine()
            if GUI_SETTINGS.showSectorLines and self.__yawLimits is not None:
                value = getter(settings_constants.GAME.SHOW_SECTOR_ON_MAP)
                if value and self.__viewPointID:
                    self._invoke(self.__viewPointID, 'setYawLimit', *self.__yawLimits)
            if not self.__isObserver and self.__isAlive:
                if self.__circlesID is None:
                    self.__updateViewRangeCircle()
                if self._canShowDrawRangeCircle():
                    self.__addDrawRangeCircle()
                if self._canShowMaxViewRangeCircle():
                    self.__addMaxViewRangeCircle()
                if self._canShowViewRangeCircle():
                    self.__addViewRangeCircle()
                if self._canShowMinSpottingRangeCircle():
                    self.__addMinSpottingRangeCircle()
                self._updateCirlcesState()
            return

    def updateSettings(self, diff):
        if not self.__isAlive:
            return
        if settings_constants.GAME.SHOW_VECTOR_ON_MAP in diff and GUI_SETTINGS.showDirectionLine:
            value = diff[settings_constants.GAME.SHOW_VECTOR_ON_MAP]
            if value:
                self.__showDirectionLine()
            else:
                self.__hideDirectionLine()
        if settings_constants.GAME.SHOW_SECTOR_ON_MAP in diff and GUI_SETTINGS.showSectorLines:
            value = diff[settings_constants.GAME.SHOW_SECTOR_ON_MAP]
            if value:
                self.__setupYawLimit()
            else:
                self.__clearYawLimit()
        if not self.__isObserver:
            if settings_constants.GAME.MINIMAP_DRAW_RANGE in diff:
                if self._canShowDrawRangeCircle():
                    self.__addDrawRangeCircle()
                else:
                    self.__removeDrawRangeCircle()
            if settings_constants.GAME.MINIMAP_MAX_VIEW_RANGE in diff:
                if self._canShowMaxViewRangeCircle():
                    self.__addMaxViewRangeCircle()
                else:
                    self.__removeMaxViewRangeCircle()
            if settings_constants.GAME.MINIMAP_MIN_SPOTTING_RANGE in diff:
                if self._canShowMinSpottingRangeCircle():
                    self.__addMinSpottingRangeCircle()
                else:
                    self.__removeMinSpottingRangeCircle()
            if settings_constants.GAME.MINIMAP_VIEW_RANGE in diff:
                if self._canShowViewRangeCircle():
                    self.__addViewRangeCircle()
                else:
                    self.__removeViewRangeCircle()
            self._updateCirlcesState()

    def setDefaultViewRangeCircleSize(self, size):
        self.__defaultViewRangeCircleSize = size

    def __onKillerVisionEnter(self, killerVehicleID):
        self.__killerVehicleID = killerVehicleID
        self.updateControlMode(_CTRL_MODE.POSTMORTEM, killerVehicleID)

    def __onKillerVisionExit(self):
        self.__killerVehicleID = 0
        self.updateControlMode(_CTRL_MODE.POSTMORTEM, 0)

    def _updateDirectionLine(self, active):
        if active:
            self.__showDirectionLine()
        else:
            self.__hideDirectionLine()

    def _updateYawLimits(self, active):
        if active:
            self.__setupYawLimit()
        else:
            self.__clearYawLimit()

    def _updateDeadPointEntry(self, active=True):
        isActive = not self.__isObserver and (not self.__isAlive or self._isInPostmortemMode())
        if self.__deadPointID:
            self._setActive(self.__deadPointID, active=isActive)
            return
        matrix = matrix_factory.makeOwnVehicleMatrix()
        self.__deadPointID = self._addEntry(_S_NAME.DEAD_POINT, _C_NAME.PERSONAL, matrix=matrix, active=isActive)

    def __createCameraEntries(self, *modes):
        self.__cameraIDs.clear()
        add = self._addEntry
        container = _C_NAME.PERSONAL
        if _CTRL_MODE.ARCADE in modes:
            if self._isInArcadeMode():
                matrix = matrix_factory.makeArcadeCameraMatrix()
                active = True
            else:
                matrix = None
                active = False
            name = _S_NAME.ARCADE_CAMERA
            entryID = add(name, container, matrix=matrix, active=active)
            if entryID:
                yield (entryID, name, active)
        if _CTRL_MODE.STRATEGIC in modes or _CTRL_MODE.ARTY in modes:
            if self._isInStrategicMode() or self._isInArtyMode():
                matrix = matrix_factory.makeStrategicCameraMatrix()
                active = True
            else:
                matrix = None
                active = False
            name = _S_NAME.STRATEGIC_CAMERA
            entryID = add(name, container, matrix=matrix, active=active, transformProps=settings.TRANSFORM_FLAG.FULL)
            if entryID:
                yield (entryID, name, active)
        if _CTRL_MODE.VIDEO in modes:
            if self._isInVideoMode():
                matrix = matrix_factory.makeDefaultCameraMatrix()
                active = True
            else:
                matrix = None
                active = False
            name = _S_NAME.VIDEO_CAMERA
            entryID = add(name, container, matrix=matrix, active=active)
            if entryID:
                yield (entryID, name, active)
        return

    def __updateCameraEntries(self):
        activateID = self.__cameraIDs[_S_NAME.ARCADE_CAMERA]
        if self._isInStrategicMode() or self._isInArtyMode():
            activateID = self.__cameraIDs[_S_NAME.STRATEGIC_CAMERA]
            matrix = matrix_factory.makeStrategicCameraMatrix()
        elif self._isInArcadeMode():
            matrix = matrix_factory.makeArcadeCameraMatrix()
        elif self._isInPostmortemMode():
            if self.__killerVehicleID:
                matrix = matrix_factory.getEntityMatrix(self.__killerVehicleID)
            else:
                matrix = matrix_factory.makePostmortemCameraMatrix()
        elif self._isInVideoMode():
            activateID = self.__cameraIDs[_S_NAME.VIDEO_CAMERA]
            matrix = matrix_factory.makeDefaultCameraMatrix()
            self._hideMarkup()
        else:
            matrix = matrix_factory.makeDefaultCameraMatrix()
        enableCameraEntry = self._enableCameraEntryInCtrlMode(self._ctrlMode)
        for entryID in self.__cameraIDs.itervalues():
            if activateID == entryID and enableCameraEntry:
                self._setMatrix(entryID, matrix)
                if self.__cameraID != entryID:
                    self._setActive(entryID, True)
                    self.__cameraID = entryID
            self._setActive(entryID, False)

    def __updateViewPointEntry(self, vehicleID=0):
        isActive = self._isInPostmortemMode() and vehicleID and vehicleID != self.__playerVehicleID or self._isInVideoMode() and self.__isAlive or not (self._isInPostmortemMode() or self._isInVideoMode() or self.__isObserver)
        if self.__killerVehicleID:
            ownMatrix = matrix_factory.getEntityMatrix(self.__killerVehicleID)
        else:
            ownMatrix = matrix_factory.makeAttachedVehicleMatrix()
        if self.__viewPointID:
            self._setActive(self.__viewPointID, active=isActive)
            self._setMatrix(self.__viewPointID, ownMatrix)
            self._setActive(self.__animationID, active=isActive)
            self._setMatrix(self.__animationID, ownMatrix)
            return
        self.__viewPointID = self._addEntry(_S_NAME.VIEW_POINT, _C_NAME.PERSONAL, matrix=ownMatrix, active=isActive)
        transformProps = settings.TRANSFORM_FLAG.DEFAULT
        transformProps ^= settings.TRANSFORM_FLAG.NO_ROTATION
        self.__animationID = self._addEntry(_S_NAME.ANIMATION, _C_NAME.PERSONAL, matrix=ownMatrix, active=isActive, transformProps=transformProps)

    def __updateViewRangeCircle(self):
        ownMatrix = matrix_factory.makeAttachedVehicleMatrix()
        isActive = not self.__isObserver and self.__isAlive
        if self.__circlesID:
            self._setActive(self.__circlesID, isActive)
            self._setMatrix(self.__circlesID, ownMatrix)
            return
        else:
            transformProps = settings.TRANSFORM_FLAG.DEFAULT
            transformProps ^= settings.TRANSFORM_FLAG.NO_ROTATION
            self.__circlesVisibilityState = 0
            self.__circlesID = self._addEntry(_S_NAME.VIEW_RANGE_CIRCLES, _C_NAME.PERSONAL, matrix=ownMatrix, active=isActive, transformProps=transformProps)
            width, height = self.__defaultViewRangeCircleSize, self.__defaultViewRangeCircleSize
            if self.__defaultViewRangeCircleSize is None:
                bottomLeft, upperRight = self._parentObj.getBoundingBox()
                width = upperRight[0] - bottomLeft[0]
                height = upperRight[1] - bottomLeft[1]
            self._invoke(self.__circlesID, settings.VIEW_RANGE_CIRCLES_AS3_DESCR.AS_INIT_ARENA_SIZE, width, height)
            return

    def _getViewPointID(self):
        return self.__viewPointID

    def _getAnimationID(self):
        return self.__animationID

    def _getDeadPointID(self):
        return self.__deadPointID

    def _getPlayerVehicleID(self):
        return self.__playerVehicleID

    def _getViewRangeCirclesID(self):
        return self.__circlesID

    def _getSelectedCameraID(self):
        return self.__cameraID

    def _getCameraIDs(self):
        return self.__cameraIDs

    def _isAlive(self):
        return self.__isAlive

    def _onVehicleStateUpdated(self, state, value):
        if state in (VEHICLE_VIEW_STATE.SWITCHING, VEHICLE_VIEW_STATE.RESPAWNING):
            self._hideMarkup()

    def _hideMarkup(self):
        self.__hideDirectionLine()
        self.__clearYawLimit()
        if self.__viewPointID:
            self._setActive(self.__viewPointID, False)
            self._setActive(self.__animationID, False)
        if self.__circlesID:
            self._setActive(self.__circlesID, False)

    def _invalidateMarkup(self, forceInvalidate=False):
        if not self.__isObserver and not forceInvalidate:
            return
        elif (self._ctrlVehicleID is None or not BigWorld.entities.has_key(self._ctrlVehicleID)) and not forceInvalidate:
            self._hideMarkup()
            return
        elif self._isInVideoMode():
            self._hideMarkup()
            return
        else:
            self.__updateViewPointEntry()
            self._setActive(self.__viewPointID, True)
            self._setActive(self.__animationID, True)
            getter = self.settingsCore.getSetting
            showDirectionLine = GUI_SETTINGS.showDirectionLine and getter(settings_constants.GAME.SHOW_VECTOR_ON_MAP)
            showDirectionLine = showDirectionLine and self._canShowDirectionLine()
            showYawLimit = GUI_SETTINGS.showSectorLines and getter(settings_constants.GAME.SHOW_SECTOR_ON_MAP)
            showCircles = self._canShowDrawRangeCircle() or self._canShowMaxViewRangeCircle() or self._canShowViewRangeCircle()
            if showDirectionLine:
                self.__showDirectionLine()
            else:
                self.__hideDirectionLine()
            self.__clearYawLimit()
            if showYawLimit:
                vInfo = self._arenaDP.getVehicleInfo(self._arenaDP.getAttachedVehicleID())
                yawLimits = vInfo.vehicleType.turretYawLimits
                if yawLimits is not None and vInfo.isSPG():
                    self.__yawLimits = (math.degrees(yawLimits[0]), math.degrees(yawLimits[1]))
                    self.__setupYawLimit()
            if showCircles:
                self.__updateViewRangeCircle()
                if self._canShowDrawRangeCircle():
                    self.__addDrawRangeCircle()
                else:
                    self.__removeDrawRangeCircle()
                if self._canShowMaxViewRangeCircle():
                    self.__addMaxViewRangeCircle()
                else:
                    self.__removeMaxViewRangeCircle()
                if self._canShowViewRangeCircle():
                    self.__addViewRangeCircle()
                else:
                    self.__removeViewRangeCircle()
                if self._canShowMinSpottingRangeCircle():
                    self.__addMinSpottingRangeCircle()
                else:
                    self.__removeMinSpottingRangeCircle()
                self._setActive(self.__circlesID, True)
            elif self.__circlesID is not None:
                self._setActive(self.__circlesID, False)
            return

    def updateVehiclesInfo(self, updated, arenaDP):
        attachedVehicleId = arenaDP.getAttachedVehicleID()
        for flags, vInfo in updated:
            if vInfo.vehicleID == attachedVehicleId and flags & INVALIDATE_OP.VEHICLE_INFO > 0:
                self._invalidateMarkup(forceInvalidate=True)
                break

    def _canShowViewRangeCircle(self):
        return self.settingsCore.getSetting(settings_constants.GAME.MINIMAP_VIEW_RANGE)

    def _canShowMaxViewRangeCircle(self):
        return self.settingsCore.getSetting(settings_constants.GAME.MINIMAP_MAX_VIEW_RANGE)

    def _canShowMinSpottingRangeCircle(self):
        return self.settingsCore.getSetting(settings_constants.GAME.MINIMAP_MIN_SPOTTING_RANGE)

    def _canShowDrawRangeCircle(self):
        return self.settingsCore.getSetting(settings_constants.GAME.MINIMAP_DRAW_RANGE)

    def _canShowDirectionLine(self):
        return True

    def _enableCameraEntryInCtrlMode(self, ctrlMode):
        return True

    def _updateCirlcesState(self):
        isActive = self.__circlesVisibilityState > 0
        self._setActive(self.__circlesID, isActive)

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.__isAlive = False
        self.__hideDirectionLine()
        self.__clearYawLimit()
        self.__updateViewPointEntry()
        self._updateDeadPointEntry()
        if not self.__isObserver and self.__circlesID:
            self.__removeAllCircles()

    def __onRespawnBaseMoving(self):
        self.__isAlive = True
        self.__isAlive = True
        self._invalidateMarkup(True)

    def __onMinimapFeedbackReceived(self, eventID, entityID, value):
        if eventID == FEEDBACK_EVENT_ID.MINIMAP_SHOW_MARKER and self.__animationID:
            if avatar_getter.getVehicleIDAttached() == entityID:
                marker, _ = value
                self._invoke(self.__animationID, 'setAnimation', marker)

    def _calcCircularVisionRadius(self):
        visibilityMinRadius = self._arenaVisitor.getVisibilityMinRadius()
        vehAttrs = self.sessionProvider.shared.feedback.getVehicleAttrs()
        return min(vehAttrs.get('circularVisionRadius', visibilityMinRadius), VISIBILITY.MAX_RADIUS)

    def _getViewRangeRadius(self):
        return self._calcCircularVisionRadius()

    def _onVehicleFeedbackReceived(self, eventID, _, __):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_ATTRS_CHANGED and self.__circlesVisibilityState & settings.CIRCLE_TYPE.VIEW_RANGE:
            self._invoke(self.__circlesID, settings.VIEW_RANGE_CIRCLES_AS3_DESCR.AS_UPDATE_DYN_CIRCLE, self._getViewRangeRadius())
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD and self.__isObserver and not BattleReplay.isServerSideReplay():
            self.__removeAllCircles()
            self.__hideDirectionLine()

    def __addDrawRangeCircle(self):
        if self.__circlesVisibilityState & settings.CIRCLE_TYPE.DRAW_RANGE:
            return
        self.__circlesVisibilityState |= settings.CIRCLE_TYPE.DRAW_RANGE
        self._invoke(self.__circlesID, settings.VIEW_RANGE_CIRCLES_AS3_DESCR.AS_ADD_MAX_DRAW_CIRCLE, settings.CIRCLE_STYLE.COLOR.DRAW_RANGE, settings.CIRCLE_STYLE.ALPHA, self._arenaVisitor.getVehicleCircularAoiRadius())

    def __removeDrawRangeCircle(self):
        self.__circlesVisibilityState &= ~settings.CIRCLE_TYPE.DRAW_RANGE
        self._invoke(self.__circlesID, settings.VIEW_RANGE_CIRCLES_AS3_DESCR.AS_DEL_MAX_DRAW_CIRCLE)

    def __addMaxViewRangeCircle(self):
        if self.__circlesVisibilityState & settings.CIRCLE_TYPE.MAX_VIEW_RANGE:
            return
        self.__circlesVisibilityState |= settings.CIRCLE_TYPE.MAX_VIEW_RANGE
        self._invoke(self.__circlesID, settings.VIEW_RANGE_CIRCLES_AS3_DESCR.AS_ADD_MAX_VIEW_CIRCLE, settings.CIRCLE_STYLE.COLOR.MAX_VIEW_RANGE, settings.CIRCLE_STYLE.ALPHA, VISIBILITY.MAX_RADIUS)

    def __removeMaxViewRangeCircle(self):
        self.__circlesVisibilityState &= ~settings.CIRCLE_TYPE.MAX_VIEW_RANGE
        self._invoke(self.__circlesID, settings.VIEW_RANGE_CIRCLES_AS3_DESCR.AS_DEL_MAX_VIEW_CIRCLE)

    def __addMinSpottingRangeCircle(self):
        if self.__circlesVisibilityState & settings.CIRCLE_TYPE.MIN_SPOTTING_RANGE:
            return
        self.__circlesVisibilityState |= settings.CIRCLE_TYPE.MIN_SPOTTING_RANGE
        self._invoke(self.__circlesID, settings.VIEW_RANGE_CIRCLES_AS3_DESCR.AS_ADD_MIN_SPOTTING_CIRCLE, settings.CIRCLE_STYLE.COLOR.MIN_SPOTTING_RANGE, settings.CIRCLE_STYLE.ALPHA, self._arenaVisitor.getVisibilityMinRadius())

    def __removeMinSpottingRangeCircle(self):
        self.__circlesVisibilityState &= ~settings.CIRCLE_TYPE.MIN_SPOTTING_RANGE
        self._invoke(self.__circlesID, settings.VIEW_RANGE_CIRCLES_AS3_DESCR.AS_DEL_MIN_SPOTTING_CIRCLE)

    def __addViewRangeCircle(self):
        if self.__circlesVisibilityState & settings.CIRCLE_TYPE.VIEW_RANGE:
            return
        self.__circlesVisibilityState |= settings.CIRCLE_TYPE.VIEW_RANGE
        self._invoke(self.__circlesID, settings.VIEW_RANGE_CIRCLES_AS3_DESCR.AS_ADD_DYN_CIRCLE, settings.CIRCLE_STYLE.COLOR.VIEW_RANGE, settings.CIRCLE_STYLE.ALPHA, self._getViewRangeRadius())

    def __removeViewRangeCircle(self):
        self.__circlesVisibilityState &= ~settings.CIRCLE_TYPE.VIEW_RANGE
        self._invoke(self.__circlesID, settings.VIEW_RANGE_CIRCLES_AS3_DESCR.AS_DEL_DYN_CIRCLE)

    def __removeAllCircles(self):
        self.__circlesVisibilityState = 0
        if self.__circlesID is not None:
            self._invoke(self.__circlesID, settings.VIEW_RANGE_CIRCLES_AS3_DESCR.AS_REMOVE_ALL_CIRCLES)
        return

    def __showDirectionLine(self):
        entryID = self.__cameraIDs[_S_NAME.ARCADE_CAMERA]
        if entryID:
            self._invoke(entryID, 'showDirectionLine')

    def __hideDirectionLine(self):
        entryID = self.__cameraIDs[_S_NAME.ARCADE_CAMERA]
        if entryID:
            self._invoke(entryID, 'hideDirectionLine')

    def __setupYawLimit(self):
        if self.__viewPointID and self.__yawLimits is not None:
            self._invoke(self.__viewPointID, 'setYawLimit', *self.__yawLimits)
        return

    def __clearYawLimit(self):
        if self.__viewPointID and self.__yawLimits is not None:
            self._invoke(self.__viewPointID, 'clearYawLimit')
        return


class ArenaVehiclesPlugin(common.EntriesPlugin, IVehiclesAndPositionsController):
    __slots__ = ('__playerVehicleID', '__isObserver', '__aoiToFarCallbacksIDs', '__destroyCallbacksIDs', '__flags', '__flagHpMinimap', '__showDestroyEntries', '__isDestroyImmediately', '__destroyDuration', '__isSPG', '__replayRegistrator', '__canShowVehicleHp', '__tempHealthStorage', '__aoiEstimateRadius')

    def __init__(self, parent):
        super(ArenaVehiclesPlugin, self).__init__(parent, clazz=entries.VehicleEntry)
        self.__playerVehicleID = 0
        self.__isObserver = False
        self.__isSPG = False
        self.__aoiEstimateRadius = 0
        self.__aoiToFarCallbacksIDs = {}
        self.__destroyCallbacksIDs = {}
        self.__flags = _FEATURES.OFF
        self.__flagHpMinimap = _FEATURES.OFF
        self.__canShowVehicleHp = False
        self.__showDestroyEntries = GUI_SETTINGS.showMinimapDeath
        self.__isDestroyImmediately = GUI_SETTINGS.permanentMinimapDeath
        self.__destroyDuration = GUI_SETTINGS.minimapDeathDuration / 1000.0
        self.__replayRegistrator = _ReplayRegistrator()
        if self.__showDestroyEntries and not self.__isDestroyImmediately and not self.__destroyDuration:
            self.__isDestroyImmediately = False
            LOG_WARNING('Gui setting permanentMinimapDeath is ignored because setting minimapDeathDuration is incorrect', self.__destroyDuration)
        self.__tempHealthStorage = {}

    def start(self):
        super(ArenaVehiclesPlugin, self).start()
        vInfo = self._arenaDP.getVehicleInfo()
        self.__playerVehicleID = self._arenaDP.getPlayerVehicleID()
        self.__isObserver = vInfo.isObserver()
        self.__isSPG = vInfo.isSPG()
        vehicleAoIRadius = self._arenaVisitor.getVehicleCircularAoiRadius()
        self.__aoiEstimateRadius = vehicleAoIRadius - _AOI_RADIUS_MARGIN if AOI.ENABLE_MANUAL_RULES else _AOI_ESTIMATE_RADIUS
        g_eventBus.addListener(events.GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=EVENT_BUS_SCOPE.BATTLE)
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapVehicleAdded += self.__onMinimapVehicleAdded
            ctrl.onMinimapVehicleRemoved += self.__onMinimapVehicleRemoved
            ctrl.onMinimapFeedbackReceived += self.__onMinimapFeedbackReceived
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        g_playerEvents.onTeamChanged += self.__onTeamChanged
        self.sessionProvider.addArenaCtrl(self)
        return

    def stop(self):
        while self.__aoiToFarCallbacksIDs:
            _, callbackID = self.__aoiToFarCallbacksIDs.popitem()
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        while self.__destroyCallbacksIDs:
            _, callbackID = self.__destroyCallbacksIDs.popitem()
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        self.sessionProvider.removeArenaCtrl(self)
        g_eventBus.removeListener(events.GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=EVENT_BUS_SCOPE.BATTLE)
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapVehicleAdded -= self.__onMinimapVehicleAdded
            ctrl.onMinimapVehicleRemoved -= self.__onMinimapVehicleRemoved
            ctrl.onMinimapFeedbackReceived -= self.__onMinimapFeedbackReceived
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        g_playerEvents.onTeamChanged -= self.__onTeamChanged
        super(ArenaVehiclesPlugin, self).stop()
        return

    def updateControlMode(self, mode, vehicleID):
        prevCtrlID = self._ctrlVehicleID
        super(ArenaVehiclesPlugin, self).updateControlMode(mode, vehicleID)
        if self._isInPostmortemMode() or self._isInVideoMode() or self._isInRespawnDeath():
            self.__switchToVehicle(prevCtrlID)

    def setSettings(self):
        value = self.settingsCore.getSetting(settings_constants.GAME.SHOW_VEH_MODELS_ON_MAP)
        self.__flags = settings.convertSettingToFeatures(value, self.__flags, settingsType=SettingsTypes.MinimapVehicles)
        vehicleHpSetting = self.settingsCore.getSetting(settings_constants.GAME.SHOW_VEHICLE_HP_IN_MINIMAP)
        self.__flagHpMinimap = settings.convertSettingToFeatures(vehicleHpSetting, self.__flagHpMinimap, settingsType=SettingsTypes.MinimapHitPoint)
        if _FEATURES.isOn(self.__flags):
            self.__showFeatures(True)
        if _FEATURES.isOn(self.__flagHpMinimap):
            self.__showMinimapHP(True)

    def updateSettings(self, diff):
        hasModelSetting = settings_constants.GAME.SHOW_VEH_MODELS_ON_MAP in diff
        hasHpSetting = settings_constants.GAME.SHOW_VEHICLE_HP_IN_MINIMAP in diff
        if not hasModelSetting and not hasHpSetting:
            return
        if hasHpSetting:
            vehicleHpSetting = diff[settings_constants.GAME.SHOW_VEHICLE_HP_IN_MINIMAP]
            self.__flagHpMinimap = settings.convertSettingToFeatures(vehicleHpSetting, self.__flagHpMinimap, settingsType=SettingsTypes.MinimapHitPoint)
        if hasModelSetting:
            value = diff[settings_constants.GAME.SHOW_VEH_MODELS_ON_MAP]
            self.__flags = settings.convertSettingToFeatures(value, self.__flags, settingsType=SettingsTypes.MinimapVehicles)
        self.__showFeatures(_FEATURES.isOn(self.__flags))
        self.__showMinimapHP(_FEATURES.isOn(self.__flagHpMinimap))

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(self._arenaDP)

    def invalidateVehiclesInfo(self, arenaDP):
        positions = self._arenaVisitor.getArenaPositions()
        getProps = arenaDP.getPlayerGuiProps
        handled = {self.__playerVehicleID}
        for vInfo in arenaDP.getVehiclesInfoIterator():
            vehicleID = vInfo.vehicleID
            handled.add(vehicleID)
            if vehicleID == self.__playerVehicleID or vInfo.isObserver() or not vInfo.isAlive():
                continue
            if vehicleID not in self._entries:
                model = self.__addEntryToPool(vehicleID, positions=positions)
            else:
                model = self._entries[vehicleID]
            if model is not None:
                self._setVehicleInfo(vehicleID, model, vInfo, getProps(vehicleID, vInfo.team), isSpotted=False)
                self._notifyVehicleAdded(vehicleID)

        for vehicleID in set(self._entries).difference(handled):
            self._delEntryEx(vehicleID)

        return

    def addVehicleInfo(self, vInfo, arenaDP):
        if not vInfo.isAlive() or vInfo.isObserver():
            return
        else:
            vehicleID = vInfo.vehicleID
            if vehicleID in self._entries:
                return
            model = self.__addEntryToPool(vehicleID, positions=self._arenaVisitor.getArenaPositions())
            if model is not None:
                self._setVehicleInfo(vehicleID, model, vInfo, arenaDP.getPlayerGuiProps(vehicleID, vInfo.team), isSpotted=False)
                if model.isActive():
                    self._setInAoI(model, True)
                self._notifyVehicleAdded(vehicleID)
            return

    def updateVehiclesInfo(self, updated, arenaDP):
        for flags, vInfo in updated:
            if vInfo.isObserver():
                continue
            vehicleID = vInfo.vehicleID
            if vehicleID in self._entries:
                entry = self._entries[vehicleID]
                if INVALIDATE_OP.VEHICLE_STATUS & flags > 0 and vInfo.isAlive() != entry.isAlive():
                    if vInfo.isAlive():
                        self.__setAlive(vehicleID, entry)
                    else:
                        self.__setDestroyed(vehicleID, entry)
                if vehicleID in self.__tempHealthStorage:
                    currHealth = self.__tempHealthStorage[vehicleID]
                    maxHealth = vInfo.vehicleType.maxHealth
                    if maxHealth >= currHealth:
                        del self.__tempHealthStorage[vehicleID]
                        self._onVehicleHealthChanged(vehicleID, currHealth, maxHealth)
                self._setVehicleInfo(vehicleID, entry, vInfo, arenaDP.getPlayerGuiProps(vehicleID, vInfo.team))

    def invalidateVehicleStatus(self, flags, vInfo, arenaDP):
        if vInfo.isObserver():
            return
        vehicleID = vInfo.vehicleID
        if vehicleID in self._entries and not vInfo.isAlive():
            self.__setDestroyed(vehicleID, self._entries[vehicleID])

    def invalidatePlayerStatus(self, flags, vInfo, arenaDP):
        if not vInfo.isAlive() or vInfo.isObserver():
            return
        vehicleID = vInfo.vehicleID
        if vehicleID in self._entries:
            entry = self._entries[vehicleID]
            guiLabel = arenaDP.getPlayerGuiProps(vehicleID, vInfo.team).name()
            self.__setGUILabel(entry, guiLabel)

    def getVehiclePosition(self, vehicleID):
        if vehicleID not in self._entries:
            return INVALID_VEHICLE_POSITION
        entry = self._entries[vehicleID]
        return INVALID_VEHICLE_POSITION if not entry.isInAoI() else Math.Matrix(entry.getMatrix()).translation

    def updatePositions(self, iterator):
        handled = set()
        for vInfo, position in iterator():
            vehicleID = vInfo.vehicleID
            handled.add(vehicleID)
            if vehicleID not in self._entries or not vInfo.isAlive():
                continue
            entry = self._entries[vehicleID]
            location = entry.getLocation()
            self.__clearAoIToFarCallback(vehicleID)
            if location == VEHICLE_LOCATION.FAR:
                entry.updatePosition(position)
                self.__setActive(entry, True)
            if location in (VEHICLE_LOCATION.UNDEFINED, VEHICLE_LOCATION.AOI_TO_FAR):
                self._setInAoI(entry, True)
                self.__setLocationAndMatrix(entry, VEHICLE_LOCATION.FAR, matrix_factory.makePositionMP(position))
                self.__setActive(entry, True)
                self._notifyVehicleAdded(vehicleID)
                if location is VEHICLE_LOCATION.UNDEFINED:
                    self.__showVehicleHp(vehicleID, entry.getID())

        for vehicleID in set(self._entries).difference(handled):
            entry = self._entries[vehicleID]
            if entry.getLocation() in (VEHICLE_LOCATION.FAR, VEHICLE_LOCATION.AOI_TO_FAR):
                self.__clearAoIToFarCallback(vehicleID)
                self._hideVehicle(entry)
                self._notifyVehicleRemoved(vehicleID)

    def _notifyVehicleAdded(self, vehicleID):
        pass

    def _notifyVehicleRemoved(self, vehicleID):
        pass

    def _getPlayerVehicleID(self):
        return self.__playerVehicleID

    def _setVehicleInfo(self, vehicleID, entry, vInfo, guiProps, isSpotted=False):
        vehicleType = vInfo.vehicleType
        classTag = vehicleType.classTag
        name = vehicleType.shortNameWithPrefix
        if classTag is not None:
            entry.setVehicleInfo(not guiProps.isFriend, guiProps.name(), classTag, vInfo.isAlive())
            animation = self.__getSpottedAnimation(entry, isSpotted)
            if animation:
                self.__playSpottedSound(entry)
            self._invoke(entry.getID(), 'setVehicleInfo', vehicleID, classTag, name, guiProps.name(), animation)
        return

    def _onVehicleHealthChanged(self, vehicleID, currH, maxH):
        if vehicleID not in self._entries:
            return
        if currH > maxH:
            self.__tempHealthStorage[vehicleID] = currH
            _logger.warning('Max Vehicle Health is less then current. Health will be updated after max health update')
            return
        self._invoke(self._entries[vehicleID].getID(), 'setVehicleHealth', normalizeHealthPercent(currH, maxH))

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_HEALTH:
            info = self.sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
            self._onVehicleHealthChanged(vehicleID, value[0], info.vehicleType.maxHealth)
        elif eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD:
            info = self.sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
            self._onVehicleHealthChanged(info, 0, info.vehicleType.maxHealth)

    def __addEntryToPool(self, vehicleID, location=VEHICLE_LOCATION.UNDEFINED, positions=None):
        if location != VEHICLE_LOCATION.UNDEFINED:
            matrix = matrix_factory.makeVehicleMPByLocation(vehicleID, location, positions or {})
            if matrix is None:
                location = VEHICLE_LOCATION.UNDEFINED
        else:
            matrix, location = matrix_factory.getVehicleMPAndLocation(vehicleID, positions or {})
        active = location != VEHICLE_LOCATION.UNDEFINED
        model = self._addEntryEx(vehicleID, _S_NAME.VEHICLE, _C_NAME.ALIVE_VEHICLES, matrix=matrix, active=active)
        if model is not None:
            model.setLocation(location)
        return model

    def __setGUILabel(self, entry, guiLabel):
        if entry.setGUILabel(guiLabel):
            self._invoke(entry.getID(), 'setGUILabel', guiLabel)

    def __setActive(self, entry, active):
        if entry.setActive(active):
            self._setActive(entry.getID(), active)

    def __setDestroyed(self, vehicleID, entry):
        self.__clearAoIToFarCallback(vehicleID)
        if self.__showDestroyEntries and entry.setAlive(False) and not entry.wasSpotted():
            isPermanent = self.__isDestroyImmediately
            if not isPermanent:
                self.__setDestroyCallback(vehicleID)
            self._move(entry.getID(), _C_NAME.DEAD_VEHICLES)
            self._invoke(entry.getID(), 'setDead', isPermanent)
        else:
            self.__setActive(entry, False)

    def __setAlive(self, vehicleID, entry):
        self.__clearDestroyCallback(vehicleID)
        self._move(entry.getID(), _C_NAME.ALIVE_VEHICLES)
        entry.setAlive(True)
        self._invoke(entry.getID(), 'setAlive')

    def __setLocationAndMatrix(self, entry, location, matrix=None):
        entry.setLocation(location)
        if matrix is not None:
            entry.setMatrix(matrix)
            self._setMatrix(entry.getID(), matrix)
        return

    def _setInAoI(self, entry, isInAoI):
        if entry.setInAoI(isInAoI):
            self._invoke(entry.getID(), 'setInAoI', isInAoI)

    def _showVehicle(self, vehicleID, location):
        matrix = matrix_factory.makeVehicleMPByLocation(vehicleID, location, self._arenaVisitor.getArenaPositions())
        entry = self._entries[vehicleID]
        if matrix is None:
            self.__setActive(entry, False)
            return
        else:
            if self.__isSPG or self._isInStrategicMode():
                isSpotted = entry.getLocation() == VEHICLE_LOCATION.UNDEFINED
            else:
                isSpotted = True
            self.__setLocationAndMatrix(entry, location, matrix)
            self._setInAoI(entry, True)
            self.__setActive(entry, True)
            self.__showVehicleHp(vehicleID, entry.getID())
            isUpgrading = False
            vehicle = BigWorld.entity(vehicleID)
            if vehicle is not None:
                isUpgrading = vehicle.isUpgrading or vehicle.isForceReloading
            animation = self.__getSpottedAnimation(entry, isSpotted)
            if animation and self.__replayRegistrator.validateShowVehicle(vehicleID) and not isUpgrading:
                self.__playSpottedSound(entry)
                self._invoke(entry.getID(), 'setAnimation', animation)
                self.__replayRegistrator.registerShowVehicle(vehicleID)
            return

    def _hideVehicle(self, entry):
        matrix = entry.getMatrix()
        if matrix is not None:
            matrix = matrix_factory.convertToLastSpottedVehicleMP(matrix)
            isDeactivate = not _FEATURES.isOn(self.__flags) or self._isInPostmortemMode() and not entry.isEnemy()
        else:
            LOG_WARNING('Matrix of vehicle entry is None, vehicle features is skipped', entry)
            isDeactivate = True
        self._setInAoI(entry, False)
        self.__setLocationAndMatrix(entry, VEHICLE_LOCATION.UNDEFINED, matrix)
        vehicleToHideID = None
        for vehicleID, savedEntry in self._entries.iteritems():
            if savedEntry.getID() == entry.getID():
                vehicleToHideID = vehicleID
                break

        self.__replayRegistrator.registerHideVehicle(vehicleToHideID)
        if isDeactivate or BattleReplay.g_replayCtrl.isVehicleChanging():
            self.__setActive(entry, False)
        return

    def __switchToVehicle(self, prevCtrlID):
        if prevCtrlID and prevCtrlID != self.__playerVehicleID and prevCtrlID in self._entries:
            entry = self._entries[prevCtrlID]
            if entry.isAlive() and entry.getLocation() != VEHICLE_LOCATION.UNDEFINED:
                self.__setActive(entry, True)
        if self._ctrlVehicleID and self._ctrlVehicleID != self.__playerVehicleID and self._ctrlVehicleID in self._entries and self._ctrlMode != _CTRL_MODE.VIDEO:
            self.__setActive(self._entries[self._ctrlVehicleID], False)

    def __showVehicleHp(self, vehicleId, entryId):
        self._invoke(entryId, 'showVehicleHp', self.__canShowVehicleHp)

    def __showFeatures(self, flag):
        self._parentObj.as_showVehiclesNameS(flag)
        for entry in self._entries.itervalues():
            if entry.wasSpotted() and entry.isAlive():
                self.__setActive(entry, flag)

    def __showMinimapHP(self, showHp):
        if showHp == self.__canShowVehicleHp:
            return
        self.__canShowVehicleHp = showHp
        for key, entry in self._entries.iteritems():
            if not entry.isActive():
                continue
            self.__showVehicleHp(key, entry.getID())

    def __getSpottedAnimation(self, entry, isSpotted):
        if not self.__isObserver and isSpotted:
            animation = entry.getSpottedAnimation(self._entries.itervalues())
        else:
            animation = ''
        return animation

    @staticmethod
    def __playSpottedSound(entry):
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications is not None:
            soundNotifications.play('enemy_sighted_for_team', position=Math.Matrix(entry.getMatrix()).translation)
        return

    def __clearDestroyCallback(self, vehicleID):
        callbackID = self.__destroyCallbacksIDs.pop(vehicleID, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def __setDestroyCallback(self, vehicleID):
        self.__clearDestroyCallback(vehicleID)
        self.__destroyCallbacksIDs[vehicleID] = BigWorld.callback(self.__destroyDuration, partial(self.__handleDestroyCallback, vehicleID))

    def __handleDestroyCallback(self, vehicleID):
        self.__destroyCallbacksIDs[vehicleID] = None
        if vehicleID in self._entries:
            self.__setActive(self._entries[vehicleID], False)
        return

    def __clearAoIToFarCallback(self, vehicleID):
        callbackID = self.__aoiToFarCallbacksIDs.pop(vehicleID, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def __setAoIToFarCallback(self, vehicleID):
        self.__clearAoIToFarCallback(vehicleID)
        self.__aoiToFarCallbacksIDs[vehicleID] = BigWorld.callback(minimap_utils.AOI_TO_FAR_TIME, partial(self.__handleAoIToFarCallback, vehicleID))

    def __handleAoIToFarCallback(self, vehicleID):
        self.__aoiToFarCallbacksIDs.pop(vehicleID, None)
        if vehicleID in self._entries:
            self._hideVehicle(self._entries[vehicleID])
            self._notifyVehicleRemoved(vehicleID)
        return

    def __onMinimapVehicleAdded(self, vProxy, vInfo, guiProps):
        vehicleID = vInfo.vehicleID
        if vehicleID == self.__playerVehicleID or vInfo.isObserver() or not vProxy.isAlive():
            return
        else:
            self.__clearAoIToFarCallback(vehicleID)
            if vehicleID not in self._entries:
                model = self.__addEntryToPool(vehicleID, VEHICLE_LOCATION.AOI)
                if model is not None:
                    self._setVehicleInfo(vehicleID, model, vInfo, guiProps, isSpotted=True)
                    self._setInAoI(model, True)
                    self._notifyVehicleAdded(vehicleID)
                    vehicle = BigWorld.entity(vehicleID)
                    self._onVehicleHealthChanged(vehicleID, vehicle.health, vehicle.maxHealth)
            else:
                self._showVehicle(vehicleID, VEHICLE_LOCATION.AOI)
                self._notifyVehicleAdded(vehicleID)
                vehicle = BigWorld.entity(vehicleID)
                self._onVehicleHealthChanged(vehicleID, vehicle.health, vehicle.maxHealth)
            return

    def __onMinimapVehicleRemoved(self, vehicleID):
        replayCtrl = BattleReplay.g_replayCtrl
        if vehicleID == self.__playerVehicleID or vehicleID not in self._entries or replayCtrl.isServerSideReplay and replayCtrl.isAllyToObservedVehicle(vehicleID):
            return
        entry = self._entries[vehicleID]
        if entry.getLocation() == VEHICLE_LOCATION.AOI:
            if replayCtrl.isServerSideReplay and replayCtrl.isVehicleChanging() or minimap_utils.isVehicleInAOI(entry.getMatrix(), self.__aoiEstimateRadius):
                self._hideVehicle(entry)
                self._notifyVehicleRemoved(vehicleID)
            else:
                matrix = matrix_factory.makeVehicleMPByLocation(vehicleID, VEHICLE_LOCATION.AOI_TO_FAR, {})
                self.__setLocationAndMatrix(entry, VEHICLE_LOCATION.AOI_TO_FAR, matrix)
                self.__setAoIToFarCallback(vehicleID)
        else:
            LOG_DEBUG('Location of vehicle entry is not in AoI', entry)

    def __onMinimapFeedbackReceived(self, eventID, entityID, value):
        if eventID == FEEDBACK_EVENT_ID.MINIMAP_SHOW_MARKER and entityID != self.__playerVehicleID:
            if entityID in self._entries:
                entry = self._entries[entityID]
                if (self.__isObserver or not avatar_getter.isVehicleAlive()) and avatar_getter.getVehicleIDAttached() == entityID:
                    return
                marker, _ = entry.isInAoI() and value
                self._invoke(entry.getID(), 'setAnimation', marker)

    def __onTeamChanged(self, teamID):
        self.invalidateArenaInfo()

    def __handleShowExtendedInfo(self, event):
        if self._parentObj.isModalViewShown():
            return
        isDown = event.ctx['isDown']
        if isDown:
            features = _FEATURES.addIfNot(self.__flags, _FEATURES.DO_REQUEST) if self.__flags != _FEATURES.OFF else self.__flags
            hpFeature = _FEATURES.addIfNot(self.__flagHpMinimap, _FEATURES.DO_REQUEST) if self.__flagHpMinimap != _FEATURES.OFF else self.__flagHpMinimap
        else:
            features = _FEATURES.removeIfHas(self.__flags, _FEATURES.DO_REQUEST)
            hpFeature = _FEATURES.removeIfHas(self.__flagHpMinimap, _FEATURES.DO_REQUEST)
        self.__flags = features
        self.__flagHpMinimap = hpFeature
        if _FEATURES.isChanged(self.__flags):
            self.__showFeatures(isDown)
        if _FEATURES.isChanged(self.__flagHpMinimap):
            self.__showMinimapHP(isDown)
        for entry in self._entries.itervalues():
            if not entry.isActive():
                continue
            self._invoke(entry.getID(), 'showExtendedInfo', isDown)


class EquipmentsPlugin(common.IntervalPlugin):
    __slots__ = ('__generator',)

    def __init__(self, parent):
        super(EquipmentsPlugin, self).__init__(parent)
        self.__generator = SequenceIDGenerator()

    def start(self):
        super(EquipmentsPlugin, self).start()
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentMarkerShown += self.__onEquipmentMarkerShown
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentMarkerShown -= self.__onEquipmentMarkerShown
        super(EquipmentsPlugin, self).stop()
        return

    def __onEquipmentMarkerShown(self, equipment, position, _, interval, team=None):
        uniqueID = self.__generator.next()
        arenaDP = self.sessionProvider.getArenaDP()
        isAllyTeam = team is None or arenaDP is None or arenaDP.isAllyTeam(team)
        marker = equipment.getMarker() if isAllyTeam else equipment.getEnemyMarker()
        if marker in settings.EQ_MARKER_TO_SYMBOL:
            symbol = settings.EQ_MARKER_TO_SYMBOL[marker]
        else:
            LOG_ERROR('Symbol is not found for equipment', equipment)
            return
        matrix = minimap_utils.makePositionMatrix(position)
        model = self._addEntryEx(uniqueID, symbol, _C_NAME.EQUIPMENTS, matrix=matrix, active=True)
        if model is not None:
            if team is not None:
                self._invoke(model.getID(), 'setOwningTeam', isAllyTeam)
            self._setCallback(uniqueID, interval)
        return


class AreaStaticMarkerPlugin(common.EntriesPlugin):

    def __init__(self, parentObj):
        super(AreaStaticMarkerPlugin, self).__init__(parentObj)
        self._entries = {}
        self._curScale = 1.0

    def start(self):
        super(AreaStaticMarkerPlugin, self).start()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded += self.__addStaticMarker
            ctrl.onStaticMarkerRemoved += self.__delStaticMarker
            ctrl.onReplyFeedbackReceived += self._onReplyFeedbackReceived
        minimapSize = settings.clampMinimapSizeIndex(AccountSettings.getSettings('minimapSize'))
        self._curScale = self.__calculateMarkerScale(minimapSize)
        self.__checkMarkers()
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded -= self.__addStaticMarker
            ctrl.onStaticMarkerRemoved -= self.__delStaticMarker
            ctrl.onReplyFeedbackReceived -= self._onReplyFeedbackReceived
        super(AreaStaticMarkerPlugin, self).stop()
        return

    def applyNewSize(self, sizeIndex):
        self._curScale = self.__calculateMarkerScale(sizeIndex)
        for entryID in self._entries:
            matrix = self._entries[entryID].getMatrix()
            matrix = minimap_utils.makePositionAndScaleMatrix(matrix.applyToOrigin(), (self._curScale, 1.0, self._curScale))
            self._setMatrix(self._entries[entryID].getID(), matrix)

    def __calculateMarkerScale(self, minimapSizeIndex):
        p = float(minimapSizeIndex - _MINIMAP_MIN_SCALE_INDEX) / float(_MINIMAP_MAX_SCALE_INDEX - _MINIMAP_MIN_SCALE_INDEX)
        return (1 - p) * _MINIMAP_LOCATION_MARKER_MIN_SCALE + p * _MINIMAP_LOCATION_MARKER_MAX_SCALE

    def __checkMarkers(self):
        _logger.debug('minimap __checkMarkers')
        for key in g_locationPointManager.markedAreas:
            _logger.debug('minimap marker created')
            locationPoint = g_locationPointManager.markedAreas[key]
            self.__addStaticMarker(locationPoint.targetID, locationPoint.creatorID, locationPoint.position, locationPoint.markerSubType, locationPoint.markerText, locationPoint.replyCount, False)

    def __addStaticMarker(self, areaID, creatorID, position, locationMarkerSubtype, markerText='', numberOfReplies=0, isTargetForPlayer=False):
        if locationMarkerSubtype not in _LOCATION_SUBTYPE_TO_FLASH_SYMBOL_NAME:
            return
        matrix = minimap_utils.makePositionAndScaleMatrix(position, (self._curScale, 1.0, self._curScale))
        self._addEntryEx(areaID, _LOCATION_SUBTYPE_TO_FLASH_SYMBOL_NAME[locationMarkerSubtype], _C_NAME.EQUIPMENTS, matrix=matrix, active=True, transformProps=settings.TRANSFORM_FLAG.FULL)
        if locationMarkerSubtype in _PING_FLASH_MINIMAP_SUBTYPES and numberOfReplies > 0 and isTargetForPlayer:
            self._invoke(self._entries[areaID].getID(), 'setState', 'reply')
        elif locationMarkerSubtype in _PING_FLASH_MINIMAP_SUBTYPES and numberOfReplies > 0:
            self._invoke(self._entries[areaID].getID(), 'setState', 'idle')
        elif locationMarkerSubtype in _PING_FLASH_MINIMAP_SUBTYPES:
            self._invoke(self._entries[areaID].getID(), 'setState', 'attack')

    def __delStaticMarker(self, objectID):
        self._delEntryEx(objectID)

    def _onReplyFeedbackReceived(self, ucmdID, replierID, markerType, oldReplyCount, newReplyCount):
        newReply = newReplyCount > oldReplyCount and replierID == avatar_getter.getPlayerVehicleID()
        if ucmdID in self._entries and newReply:
            self._invoke(self._entries[ucmdID].getID(), 'setState', 'reply')
            return True
        removedOwnReply = newReplyCount < oldReplyCount and replierID == avatar_getter.getPlayerVehicleID()
        if ucmdID in self._entries and (removedOwnReply or newReplyCount <= 0):
            self._invoke(self._entries[ucmdID].getID(), 'setState', 'idle')
            return True
        return False


class _EMinimapMouseKey(Enum):
    KEY_MBL = 0
    KEY_MBR = 1
    KEY_MBM = 2
    KEY_M_1 = 3
    KEY_M_2 = 4
    KEY_M_3 = 4


class SimpleMinimapPingPlugin(common.IntervalPlugin):
    __slots__ = ('_mouseKeyEventHandler', '__isHintPanelEnabled', '_boundingBox', '__minimapSettings', '__registeredToMouseEvents')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parentObj):
        super(SimpleMinimapPingPlugin, self).__init__(parentObj)
        self._mouseKeyEventHandler = {}
        self.__isHintPanelEnabled = False
        self._boundingBox = (Math.Vector2(0, 0), Math.Vector2(0, 0))
        self.__minimapSettings = None
        self.__registeredToMouseEvents = False
        return

    def start(self):
        super(SimpleMinimapPingPlugin, self).start()
        self._setupKeyBindingEvents(False)

    def stop(self):
        super(SimpleMinimapPingPlugin, self).stop()
        self._mouseKeyEventHandler.clear()

    def onMinimapClicked(self, x, y, buttonIdx, mapScaleIndex):
        if buttonIdx in self._mouseKeyEventHandler:
            self._mouseKeyEventHandler[buttonIdx](x, y, mapScaleIndex)

    def _getClickPosition(self, x, y):
        raise NotImplementedError('must be implemented')

    def _processCommandByPosition(self, commands, locationCommand, position, mapScaleIndex):
        raise NotImplementedError('must be implemented')

    def _setupKeyBindingEvents(self, isSPGAndStrategicView):
        self._mouseKeyEventHandler[_EMinimapMouseKey.KEY_MBL.value] = self._make3DAttentionToPing

    def _getTerrainHeightAt(self, spaceID, x, z):
        collisionWithTerrain = BigWorld.wg_collideSegment(spaceID, Math.Vector3(x, 1000.0, z), Math.Vector3(x, -1000.0, z), 128)
        return collisionWithTerrain.closestPoint if collisionWithTerrain is not None else (x, 0, z)

    def _make3DPing(self, x, y, locationCommand, mapScaleIndex):
        commands = self.sessionProvider.shared.chatCommands
        if commands is None:
            return
        else:
            position = Math.Vector3(self._getClickPosition(x, y))
            position = Math.Vector3(self._getTerrainHeightAt(BigWorld.player().spaceID, position.x, position.z))
            self._processCommandByPosition(commands, locationCommand, position, mapScaleIndex)
            return

    def _make3DAttentionToPing(self, x, y, mapScaleIndex):
        self._make3DPing(x, y, BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION, mapScaleIndex)


class MinimapPingPlugin(SimpleMinimapPingPlugin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parentObj):
        super(MinimapPingPlugin, self).__init__(parentObj)
        self._mouseKeyEventHandler = {}
        self.__isHintPanelEnabled = False
        self.__minimapSettings = None
        self.__registeredToMouseEvents = False
        return

    def start(self):
        super(MinimapPingPlugin, self).start()
        self.__minimapSettings = dict(AccountSettings.getSettings(MINIMAP_IBC_HINT_SECTION))
        if self.__haveHintsLeft(self.__minimapSettings) and not self.sessionProvider.arenaVisitor.gui.isBootcampBattle():
            self.__registeredToMouseEvents = True
            InputHandler.g_instance.onKeyDown += self.__handleKeyDownEvent
            InputHandler.g_instance.onKeyUp += self.__handleKeyUpEvent
        self._boundingBox = self._arenaVisitor.type.getBoundingBox()

    def stop(self):
        super(MinimapPingPlugin, self).stop()
        if self.__registeredToMouseEvents:
            InputHandler.g_instance.onKeyDown -= self.__handleKeyDownEvent
            InputHandler.g_instance.onKeyUp -= self.__handleKeyUpEvent
        self._boundingBox = (Math.Vector2(0, 0), Math.Vector2(0, 0))
        AccountSettings.setSettings(MINIMAP_IBC_HINT_SECTION, self.__minimapSettings)

    def __handleKeyDownEvent(self, event):
        if event.key not in (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL):
            return
        if not avatar_getter.isVehicleAlive() or self.__isHintPanelEnabled or self._parentObj.isModalViewShown():
            return
        if not self.__haveHintsLeft(self.__minimapSettings):
            return
        self.__minimapSettings[HINTS_LEFT] = max(0, self.__minimapSettings[HINTS_LEFT] - 1)
        self.__isHintPanelEnabled = True
        self.parentObj.as_enableHintPanelWithDataS(self._isInStrategicMode(), self.sessionProvider.getArenaDP().getVehicleInfo().isSPG())

    def __handleKeyUpEvent(self, event):
        if event.key not in (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL):
            return
        if not self.__isHintPanelEnabled:
            return
        self.__isHintPanelEnabled = False
        self.parentObj.as_disableHintPanelS()

    def updateControlMode(self, crtlMode, vehicleID):
        super(MinimapPingPlugin, self).updateControlMode(crtlMode, vehicleID)
        isSPGAndStrategicView = True if crtlMode in (aih_constants.CTRL_MODE_NAME.STRATEGIC, aih_constants.CTRL_MODE_NAME.ARTY, aih_constants.CTRL_MODE_NAME.MAP_CASE) else False
        if self.__isHintPanelEnabled:
            self.parentObj.as_updateHintPanelDataS(isSPGAndStrategicView, self.sessionProvider.getArenaDP().getVehicleInfo().isSPG())
        self._setupKeyBindingEvents(isSPGAndStrategicView and self.sessionProvider.getArenaDP().getVehicleInfo().isSPG())

    def onMinimapClicked(self, x, y, buttonIdx, mapScaleIndex):
        if buttonIdx in self._mouseKeyEventHandler:
            self._mouseKeyEventHandler[buttonIdx](x, y, mapScaleIndex)

    def _getClickPosition(self, x, y):
        raise NotImplementedError('must be implemented')

    def _processCommandByPosition(self, commands, locationCommand, position, mapScaleIndex):
        raise NotImplementedError('must be implemented')

    def _getIdByBaseNumber(self, team, number):
        raise NotImplementedError('must be implemented')

    def _make3DPingBases(self, commands, bases, baseName=''):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is None:
            return
        else:
            team, _, number = bases
            uniqueId = self._getIdByBaseNumber(team, number)
            replyState, commandKey = advChatCmp.getReplyStateForTargetIDAndMarkerType(uniqueId, MarkerType.BASE_MARKER_TYPE)
            if replyState is ReplyState.NO_REPLY:
                commandKey = BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE if team != avatar_getter.getPlayerTeam() else BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE
                commands.sendCommandToBase(uniqueId, commandKey, baseName)
                return
            self._processReplyCommand(replyState, commands, uniqueId, commandKey)
            return

    def _replyPing3DMarker(self, commands, uniqueId):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is None:
            return
        else:
            replyState, commandKey = advChatCmp.getReplyStateForTargetIDAndMarkerType(uniqueId, MarkerType.LOCATION_MARKER_TYPE)
            if commandKey is None:
                _logger.error('commandKey is None - this might be incorrect and should not happen!')
                return
            self._processReplyCommand(replyState, commands, uniqueId, commandKey)
            return

    def _specialMinimapCommand(self, x, y, mapScaleIndex):
        handler = avatar_getter.getInputHandler()
        if handler is None:
            return
        else:
            wasHandled = handler.onMinimapClicked(self._getClickPosition(x, y))
            if not wasHandled:
                self._make3DGoingToPing(x, y, mapScaleIndex)
            return

    def _setupKeyBindingEvents(self, isSPGAndStrategicView):
        self._mouseKeyEventHandler[_EMinimapMouseKey.KEY_MBR.value] = self._specialMinimapCommand
        if isSPGAndStrategicView:
            self._mouseKeyEventHandler[_EMinimapMouseKey.KEY_MBL.value] = self._make3DSPGAimArea
        else:
            self._mouseKeyEventHandler[_EMinimapMouseKey.KEY_MBL.value] = self._make3DAttentionToPing

    def _make3DGoingToPing(self, x, y, mapScaleIndex):
        self._make3DPing(x, y, BATTLE_CHAT_COMMAND_NAMES.GOING_THERE, mapScaleIndex)

    def _make3DSPGAimArea(self, x, y, mapScaleIndex):
        self._make3DPing(x, y, BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA, mapScaleIndex)

    def __haveHintsLeft(self, value):
        return value[HINTS_LEFT] > 0

    def _processReplyCommand(self, replyState, commands, uniqueId, commandKey):
        if replyState == ReplyState.CAN_CANCEL_REPLY:
            commands.sendCancelReplyChatCommand(uniqueId, commandKey)
            return
        if replyState == ReplyState.CAN_CONFIRM:
            commands.sendCommand(ONE_SHOT_COMMANDS_TO_REPLIES[commandKey])
            return
        commands.sendReplyChatCommand(uniqueId, commandKey)

    @staticmethod
    def _getNearestLocationIDForPosition(position, pRange):
        repliableAreas = g_locationPointManager.getRepliablePoints(avatar_getter.getPlayerVehicleID())
        if not repliableAreas:
            return None
        else:
            positionWithOffset = Math.Vector3(position.x, position.y, position.z - pRange * 0.5)

            def getDistance(entity):
                return Math.Vector3(entity.position).flatDistTo(positionWithOffset)

            closestMarker = min(repliableAreas, key=getDistance)
            return closestMarker.targetID if getDistance(closestMarker) < pRange else None


class _ReplayRegistrator(object):
    __lastAppearances = {}

    def registerShowVehicle(self, vehicleID):
        if self.__isActive():
            self.__lastAppearances[vehicleID] = self.__getCurrentTime()

    def registerHideVehicle(self, vehicleID):
        if self.__isActive() and not BattleReplay.g_replayCtrl.rewind:
            self.__lastAppearances.pop(vehicleID, None)
        return

    def validateShowVehicle(self, vehicleID):
        return not (self.__isActive() and vehicleID in self.__lastAppearances and self.__lastAppearances[vehicleID] + 1 < self.__getCurrentTime())

    def __isActive(self):
        return BattleReplay.g_replayCtrl.isPlaying

    def __getCurrentTime(self):
        return BattleReplay.g_replayCtrl.currentTime

    def __getVehicleIntervals(self, vehicleID):
        return self.__lastAppearances.setdefault(vehicleID, [])


RadarEntryParams = namedtuple('RadarEntryParams', 'symbol container')
RadarPluginParams = namedtuple('RadarPluginParams', 'fadeIn fadeOut lifetime vehicleEntryParams lootEntryParams')

class _RadarEntryData(object):

    def __init__(self, entryId, destroyMeCallback, params, typeId=None):
        super(_RadarEntryData, self).__init__()
        self.__entryId = entryId
        self.__lifeTime = params.lifetime
        self.__destroyMeCallback = destroyMeCallback
        self.__typeId = typeId
        self._callbackDelayer = CallbackDelayer()

    @property
    def entryId(self):
        return self.__entryId

    def getTypeId(self):
        return self.__typeId

    def destroy(self):
        self.stopTimer()
        self.__destroyMeCallback = None
        self._callbackDelayer = None
        return

    def upTimer(self):
        self.stopTimer()
        self._callbackDelayer.delayCallback(self.__lifeTime, partial(self.__destroyMeCallback, self.__entryId))

    def stopTimer(self):
        self._callbackDelayer.destroy()


class RadarPlugin(common.SimplePlugin, IRadarListener):

    def __init__(self, parent):
        super(RadarPlugin, self).__init__(parent)
        self._vehicleEntries = {}
        self._lootEntries = []
        self._params = RadarPluginParams(fadeIn=0.0, fadeOut=0.0, lifetime=0.0, vehicleEntryParams=RadarEntryParams(container='', symbol=''), lootEntryParams=RadarEntryParams(container='', symbol=''))

    def init(self, arenaVisitor, arenaDP):
        super(RadarPlugin, self).init(arenaVisitor, arenaDP)
        if self.sessionProvider.dynamic.radar:
            self.sessionProvider.dynamic.radar.addRuntimeView(self)

    def fini(self):
        if self.sessionProvider.dynamic.radar:
            self.sessionProvider.dynamic.radar.removeRuntimeView(self)
        for lootData in self._lootEntries:
            lootData.destroy()

        for _, vehicleData in self._vehicleEntries.iteritems():
            vehicleData.destroy()

        super(RadarPlugin, self).fini()

    def radarInfoReceived(self, data):
        for vehicleId, vehicleXZPos in data[1]:
            self._addVehicleEntry(vehicleId, vehicleXZPos)

        for typeId, lootXZPos in data[2]:
            self._addLootEntry(typeId, lootXZPos)

    def _createEntryData(self, entryId, destroyMeCallback, params, typeId=None):
        return _RadarEntryData(entryId, destroyMeCallback, params, typeId)

    def _addVehicleEntry(self, vehicleId, xzPosition):
        if self._arenaDP.getPlayerVehicleID() == vehicleId:
            return
        else:
            vEntry = self._vehicleEntries.get(vehicleId)
            if vEntry is not None:
                matrix = self.__getMatrixByXZ(xzPosition)
                self._parentObj.setMatrix(vEntry.entryId, matrix)
            else:
                entryId = self._addEntry(self._params.vehicleEntryParams.symbol, self._params.vehicleEntryParams.container, matrix=self.__getMatrixByXZ(xzPosition), active=True)
                vEntry = self._createEntryData(entryId, self.__destroyVehicleEntryByEntryID, self._params)
                self._vehicleEntries[vehicleId] = vEntry
            vEntry.upTimer()
            return vEntry.entryId

    def _addLootEntry(self, typeId, xzPosition):
        entryId = self._addEntry(self._params.lootEntryParams.symbol, self._params.lootEntryParams.container, matrix=self.__getMatrixByXZ(xzPosition), active=True)
        lEntry = self._createEntryData(entryId, self.__destroyLootEntry, self._params, typeId=typeId)
        lEntry.upTimer()
        self._lootEntries.append(lEntry)
        return lEntry.entryId

    def _destroyVehicleEntry(self, entryId, destroyedVehId):
        self._delEntry(entryId)
        if destroyedVehId is not None:
            entry = self._vehicleEntries.pop(destroyedVehId)
            entry.destroy()
        return

    def __clearLootEntries(self):
        while self._lootEntries:
            entry = self._lootEntries.pop()
            entry.stopTimer()
            self._delEntry(entry.entryId)

    def __destroyLootEntry(self, entryId):
        self._delEntry(entryId)
        destroyedObj = findFirst(lambda entry: entry.entryId == entryId, self._lootEntries)
        if destroyedObj is not None:
            self._lootEntries.remove(destroyedObj)
        return

    def __destroyVehicleEntryByEntryID(self, entryId):
        destroyedObjId = findFirst(lambda vId: self._vehicleEntries[vId].entryId == entryId, self._vehicleEntries)
        self._destroyVehicleEntry(entryId, destroyedObjId)

    @staticmethod
    def __getMatrixByXZ(xzPosition):
        matrix = Math.Matrix()
        matrix.translation = Math.Vector3(xzPosition[0], 0, xzPosition[1])
        return matrix


class AreaMarkerEntriesPlugin(common.BaseAreaMarkerEntriesPlugin):
    pass


class _BaseEnemySPGImpl(object):

    @staticmethod
    def getOptionName():
        raise NotImplementedError

    def getSymbolName(self):
        raise NotImplementedError

    def getIdAndPosition(self, position):
        raise NotImplementedError


class _EmptyEnemySPGImpl(_BaseEnemySPGImpl):

    @staticmethod
    def getOptionName():
        return MinimapArtyHitSetting.OPTIONS.HIDE

    def getSymbolName(self):
        return None

    def getIdAndPosition(self, position):
        return (None, None)


class _DotEnemySPGImpl(_BaseEnemySPGImpl):
    __slots__ = ('__generator',)

    def __init__(self):
        super(_DotEnemySPGImpl, self).__init__()
        self.__generator = SequenceIDGenerator()

    @staticmethod
    def getOptionName():
        return MinimapArtyHitSetting.OPTIONS.DOT

    def getSymbolName(self):
        return ENTRY_SYMBOL_NAME.ARTY_HIT_DOT_MARKER

    def getIdAndPosition(self, position):
        matrix = minimap_utils.makePositionMatrix(position)
        uniqueID = self.__generator.next()
        return (uniqueID, matrix)


class EnemySPGShotPlugin(common.IntervalPlugin):
    __slots__ = ('__hitImpl', '__currentTeam')
    _DISPLAY_TIME = 10
    _IMPL_LIST = (_EmptyEnemySPGImpl, _DotEnemySPGImpl)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parent):
        super(EnemySPGShotPlugin, self).__init__(parent)
        self.__hitImpl = _EmptyEnemySPGImpl()
        self.__currentTeam = None
        return

    def start(self):
        super(EnemySPGShotPlugin, self).start()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onEnemySPGShotReceived += self.__onEnemySPGShotReceived
        g_playerEvents.onTeamChanged += self.__onTeamChanged
        arenaDP = self.sessionProvider.getArenaDP()
        if arenaDP is not None:
            teams = arenaDP.getAllyTeams()
            self.__currentTeam = teams[0] if teams else None
        return

    def stop(self):
        g_playerEvents.onTeamChanged -= self.__onTeamChanged
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onEnemySPGShotReceived -= self.__onEnemySPGShotReceived
        self.__currentTeam = None
        super(EnemySPGShotPlugin, self).stop()
        return

    def setSettings(self):
        value = self.settingsCore.getSetting(settings_constants.GAME.SHOW_ARTY_HIT_ON_MAP)
        self.__setHitImpl(value)

    def updateSettings(self, diff):
        if settings_constants.GAME.SHOW_ARTY_HIT_ON_MAP in diff:
            value = diff[settings_constants.GAME.SHOW_ARTY_HIT_ON_MAP]
            self.__setHitImpl(value)

    def __setHitImpl(self, value):
        options = MinimapArtyHitSetting.ARTY_HIT_OPTIONS
        if value >= len(options):
            return
        option = options[value]
        if option == self.__hitImpl.getOptionName():
            return
        for implClazz in self._IMPL_LIST:
            if option == implClazz.getOptionName():
                self.__hitImpl = implClazz()
                self._clearAllCallbacks()
                break

    def __onEnemySPGShotReceived(self, position):
        symbolName = self.__hitImpl.getSymbolName()
        if symbolName is None:
            return
        else:
            uniqueID, matrix = self.__hitImpl.getIdAndPosition(position)
            if uniqueID is None:
                return
            model = self._addEntryEx(uniqueID, symbolName, _C_NAME.PERSONAL, matrix=matrix, active=True)
            if model is not None:
                self._invoke(model.getID(), 'show', self._DISPLAY_TIME)
                self._setCallback(uniqueID, self._DISPLAY_TIME)
            return

    def __onTeamChanged(self, teamID):
        if self.__currentTeam != teamID:
            self._clearAllCallbacks()
        self.__currentTeam = teamID
