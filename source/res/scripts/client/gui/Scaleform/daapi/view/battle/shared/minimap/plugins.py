# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/minimap/plugins.py
import math
from collections import defaultdict
from functools import partial
import BigWorld
import Math
import BattleReplay
import aih_constants
from AvatarInputHandler import AvatarInputHandler
from PlayerEvents import g_playerEvents
from account_helpers.settings_core import settings_constants
from battleground.StunAreaManager import STUN_AREA_STATIC_MARKER
from constants import VISIBILITY, AOI
from debug_utils import LOG_WARNING, LOG_ERROR, LOG_DEBUG
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.battle.shared.minimap import common
from gui.Scaleform.daapi.view.battle.shared.minimap import entries
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.battle_control import avatar_getter, minimap_utils, matrix_factory
from gui.battle_control.arena_info.interfaces import IVehiclesAndPositionsController
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, VEHICLE_LOCATION, VEHICLE_VIEW_STATE
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from ids_generators import SequenceIDGenerator
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_FEATURES = settings.ADDITIONAL_FEATURES
_CTRL_MODE = aih_constants.CTRL_MODE_NAME
_TO_FLASH_SYMBOL_NAME_MAPPING = {STUN_AREA_STATIC_MARKER: settings.ENTRY_SYMBOL_NAME.ARTY_MARKER}

class PersonalEntriesPlugin(common.SimplePlugin):
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
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self.__onPostMortemSwitched
            ctrl.onVehicleStateUpdated += self._onVehicleStateUpdated
            ctrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapFeedbackReceived += self.__onMinimapFeedbackReceived
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        handler = avatar_getter.getInputHandler()
        if isinstance(handler, AvatarInputHandler):
            handler.onPostmortemKillerVisionEnter += self.__onKillerVisionEnter
            handler.onPostmortemKillerVisionExit += self.__onKillerVisionExit
        super(PersonalEntriesPlugin, self).start()
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            ctrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
            ctrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapFeedbackReceived -= self.__onMinimapFeedbackReceived
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
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
                if getter(settings_constants.GAME.MINIMAP_DRAW_RANGE):
                    self.__addDrawRangeCircle()
                if getter(settings_constants.GAME.MINIMAP_MAX_VIEW_RANGE):
                    self.__addMaxViewRangeCircle()
                if getter(settings_constants.GAME.MINIMAP_VIEW_RANGE):
                    self.__addViewRangeCircle()
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
                value = diff[settings_constants.GAME.MINIMAP_DRAW_RANGE]
                if value:
                    self.__addDrawRangeCircle()
                else:
                    self.__removeDrawRangeCircle()
            if settings_constants.GAME.MINIMAP_MAX_VIEW_RANGE in diff:
                value = diff[settings_constants.GAME.MINIMAP_MAX_VIEW_RANGE]
                if value:
                    self.__addMaxViewRangeCircle()
                else:
                    self.__removeMaxViewRangeCircle()
            if settings_constants.GAME.MINIMAP_VIEW_RANGE in diff:
                value = diff[settings_constants.GAME.MINIMAP_VIEW_RANGE]
                if value:
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
            if self._isInStrategicMode():
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
        if self._isInArtyMode():
            activateID = self.__cameraIDs[_S_NAME.STRATEGIC_CAMERA]
            matrix = matrix_factory.makeArtyAimPointMatrix()
        elif self._isInStrategicMode():
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
                bottomLeft, upperRight = self._arenaVisitor.type.getBoundingBox()
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
        else:
            self.__updateViewPointEntry()
            self._setActive(self.__viewPointID, True)
            self._setActive(self.__animationID, True)
            getter = self.settingsCore.getSetting
            showDirectionLine = GUI_SETTINGS.showDirectionLine and getter(settings_constants.GAME.SHOW_VECTOR_ON_MAP)
            showYawLimit = GUI_SETTINGS.showSectorLines and getter(settings_constants.GAME.SHOW_SECTOR_ON_MAP)
            showCircles = getter(settings_constants.GAME.MINIMAP_DRAW_RANGE) or getter(settings_constants.GAME.MINIMAP_MAX_VIEW_RANGE) or getter(settings_constants.GAME.MINIMAP_VIEW_RANGE)
            if showDirectionLine:
                self.__showDirectionLine()
            else:
                self.__hideDirectionLine()
            self.__clearYawLimit()
            if showYawLimit:
                vInfo = self._arenaDP.getVehicleInfo(self._ctrlVehicleID)
                yawLimits = vInfo.vehicleType.turretYawLimits
                if yawLimits is not None and vInfo.isSPG():
                    self.__yawLimits = (math.degrees(yawLimits[0]), math.degrees(yawLimits[1]))
                    self.__setupYawLimit()
            self._showCircles(showCircles)
            return

    def _showCircles(self, showCircles):
        getter = self.settingsCore.getSetting
        if showCircles:
            self.__updateViewRangeCircle()
            if getter(settings_constants.GAME.MINIMAP_DRAW_RANGE):
                self.__addDrawRangeCircle()
            else:
                self.__removeDrawRangeCircle()
            if getter(settings_constants.GAME.MINIMAP_MAX_VIEW_RANGE):
                self.__addMaxViewRangeCircle()
            else:
                self.__removeMaxViewRangeCircle()
            if getter(settings_constants.GAME.MINIMAP_VIEW_RANGE):
                self.__addViewRangeCircle()
            else:
                self.__removeViewRangeCircle()
            self._setActive(self.__circlesID, True)
        elif self.__circlesID is not None:
            self._setActive(self.__circlesID, False)
        return

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
        vInfo = self._arenaDP.getVehicleInfo()
        self.__isAlive = vInfo.isAlive()
        self._invalidateMarkup(True)

    def __onMinimapFeedbackReceived(self, eventID, entityID, value):
        if eventID == FEEDBACK_EVENT_ID.MINIMAP_SHOW_MARKER and self.__animationID:
            if avatar_getter.getVehicleIDAttached() == entityID:
                self._invoke(self.__animationID, 'setAnimation', value)

    def __onVehicleFeedbackReceived(self, eventID, _, value):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_ATTRS_CHANGED and self.__circlesVisibilityState & settings.CIRCLE_TYPE.VIEW_RANGE:
            self._invoke(self.__circlesID, settings.VIEW_RANGE_CIRCLES_AS3_DESCR.AS_UPDATE_DYN_CIRCLE, min(value.get('circularVisionRadius', VISIBILITY.MIN_RADIUS), VISIBILITY.MAX_RADIUS))
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD and self.__isObserver:
            self.__removeAllCircles()
            self.__hideDirectionLine()

    def __addDrawRangeCircle(self):
        if self.__circlesVisibilityState & settings.CIRCLE_TYPE.DRAW_RANGE:
            return
        self.__circlesVisibilityState |= settings.CIRCLE_TYPE.DRAW_RANGE
        self._invoke(self.__circlesID, settings.VIEW_RANGE_CIRCLES_AS3_DESCR.AS_ADD_MAX_DRAW_CIRCLE, settings.CIRCLE_STYLE.COLOR.DRAW_RANGE, settings.CIRCLE_STYLE.ALPHA, AOI.VEHICLE_CIRCULAR_AOI_RADIUS)

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

    def __addViewRangeCircle(self):
        if self.__circlesVisibilityState & settings.CIRCLE_TYPE.VIEW_RANGE:
            return
        self.__circlesVisibilityState |= settings.CIRCLE_TYPE.VIEW_RANGE
        vehicleAttrs = self.sessionProvider.shared.feedback.getVehicleAttrs()
        self._invoke(self.__circlesID, settings.VIEW_RANGE_CIRCLES_AS3_DESCR.AS_ADD_DYN_CIRCLE, settings.CIRCLE_STYLE.COLOR.VIEW_RANGE, settings.CIRCLE_STYLE.ALPHA, min(vehicleAttrs.get('circularVisionRadius', VISIBILITY.MIN_RADIUS), VISIBILITY.MAX_RADIUS))

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
    __slots__ = ('__playerVehicleID', '__isObserver', '__aoiToFarCallbacksIDs', '__destroyCallbacksIDs', '__flags', '__showDestroyEntries', '__isDestroyImmediately', '__destroyDuration', '__isSPG', '__replayRegistrator')

    def __init__(self, parent):
        super(ArenaVehiclesPlugin, self).__init__(parent, clazz=entries.VehicleEntry)
        self.__playerVehicleID = 0
        self.__isObserver = False
        self.__isSPG = False
        self.__aoiToFarCallbacksIDs = {}
        self.__destroyCallbacksIDs = {}
        self.__flags = _FEATURES.OFF
        self.__showDestroyEntries = GUI_SETTINGS.showMinimapDeath
        self.__isDestroyImmediately = GUI_SETTINGS.permanentMinimapDeath
        self.__destroyDuration = GUI_SETTINGS.minimapDeathDuration / 1000.0
        self.__replayRegistrator = _ReplayRegistrator()
        if self.__showDestroyEntries and not self.__isDestroyImmediately and not self.__destroyDuration:
            self.__isDestroyImmediately = False
            LOG_WARNING('Gui setting permanentMinimapDeath is ignored because setting minimapDeathDuration is incorrect', self.__destroyDuration)

    def start(self):
        super(ArenaVehiclesPlugin, self).start()
        vInfo = self._arenaDP.getVehicleInfo()
        self.__playerVehicleID = self._arenaDP.getPlayerVehicleID()
        self.__isObserver = vInfo.isObserver()
        self.__isSPG = vInfo.isSPG()
        g_eventBus.addListener(events.GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=EVENT_BUS_SCOPE.BATTLE)
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapVehicleAdded += self.__onMinimapVehicleAdded
            ctrl.onMinimapVehicleRemoved += self.__onMinimapVehicleRemoved
            ctrl.onMinimapFeedbackReceived += self.__onMinimapFeedbackReceived
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
        self.__flags = settings.convertSettingToFeatures(value, self.__flags)
        if _FEATURES.isOn(self.__flags):
            self.__showFeatures(True)

    def updateSettings(self, diff):
        if settings_constants.GAME.SHOW_VEH_MODELS_ON_MAP in diff:
            value = diff[settings_constants.GAME.SHOW_VEH_MODELS_ON_MAP]
            self.__flags = settings.convertSettingToFeatures(value, self.__flags)
            if _FEATURES.isOn(self.__flags):
                self.__showFeatures(True)
            else:
                self.__showFeatures(False)

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
                self.__setVehicleInfo(vehicleID, model, vInfo, getProps(vehicleID, vInfo.team), isSpotted=False)
                if model.isActive():
                    self.__setInAoI(model, True)
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
                self.__setVehicleInfo(vehicleID, model, vInfo, arenaDP.getPlayerGuiProps(vehicleID, vInfo.team), isSpotted=False)
                if model.isActive():
                    self.__setInAoI(model, True)
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
                self.__setVehicleInfo(vehicleID, entry, vInfo, arenaDP.getPlayerGuiProps(vehicleID, vInfo.team))

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
            return Math.Vector3(-99999.9, -99999.9, -99999.9)
        entry = self._entries[vehicleID]
        return Math.Vector3(-99999.9, -99999.9, -99999.9) if not entry.isInAoI() else Math.Matrix(entry.getMatrix()).translation

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
                self.__setInAoI(entry, True)
                self.__setLocationAndMatrix(entry, VEHICLE_LOCATION.FAR, matrix_factory.makePositionMP(position))
                self.__setActive(entry, True)
                self._notifyVehicleAdded(vehicleID)

        for vehicleID in set(self._entries).difference(handled):
            entry = self._entries[vehicleID]
            if entry.getLocation() in (VEHICLE_LOCATION.FAR, VEHICLE_LOCATION.AOI_TO_FAR):
                self.__clearAoIToFarCallback(vehicleID)
                self.__hideVehicle(entry)
                self._notifyVehicleRemoved(vehicleID)

    def _notifyVehicleAdded(self, vehicleID):
        pass

    def _notifyVehicleRemoved(self, vehicleID):
        pass

    def _getPlayerVehicleID(self):
        return self.__playerVehicleID

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

    def __setVehicleInfo(self, vehicleID, entry, vInfo, guiProps, isSpotted=False):
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

    def __setInAoI(self, entry, isInAoI):
        if entry.setInAoI(isInAoI):
            self._invoke(entry.getID(), 'setInAoI', isInAoI)

    def __showVehicle(self, vehicleID, location):
        matrix = matrix_factory.makeVehicleMPByLocation(vehicleID, location, self._arenaVisitor.getArenaPositions())
        entry = self._entries[vehicleID]
        if matrix is None:
            self.__setActive(entry, False)
            return
        else:
            if self.__isSPG:
                isSpotted = entry.getLocation() == VEHICLE_LOCATION.UNDEFINED
            else:
                isSpotted = True
            self.__setLocationAndMatrix(entry, location, matrix)
            self.__setInAoI(entry, True)
            self.__setActive(entry, True)
            animation = self.__getSpottedAnimation(entry, isSpotted)
            if animation and self.__replayRegistrator.validateShowVehicle(vehicleID):
                self.__playSpottedSound(entry)
                self._invoke(entry.getID(), 'setAnimation', animation)
                self.__replayRegistrator.registerShowVehicle(vehicleID)
            return

    def __hideVehicle(self, entry):
        matrix = entry.getMatrix()
        if matrix is not None:
            matrix = matrix_factory.convertToLastSpottedVehicleMP(matrix)
            isDeactivate = not _FEATURES.isOn(self.__flags) or self._isInPostmortemMode() and not entry.isEnemy()
        else:
            LOG_WARNING('Matrix of vehicle entry is None, vehicle features is skipped', entry)
            isDeactivate = True
        self.__setInAoI(entry, False)
        self.__setLocationAndMatrix(entry, VEHICLE_LOCATION.UNDEFINED, matrix)
        vehicleToHideID = None
        for vehicleID, savedEntry in self._entries.iteritems():
            if savedEntry.getID() == entry.getID():
                vehicleToHideID = vehicleID
                break

        self.__replayRegistrator.registerHideVehicle(vehicleToHideID)
        if isDeactivate:
            self.__setActive(entry, False)
        return

    def __switchToVehicle(self, prevCtrlID):
        if prevCtrlID and prevCtrlID != self.__playerVehicleID and prevCtrlID in self._entries:
            entry = self._entries[prevCtrlID]
            if entry.isAlive() and entry.getLocation() != VEHICLE_LOCATION.UNDEFINED:
                self.__setActive(entry, True)
        if self._ctrlVehicleID and self._ctrlVehicleID != self.__playerVehicleID and self._ctrlVehicleID in self._entries:
            self.__setActive(self._entries[self._ctrlVehicleID], False)

    def __showFeatures(self, flag):
        self._parentObj.as_showVehiclesNameS(flag)
        for entry in self._entries.itervalues():
            if entry.wasSpotted() and entry.isAlive():
                self.__setActive(entry, flag)

    def __getSpottedAnimation(self, entry, isSpotted):
        if not self.__isObserver and isSpotted:
            animation = entry.getSpottedAnimation(self._entries.itervalues())
        else:
            animation = ''
        return animation

    @staticmethod
    def __playSpottedSound(entry):
        nots = avatar_getter.getSoundNotifications()
        if nots is not None:
            nots.play('enemy_sighted_for_team', None, None, Math.Matrix(entry.getMatrix()).translation)
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
            self.__hideVehicle(self._entries[vehicleID])
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
                    self.__setVehicleInfo(vehicleID, model, vInfo, guiProps, isSpotted=True)
                    self.__setInAoI(model, True)
                    self._notifyVehicleAdded(vehicleID)
            else:
                self.__showVehicle(vehicleID, VEHICLE_LOCATION.AOI)
                self._notifyVehicleAdded(vehicleID)
            return

    def __onMinimapVehicleRemoved(self, vehicleID):
        if vehicleID == self.__playerVehicleID or vehicleID not in self._entries:
            return
        entry = self._entries[vehicleID]
        if entry.getLocation() == VEHICLE_LOCATION.AOI:
            if not minimap_utils.isVehicleInAOI(entry.getMatrix()):
                matrix = matrix_factory.makeVehicleMPByLocation(vehicleID, VEHICLE_LOCATION.AOI_TO_FAR, {})
                self.__setLocationAndMatrix(entry, VEHICLE_LOCATION.AOI_TO_FAR, matrix)
                self.__setAoIToFarCallback(vehicleID)
            else:
                self.__hideVehicle(entry)
                self._notifyVehicleRemoved(vehicleID)
        else:
            LOG_DEBUG('Location of vehicle entry is not in AoI', entry)

    def __onMinimapFeedbackReceived(self, eventID, entityID, value):
        if eventID == FEEDBACK_EVENT_ID.MINIMAP_SHOW_MARKER and entityID != self.__playerVehicleID:
            if entityID in self._entries:
                entry = self._entries[entityID]
                if (self.__isObserver or not avatar_getter.isVehicleAlive()) and avatar_getter.getVehicleIDAttached() == entityID:
                    return
                entry.isInAoI() and self._invoke(entry.getID(), 'setAnimation', value)

    def __onTeamChanged(self, teamID):
        self.invalidateArenaInfo()

    def __handleShowExtendedInfo(self, event):
        if self._parentObj.isModalViewShown():
            return
        isDown = event.ctx['isDown']
        if isDown:
            features = _FEATURES.addIfNot(self.__flags, _FEATURES.DO_REQUEST)
        else:
            features = _FEATURES.removeIfHas(self.__flags, _FEATURES.DO_REQUEST)
        self.__flags = features
        if _FEATURES.isChanged(self.__flags):
            self.__showFeatures(isDown)


class TeleportPlugin(common.AttentionToCellPlugin):

    def _doAttention(self, index, duration):
        player = BigWorld.player()
        if player is not None and player.isTeleport:
            position = minimap_utils.getPositionByCellIndex(index, *self._boundingBox)
            result = BigWorld.collide(player.spaceID, (position[0], 1000.0, position[2]), (position[0], -1000.0, position[2]))
            player.base.vehicle_teleport((position[0], result[0][1], position[2]), 0)
        return

    def _doAttentionAtPosition(self, senderID, position, duration):
        pass

    def _doAttentionToObjective(self, senderID, hqIdx, duration):
        pass

    def _doAttentionToBase(self, senderID, baseIdx, baseName, duration):
        pass


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

    def __onEquipmentMarkerShown(self, equipment, position, _, interval):
        uniqueID = self.__generator.next()
        marker = equipment.getMarker()
        if marker in settings.EQ_MARKER_TO_SYMBOL:
            symbol = settings.EQ_MARKER_TO_SYMBOL[marker]
        else:
            LOG_ERROR('Symbol is not found for equipment', equipment)
            return
        matrix = minimap_utils.makePositionMatrix(position)
        model = self._addEntryEx(uniqueID, symbol, _C_NAME.EQUIPMENTS, matrix=matrix, active=True)
        if model is not None:
            self._setCallback(uniqueID, int(interval))
        return


class AreaStaticMarkerPlugin(common.EntriesPlugin):

    def start(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded += self.__addStaticMarker
            ctrl.onStaticMarkerRemoved += self.__delStaticMarker
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded -= self.__addStaticMarker
            ctrl.onStaticMarkerRemoved -= self.__delStaticMarker
        super(AreaStaticMarkerPlugin, self).fini()
        return

    def __addStaticMarker(self, objectID, position, markerSymbolName, show3DMarker):
        if markerSymbolName in _TO_FLASH_SYMBOL_NAME_MAPPING:
            self._addEntryEx(objectID, _TO_FLASH_SYMBOL_NAME_MAPPING[markerSymbolName], _C_NAME.EQUIPMENTS, matrix=minimap_utils.makePositionMatrix(position), active=True)

    def __delStaticMarker(self, objectID):
        self._delEntryEx(objectID)


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
