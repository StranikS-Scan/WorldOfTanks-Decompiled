# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/minimap/minimap.py
from __future__ import absolute_import, division
import BattleReplay
import GUI
import Math
from chat_commands_consts import INVALID_TARGET_ID, MarkerType, ReplyState, BATTLE_CHAT_COMMAND_NAMES
from constants import IS_DEVELOPMENT
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicTeleportPlugin
from gui.battle_control import avatar_getter
from gui.Scaleform.daapi.view.battle.epic.minimap import CenteredPersonalEntriesPlugin, MINIMAP_SCALE_TYPES, makeMousePositionToEpicWorldPosition
from gui.Scaleform.daapi.view.battle.shared.minimap.common import BaseAreaMarkerEntriesPlugin, SimplePlugin
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared.minimap.entries import MinimapEntry
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import ArenaVehiclesPlugin, AreaStaticMarkerPlugin, MinimapPingPlugin, EquipmentsPlugin
from halloween.gui.hw_vehicle_role_helper import getVehicleRole
from halloween.gui.scaleform.daapi.view.battle.markers2d.vehicle_plugins import BOSS_MARKER_ROLE, BOSS_ROLE
from halloween.gui.scaleform.daapi.view.meta.HWMinimapMeta import HWMinimapMeta
from halloween.gui.shared.utils import findMarkerEntity
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID, FEEDBACK_EVENT_ID
from halloween_common.halloween_constants import HalloweenMarkerComponentNames
from shared_utils import findFirst, nextTick
from HWArenaPhasesComponent import HWArenaPhasesComponent
from HWArenaInfoBossHealthBarComponent import getArenaInfoBossHealthBarComponent
from StaticDeathZoneVisual import StaticDeathZoneVisual
from HWDeathZone import HWDeathZone
from vehicle_systems.stricted_loading import makeCallbackWeak
_C_NAME = settings.CONTAINER_NAME

class AreaMarkerEntry(MinimapEntry):

    def __init__(self, markerID, active, matrix, targetID=INVALID_TARGET_ID, bcMarkerType=MarkerType.INVALID_MARKER_TYPE):
        super(AreaMarkerEntry, self).__init__(markerID, active, matrix)
        self._targetID = targetID
        self._bcMarkerType = bcMarkerType
        self._isReplied = False
        self._hasAnimation = False

    def getTargetID(self):
        return self._targetID

    def getBCMarkerType(self):
        return self._bcMarkerType

    def getIsReplied(self):
        return self._isReplied

    def setIsReplied(self, value):
        self._isReplied = value

    def hasAnimation(self):
        return self._hasAnimation

    def setHasAnimation(self, value):
        self._hasAnimation = value


class HalloweenMinimapScaleMixin(SimplePlugin):
    REAL_SCALE_CONTAINERS = []

    def _addEntry(self, symbol, container, matrix=None, active=False, transformProps=settings.TRANSFORM_FLAG.DEFAULT):
        entryID = super(HalloweenMinimapScaleMixin, self)._addEntry(symbol, container, matrix, active, transformProps)
        self._parentObj.setEntryParameters(entryID, scaleType=MINIMAP_SCALE_TYPES.REAL_SCALE if container in self.REAL_SCALE_CONTAINERS else MINIMAP_SCALE_TYPES.NATIVE)
        return entryID


class HalloweenAreaMarkerEntriesPlugin(HalloweenMinimapScaleMixin, BaseAreaMarkerEntriesPlugin):

    def __init__(self, parent, clazz=AreaMarkerEntry):
        super(HalloweenAreaMarkerEntriesPlugin, self).__init__(parent)
        self._clazz = clazz
        self.__replayMarkersFeedbackStorage = {}

    def start(self):
        super(HalloweenAreaMarkerEntriesPlugin, self).start()
        self.__replayMarkersFeedbackStorage = {}
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onReplyFeedbackReceived += self.__onReplyFeedbackReceived
        return

    def stop(self):
        self.__replayMarkersFeedbackStorage = {}
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onReplyFeedbackReceived -= self.__onReplyFeedbackReceived
        super(HalloweenAreaMarkerEntriesPlugin, self).stop()
        return

    def createMarker(self, uniqueID, symbol, container, matrix, active, targetID=INVALID_TARGET_ID, bcMarkerType=MarkerType.INVALID_MARKER_TYPE):
        model = self._addEntryEx(uniqueID, symbol, container, matrix=matrix, active=active, targetID=targetID, bcMarkerType=bcMarkerType)
        if model is not None:
            self.__checkReplayFeedback(targetID, bcMarkerType)
            return True
        else:
            return False

    def setHasAnimation(self, componentID, value):
        entry = self._entries.get(componentID)
        if not entry:
            return
        entry.setHasAnimation(value)

    def _addEntryEx(self, uniqueID, symbol, container, matrix=None, active=False, targetID=INVALID_TARGET_ID, bcMarkerType=MarkerType.INVALID_MARKER_TYPE, transformProps=settings.TRANSFORM_FLAG.DEFAULT):
        if uniqueID in self._entries:
            return self._entries[uniqueID]
        else:
            entryID = self._addEntry(symbol, container, matrix=matrix, active=active, transformProps=transformProps)
            if entryID:
                model = self._clazz(entryID, active, matrix, targetID=targetID, bcMarkerType=bcMarkerType)
                self._entries[uniqueID] = model
            else:
                model = None
            return model

    def _getMarkerFromTargetID(self, targetID, markerType):
        return findFirst(lambda item: item.getTargetID() == targetID and item.getBCMarkerType() == markerType, self._entries.values())

    def __onReplyFeedbackReceived(self, targetID, replierID, markerType, oldReplyCount, newReplyCount):
        entry = self._getMarkerFromTargetID(targetID, markerType)
        if not entry:
            if BattleReplay.g_replayCtrl.isPlaying:
                self.__replayMarkersFeedbackStorage.setdefault((targetID, markerType), []).append((targetID,
                 replierID,
                 markerType,
                 oldReplyCount,
                 newReplyCount))
            return
        if entry.hasAnimation() and oldReplyCount == 0 and newReplyCount == 0:
            self._parentObj.invoke(entry.getID(), 'triggerClickAnimation')
        isReply = newReplyCount > 0
        if entry.getIsReplied() != isReply:
            self._parentObj.invoke(entry.getID(), 'setMarkerReplied', isReply)
            entry.setIsReplied(isReply)

    def __checkReplayFeedback(self, targetID, markerType):
        argsStorage = self.__replayMarkersFeedbackStorage.pop((targetID, markerType), [])
        for args in argsStorage:
            nextTick(makeCallbackWeak(self.__onReplyFeedbackReceived))(*args)

    def setEntryParameters(self, uniqueID, doClip=True, scaleType=MINIMAP_SCALE_TYPES.ADAPTED_SCALE):
        model = self._entries.get(uniqueID)
        if model:
            self._parentObj.setEntryParameters(model.getID(), doClip, scaleType)


class HalloweenMinimapVehiclesPlugin(HalloweenMinimapScaleMixin, ArenaVehiclesPlugin):

    def start(self):
        super(HalloweenMinimapVehiclesPlugin, self).start()
        HWArenaPhasesComponent.onHideVehicleOnMinimap += self._onHideVehicleOnMinimap
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onBossHealthChanged += self._onBossHealthChanged

    def stop(self):
        super(HalloweenMinimapVehiclesPlugin, self).stop()
        HWArenaPhasesComponent.onHideVehicleOnMinimap -= self._onHideVehicleOnMinimap
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onBossHealthChanged -= self._onBossHealthChanged

    @property
    def hwBattleGuiCtrl(self):
        return self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    def _getDisplayedVehicleClassTag(self, vInfo):
        vehicleType = vInfo.vehicleType
        role = getVehicleRole(vehicleType)
        if role is not None:
            if role != BOSS_ROLE:
                return role
            return BOSS_MARKER_ROLE
        else:
            return super(HalloweenMinimapVehiclesPlugin, self)._getDisplayedVehicleClassTag(vInfo)

    def _onHideVehicleOnMinimap(self, vehicleID):
        entry = self._entries.get(vehicleID)
        if entry:
            entry.setActive(False)
            entry.setInAoI(False)
            self._setActive(entry.getID(), False)

    def _onVehicleHealthChanged(self, vehicleID, currH, maxH):
        component = getArenaInfoBossHealthBarComponent()
        if not component or not component.isActive or vehicleID not in component.bossVehicleIDs:
            super(HalloweenMinimapVehiclesPlugin, self)._onVehicleHealthChanged(vehicleID, currH, maxH)
        else:
            self._updateBossHealth()

    def _onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        component = getArenaInfoBossHealthBarComponent()
        if not component or not component.isActive or vehicleID not in component.bossVehicleIDs:
            super(HalloweenMinimapVehiclesPlugin, self)._onVehicleFeedbackReceived(eventID, vehicleID, value)
        if eventID == FEEDBACK_EVENT_ID.HW_VEHICLE_MARKER_HEALTH and vehicleID in component.bossVehicleIDs:
            self._updateBossHealth()

    def _onBossHealthChanged(self, newHealth, prevHealth, bossVehicleID, attackerID, attackReasonID):
        self._updateBossHealth()

    def _updateBossHealth(self):
        component = getArenaInfoBossHealthBarComponent()
        bossCurH, bossMaxH = component.getBossCurrentLifeHealthValues()
        for bossID in component.bossVehicleIDs:
            super(HalloweenMinimapVehiclesPlugin, self)._onVehicleHealthChanged(bossID, bossCurH, bossMaxH)


class HalloweenAreaStaticMarkerPlugin(AreaStaticMarkerPlugin):

    def _addEntry(self, symbol, container, matrix=None, active=False, transformProps=settings.TRANSFORM_FLAG.DEFAULT):
        entryID = super(HalloweenAreaStaticMarkerPlugin, self)._addEntry(symbol, container, matrix, active, transformProps)
        self._parentObj.setEntryParameters(entryID, doClip=False, scaleType=MINIMAP_SCALE_TYPES.PROPORTIONAL)
        return entryID


class HalloweenEquipmentsPlugin(HalloweenMinimapScaleMixin, EquipmentsPlugin):
    _SYMBOL_DEATH_ZONE = 'HWDeathZoneEntryUI'
    _SYMBOL_DEATH_ZONE_IGNITE = 'HWDeathZoneIgniteEntryUI'
    _SYMBOL_DEATH_ZONE_STUN = 'HWDeathZoneStunEntryUI'
    _SYMBOL_DEATH_ZONE_INTERVAL = 'HWDeathZoneDamageOvertimeEntryUI'
    HW_EQ_MARKER_TO_SYMBOL = {'EventDeathZoneUI': _SYMBOL_DEATH_ZONE,
     'EventDeathZoneIgniteUI': _SYMBOL_DEATH_ZONE_IGNITE,
     'EventDeathZoneStunUI': _SYMBOL_DEATH_ZONE_STUN,
     'EventDeathZoneDamageOvertimeUI': _SYMBOL_DEATH_ZONE_INTERVAL}

    def _getSymbolFromMarker(self, marker):
        return self.HW_EQ_MARKER_TO_SYMBOL[marker] if marker in self.HW_EQ_MARKER_TO_SYMBOL else super(HalloweenEquipmentsPlugin, self)._getSymbolFromMarker(marker)


class HalloweenMinimapPingPlugin(HalloweenMinimapScaleMixin, MinimapPingPlugin):
    _CAMP_PING_RANGE = 63
    _COLLECTOR_PING_RANGE = 100
    _LOCATION_PING_RANGE = 30

    def _getClickPosition(self, x, y):
        return makeMousePositionToEpicWorldPosition(x, y, self._parentObj.getVisualBounds())

    def _getIdByBaseNumber(self, team, number):
        pass

    def _processCommandByPosition(self, commands, locationCommand, position, minimapScaleIndex):
        if avatar_getter.isVehicleAlive():
            entity = self._getNearestMarkerEntity(position)
            if entity is not None:
                self._make3DPingEntity(commands, entity)
                return
            locationID = self._getNearestLocationIDForPosition(position, self._LOCATION_PING_RANGE)
            if locationID is not None:
                self._replyPing3DMarker(commands, locationID)
                return
        commands.sendAttentionToPosition3D(position, locationCommand)
        return

    def _getEntityPingRange(self, entity):
        return self._COLLECTOR_PING_RANGE if HalloweenMarkerComponentNames.SOULS_COLLECTOR in entity.dynamicComponents else self._CAMP_PING_RANGE

    def _getNearestMarkerEntity(self, inPosition):
        entities = findMarkerEntity()
        if not entities:
            return None
        else:
            nearestEntity = entities[0]
            for entity in entities:
                if Math.Vector3(entity.position).flatDistTo(inPosition) < Math.Vector3(nearestEntity.position).flatDistTo(inPosition):
                    nearestEntity = entity

            return nearestEntity if Math.Vector3(nearestEntity.position).flatDistTo(inPosition) <= self._getEntityPingRange(nearestEntity) else None

    def _make3DPingEntity(self, commands, entity):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is None:
            return
        elif HalloweenMarkerComponentNames.SOULS_COLLECTOR not in entity.dynamicComponents and HalloweenMarkerComponentNames.CAMP not in entity.dynamicComponents:
            return
        else:
            targetID = entity.id
            replyState, commandKey = advChatCmp.getReplyStateForTargetIDAndMarkerType(targetID, MarkerType.TARGET_POINT_MARKER_TYPE)
            if replyState is ReplyState.NO_REPLY:
                commands.sendTargetedCommand(BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT, targetID)
                return
            self._processReplyCommand(replyState, commands, targetID, commandKey)
            return


class HWPersonalEntriesPlugin(HalloweenMinimapScaleMixin, CenteredPersonalEntriesPlugin):
    _SYMBOL = 'HWEmptyEntryUI'

    def __init__(self, parentObj):
        super(HWPersonalEntriesPlugin, self).__init__(parentObj)
        self.__minimapCenterEntry = None
        self.__centerCoordinate = Math.Vector3()
        self._autoZoom = True
        arenaPhasesComponent = HWArenaPhasesComponent.getInstance()
        if arenaPhasesComponent:
            self._autoZoom = arenaPhasesComponent.minimapAutoZoom
        return

    def start(self):
        super(HWPersonalEntriesPlugin, self).start()
        StaticDeathZoneVisual.onShowDeathZone += self._onShowDeathZone
        StaticDeathZoneVisual.onHideDeathZone += self._onHideDeathZone
        HWDeathZone.onResizeDeathZone += self._resize
        HWArenaPhasesComponent.onMinimapAutoZoomChanged += self._onMinimapAutoZoomChanged
        self._setMinimapCenter()

    def stop(self):
        super(HWPersonalEntriesPlugin, self).stop()
        StaticDeathZoneVisual.onShowDeathZone -= self._onShowDeathZone
        StaticDeathZoneVisual.onHideDeathZone -= self._onHideDeathZone
        HWDeathZone.onResizeDeathZone -= self._resize
        HWArenaPhasesComponent.onMinimapAutoZoomChanged -= self._onMinimapAutoZoomChanged

    def initControlMode(self, mode, available):
        super(HWPersonalEntriesPlugin, self).initControlMode(mode, available)
        self._setMinimapCenter()
        if self._getViewPointID() >= 0:
            self._parentObj.setEntryParameters(self._getViewPointID(), doClip=False, scaleType=MINIMAP_SCALE_TYPES.NATIVE)
        if self._getAnimationID() >= 0:
            self._parentObj.setEntryParameters(self._getAnimationID(), doClip=False, scaleType=MINIMAP_SCALE_TYPES.NATIVE)

    def updateControlMode(self, mode, vehicleID):
        super(HWPersonalEntriesPlugin, self).updateControlMode(mode, vehicleID)
        self._setMinimapCenter()

    def _setMinimapCenter(self):
        matrix = Math.Matrix()
        matrix.setTranslate(self.__centerCoordinate)
        if self.__minimapCenterEntry is None:
            self.__minimapCenterEntry = self._addEntry(self._SYMBOL, _C_NAME.ICONS, matrix=matrix, active=True)
        else:
            self._setMatrix(self.__minimapCenterEntry, matrix)
        self._parentObj.setMinimapCenterEntry(self.__minimapCenterEntry)
        return

    def _onShowDeathZone(self, dzVisual):
        if not dzVisual.entity.masks:
            return
        self.__centerCoordinate = dzVisual.entity.masks[0].polygonCenter
        self._setMinimapCenter()

    def _onHideDeathZone(self):
        self.__centerCoordinate = Math.Vector3()
        self._setMinimapCenter()

    def _resize(self, zone):
        if not self._autoZoom:
            return
        self.__centerCoordinate = zone.polygonCenter
        self._setMinimapCenter()

    def _onMinimapAutoZoomChanged(self, autoZoom):
        self._autoZoom = autoZoom


class HWTeleportPlugin(ClassicTeleportPlugin):

    def _getClickPosition(self, x, y):
        return makeMousePositionToEpicWorldPosition(x, y, self._parentObj.getVisualBounds())


class HalloweenMinimapComponent(HWMinimapMeta):
    _MINIMAP_1M_IN_PX = 0.21
    _DEFAULT_ARENA_SIZE = 1000.0
    _SZ_MARGIN = 1.1

    def __init__(self):
        super(HalloweenMinimapComponent, self).__init__()
        self._arenaScale = 1.0
        self._autoZoom = True
        arenaPhasesComponent = HWArenaPhasesComponent.getInstance()
        if arenaPhasesComponent:
            self._autoZoom = arenaPhasesComponent.minimapAutoZoom

    def getVisualBounds(self):
        return self.getComponent().getVisualBound()

    def _populate(self):
        super(HalloweenMinimapComponent, self)._populate()
        StaticDeathZoneVisual.onShowDeathZone += self._onShowDeathZone
        StaticDeathZoneVisual.onHideDeathZone += self._onHideDeathZone
        HWDeathZone.onResizeDeathZone += self._resize
        HWArenaPhasesComponent.onMinimapAutoZoomChanged += self._onMinimapAutoZoomChanged

    def _dispose(self):
        super(HalloweenMinimapComponent, self)._dispose()
        StaticDeathZoneVisual.onShowDeathZone -= self._onShowDeathZone
        StaticDeathZoneVisual.onHideDeathZone -= self._onHideDeathZone
        HWDeathZone.onResizeDeathZone -= self._resize
        HWArenaPhasesComponent.onMinimapAutoZoomChanged -= self._onMinimapAutoZoomChanged

    def changeMinimapZoom(self, mode):
        self.getComponent().changeMinimapZoom(mode)

    def setEntryParameters(self, entryId, doClip=True, scaleType=MINIMAP_SCALE_TYPES.ADAPTED_SCALE):
        self.getComponent().setEntryParameters(entryId, doClip, scaleType)

    def setMinimapCenterEntry(self, entryID):
        self.getComponent().setMinimapCenterEntry(entryID)

    def _createFlashComponent(self):
        return GUI.WGScrollingMinimapGUIComponentAS3(self.app.movie, settings.MINIMAP_COMPONENT_PATH)

    def _processMinimapSize(self, bottomLeft, upperRight):
        arenaSize = upperRight - bottomLeft
        self._arenaScale = max(arenaSize[0], arenaSize[1]) / self._DEFAULT_ARENA_SIZE
        self.changeMinimapZoom(self._arenaScale)
        arenaSizePx = arenaSize * self._MINIMAP_1M_IN_PX
        self.as_setMapDimensionsS(int(arenaSizePx[0]), int(arenaSizePx[1]))

    def _onShowDeathZone(self, dzVisual):
        if not dzVisual.entity.masks:
            return
        szScale = self._getSafeZoneScale(dzVisual)
        self.changeMinimapZoom(szScale)
        self.as_setZoomModeS(True)

    def _onHideDeathZone(self):
        self.changeMinimapZoom(self._arenaScale)
        self.as_setZoomModeS(False)

    def _onMinimapAutoZoomChanged(self, autoZoom):
        self._autoZoom = autoZoom

    def _resize(self, zone):
        if not self._autoZoom:
            return
        if zone.isActive and zone.visual:
            szScale = self._getSafeZoneScale(zone.visual)
            self.changeMinimapZoom(szScale)

    def _getSafeZoneScale(self, dzVisual):
        szSize = dzVisual.entity.masks[0].getDimensions()
        return max(szSize[0], szSize[2]) / self._DEFAULT_ARENA_SIZE * self._SZ_MARGIN

    def _setupPlugins(self, arenaVisitor):
        setup = super(HalloweenMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['area_markers'] = HalloweenAreaMarkerEntriesPlugin
        setup['personal'] = HWPersonalEntriesPlugin
        setup['vehicles'] = HalloweenMinimapVehiclesPlugin
        setup['area'] = HalloweenAreaStaticMarkerPlugin
        setup['equipments'] = HalloweenEquipmentsPlugin
        if IS_DEVELOPMENT:
            setup['teleport'] = HWTeleportPlugin
        if not BattleReplay.g_replayCtrl.isPlaying:
            setup['pinging'] = HalloweenMinimapPingPlugin
        return setup
