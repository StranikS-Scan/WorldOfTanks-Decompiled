# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/plugins.py
from functools import partial
from collections import defaultdict
import BattleReplay
import BigWorld
import constants
from Math import Matrix
from PlayerEvents import g_playerEvents
from account_helpers.settings_core.settings_constants import MARKERS, GRAPHICS, GAME
from battleground.StunAreaManager import STUN_AREA_STATIC_MARKER
from gui.Scaleform.daapi.view.battle.shared.markers2d import markers
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
from gui.battle_control.battle_constants import PLAYER_GUI_PROPS, MARKER_HIT_STATE
from gui.doc_loaders import GuiColorsLoader
from gui.shared import g_eventBus
from gui.shared.events import GameEvent
from gui.shared.utils.plugins import IPlugin
from helpers import dependency
from helpers import i18n
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IBootcampController
_TO_FLASH_SYMBOL_NAME_MAPPING = {STUN_AREA_STATIC_MARKER: settings.MARKER_SYMBOL_NAME.STATIC_ARTY_MARKER}
STUN_STATE = 0
INSPIRING_STATE = 1
INSPIRED_STATE = 2
ENGINEER_STATE = 3

class IMarkersManager(object):

    def createMarker(self, symbol, matrixProvider=None, active=True):
        raise NotImplementedError

    def invokeMarker(self, markerID, *signature):
        raise NotImplementedError

    def setMarkerMatrix(self, markerID, matrix):
        raise NotImplementedError

    def setMarkerActive(self, markerID, active):
        raise NotImplementedError

    def destroyMarker(self, markerID):
        raise NotImplementedError

    def _createCanvas(self, arenaVisitor):
        raise NotImplementedError

    def _setupPlugins(self, arenaVisitor):
        raise NotImplementedError


class MarkerPlugin(IPlugin):
    __slots__ = ()
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def _createMarkerWithPosition(self, symbol, position, active=True):
        matrixProvider = Matrix()
        matrixProvider.translation = position
        return self._parentObj.createMarker(symbol, matrixProvider, active)

    def _createMarkerWithMatrix(self, symbol, matrixProvider=None, active=True):
        return self._parentObj.createMarker(symbol, matrixProvider=matrixProvider, active=active)

    def _invokeMarker(self, markerID, function, *args):
        self._parentObj.invokeMarker(markerID, function, *args)

    def _setMarkerPosition(self, markerID, position):
        matrix = Matrix()
        matrix.setTranslate(position)
        self._parentObj.setMarkerMatrix(markerID, matrix)

    def _setMarkerMatrix(self, markerID, matrix):
        self._parentObj.setMarkerMatrix(markerID, matrix)

    def _setMarkerActive(self, markerID, active):
        self._parentObj.setMarkerActive(markerID, active)

    def _destroyMarker(self, markerID):
        self._parentObj.destroyMarker(markerID)


class SettingsPlugin(MarkerPlugin):

    def init(self, *args):
        super(SettingsPlugin, self).init(*args)
        self.__setMarkerSettings(notify=False)
        self.__setColorsSchemes()
        self._parentObj.setColorBlindFlag(self.settingsCore.getSetting(GRAPHICS.COLOR_BLIND))
        self._parentObj.setScale(self.settingsCore.interfaceScale.get())
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.settingsCore.interfaceScale.onScaleChanged += self.__onScaleChanged

    def fini(self):
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.settingsCore.interfaceScale.onScaleChanged -= self.__onScaleChanged
        super(SettingsPlugin, self).fini()

    def __setMarkerSettings(self, notify=False):
        getter = self.settingsCore.getSetting
        self._parentObj.setMarkerSettings(dict(((name, getter(name)) for name in MARKERS.ALL())), notify=notify)

    def __setColorsSchemes(self):
        colors = GuiColorsLoader.load()
        defaultSchemes = {}
        for name in colors.schemasNames():
            if not name.startswith(settings.MARKERS_COLOR_SCHEME_PREFIX):
                continue
            defaultSchemes[name] = colors.getSubSchemeToFlash(name, GuiColorsLoader.DEFAULT_SUB_SCHEME)

        colorBlindSchemes = {}
        for name in colors.schemasNames():
            if not name.startswith(settings.MARKERS_COLOR_SCHEME_PREFIX):
                continue
            colorBlindSchemes[name] = colors.getSubSchemeToFlash(name, GuiColorsLoader.COLOR_BLIND_SUB_SCHEME)

        self._parentObj.setColorsSchemes(defaultSchemes, colorBlindSchemes)

    def __onSettingsChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            self._parentObj.setColorBlindFlag(diff[GRAPHICS.COLOR_BLIND])
        if set(MARKERS.ALL()) & set(diff):
            self.__setMarkerSettings(notify=True)

    def __onScaleChanged(self, scale):
        self._parentObj.setScale(scale)


class EventBusPlugin(MarkerPlugin):

    def init(self, *args):
        super(EventBusPlugin, self).init(*args)
        add = g_eventBus.addListener
        add(GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=settings.SCOPE)
        add(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=settings.SCOPE)
        add(GameEvent.MARKERS_2D_VISIBILITY, self.__handleMarkerVisibility, scope=settings.SCOPE)

    def fini(self):
        remove = g_eventBus.removeListener
        remove(GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=settings.SCOPE)
        remove(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=settings.SCOPE)
        remove(GameEvent.MARKERS_2D_VISIBILITY, self.__handleMarkerVisibility, scope=settings.SCOPE)
        super(EventBusPlugin, self).fini()

    def __handleShowExtendedInfo(self, event):
        self._parentObj.setShowExInfoFlag(event.ctx['isDown'])

    def __handleGUIVisibility(self, event):
        self._parentObj.setVisible(event.ctx['visible'])

    def __handleMarkerVisibility(self, _):
        self._parentObj.setVisible(not self._parentObj.isVisible())


class AreaStaticMarkerPlugin(MarkerPlugin):
    __slots__ = ('__objects',)

    def __init__(self, parentObj):
        super(AreaStaticMarkerPlugin, self).__init__(parentObj)
        self.__objects = {}

    def init(self, *args):
        super(AreaStaticMarkerPlugin, self).init(*args)
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded += self.__addStaticMarker
            ctrl.onStaticMarkerRemoved += self.__delStaticMarker
        return

    def fini(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded -= self.__addStaticMarker
            ctrl.onStaticMarkerRemoved -= self.__delStaticMarker
        for key in self.__objects.iterkeys():
            self._destroyMarker(self.__objects[key])

        super(AreaStaticMarkerPlugin, self).fini()
        return

    def __addStaticMarker(self, areaID, position, markerSymbolName, show3DMarker=True):
        if not show3DMarker:
            return
        if areaID in self.__objects or markerSymbolName not in _TO_FLASH_SYMBOL_NAME_MAPPING:
            return
        markerID = self._createMarkerWithPosition(_TO_FLASH_SYMBOL_NAME_MAPPING[markerSymbolName], position, active=True)
        self.__objects[areaID] = markerID

    def __delStaticMarker(self, areaID):
        if areaID in self.__objects:
            markerID = self.__objects.pop(areaID, None)
            if markerID is not None:
                self._destroyMarker(markerID)
        return


class VehicleMarkerPlugin(MarkerPlugin, IArenaVehiclesController):
    bootcamp = dependency.descriptor(IBootcampController)
    __slots__ = ('_markers', '_markersStates', '_clazz', '__playerVehicleID', '_isSquadIndicatorEnabled', '__showDamageIcon')

    def __init__(self, parentObj, clazz=markers.VehicleMarker):
        super(VehicleMarkerPlugin, self).__init__(parentObj)
        self._markers = {}
        self._markersStates = defaultdict(list)
        self._clazz = clazz
        self._isSquadIndicatorEnabled = False
        self.__playerVehicleID = 0
        self.__showDamageIcon = False

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def init(self, *args):
        super(VehicleMarkerPlugin, self).init()
        settingsDamageIcon = self.settingsCore.getSetting(GAME.SHOW_DAMAGE_ICON)
        isInBootcamp = self.bootcamp.isInBootcamp()
        enableInBootcamp = isInBootcamp and self.bootcamp.isEnableDamageIcon()
        self.__showDamageIcon = settingsDamageIcon and (not isInBootcamp or enableInBootcamp)
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded += self.__onVehicleMarkerAdded
            ctrl.onVehicleMarkerRemoved += self.__onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        g_messengerEvents.voip.onPlayerSpeaking += self.__onPlayerSpeaking
        g_playerEvents.onTeamChanged += self.__onTeamChanged
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        return

    def fini(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded -= self.__onVehicleMarkerAdded
            ctrl.onVehicleMarkerRemoved -= self.__onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        g_messengerEvents.voip.onPlayerSpeaking -= self.__onPlayerSpeaking
        g_playerEvents.onTeamChanged -= self.__onTeamChanged
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(VehicleMarkerPlugin, self).fini()
        return

    def start(self):
        super(VehicleMarkerPlugin, self).start()
        self.__playerVehicleID = self.sessionProvider.getArenaDP().getPlayerVehicleID()
        self.sessionProvider.addArenaCtrl(self)

    def stop(self):
        while self._markers:
            _, marker = self._markers.popitem()
            marker.destroy()

        super(VehicleMarkerPlugin, self).stop()

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(self.sessionProvider.getArenaDP())

    def invalidateVehiclesInfo(self, arenaDP):
        getProps = arenaDP.getPlayerGuiProps
        getParts = self.sessionProvider.getCtx().getPlayerFullNameParts
        feedback = self.sessionProvider.shared.feedback
        for vInfo in arenaDP.getVehiclesInfoIterator():
            vehicleID = vInfo.vehicleID
            if vehicleID == self.__playerVehicleID or vInfo.isObserver():
                continue
            if vehicleID not in self._markers:
                marker = self.__addMarkerToPool(vehicleID, vProxy=feedback.getVehicleProxy(vehicleID))
            else:
                marker = self._markers[vehicleID]
            self.__setVehicleInfo(marker, vInfo, getProps(vehicleID, vInfo.team), getParts(vehicleID))
            self._setMarkerInitialState(marker, accountDBID=vInfo.player.accountDBID)

    def addVehicleInfo(self, vInfo, arenaDP):
        if vInfo.isObserver():
            return
        vehicleID = vInfo.vehicleID
        if vehicleID in self._markers:
            return
        ctx = self.sessionProvider.getCtx()
        feedback = self.sessionProvider.shared.feedback
        marker = self.__addMarkerToPool(vehicleID, vProxy=feedback.getVehicleProxy(vehicleID))
        self.__setVehicleInfo(marker, vInfo, ctx.getPlayerGuiProps(vehicleID, vInfo.team), ctx.getPlayerFullNameParts(vehicleID))
        self._setMarkerInitialState(marker, accountDBID=vInfo.player.accountDBID)

    def updateVehiclesInfo(self, updated, arenaDP):
        getProps = arenaDP.getPlayerGuiProps
        getParts = self.sessionProvider.getCtx().getPlayerFullNameParts
        for _, vInfo in updated:
            vehicleID = vInfo.vehicleID
            if vehicleID not in self._markers:
                continue
            marker = self._markers[vehicleID]
            self.__setVehicleInfo(marker, vInfo, getProps(vehicleID, vInfo.team), getParts(vehicleID))

    def invalidatePlayerStatus(self, flags, vInfo, arenaDP):
        self.__setEntityName(vInfo, arenaDP)

    def _setMarkerInitialState(self, marker, accountDBID=0):
        self.__setupDynamic(marker, accountDBID=accountDBID)
        if marker.isActive():
            self.__setupHealth(marker)

    def _hideVehicleMarker(self, vehicleID):
        if vehicleID in self._markers:
            marker = self._markers[vehicleID]
            if marker.setActive(False):
                markerID = marker.getMarkerID()
                self._setMarkerActive(markerID, False)
                self._setMarkerMatrix(markerID, None)
            marker.detach()
        return

    def _destroyVehicleMarker(self, vehicleID):
        if vehicleID in self._markers:
            marker = self._markers.pop(vehicleID)
            self._destroyMarker(marker.getMarkerID())
            marker.destroy()

    def __addMarkerToPool(self, vehicleID, vProxy=None):
        if vProxy is not None:
            matrixProvider = self._clazz.fetchMatrixProvider(vProxy)
            active = True
        else:
            matrixProvider = None
            active = False
        markerID = self._createMarkerWithMatrix(settings.MARKER_SYMBOL_NAME.VEHICLE_MARKER, matrixProvider=matrixProvider, active=active)
        marker = self._clazz(markerID, vehicleID, vProxy=vProxy, active=active)
        marker.onVehicleModelChanged += self.__onVehicleModelChanged
        self._markers[vehicleID] = marker
        if marker.isActive() and not marker.isAlive():
            self.__updateMarkerState(markerID, 'dead', True, '')
        return marker

    def __setVehicleInfo(self, marker, vInfo, guiProps, nameParts):
        markerID = marker.getMarkerID()
        vType = vInfo.vehicleType
        if self._isSquadIndicatorEnabled and vInfo.squadIndex:
            squadIndex = vInfo.squadIndex
        else:
            squadIndex = 0
        hunting = VehicleActions.isHunting(vInfo.events)
        self._invokeMarker(markerID, 'setVehicleInfo', vType.classTag, vType.iconPath, nameParts.vehicleName, vType.level, nameParts.playerFullName, nameParts.playerName, nameParts.clanAbbrev, nameParts.regionCode, vType.maxHealth, guiProps.name(), hunting, squadIndex, i18n.makeString(INGAME_GUI.STUN_SECONDS))
        self._invokeMarker(markerID, 'update')

    def __setupDynamic(self, marker, accountDBID=0):
        if accountDBID:
            speaking = self.bwProto.voipController.isPlayerSpeaking(accountDBID)
        else:
            speaking = False
        if marker.setSpeaking(speaking):
            self._invokeMarker(marker.getMarkerID(), 'setSpeaking', speaking)

    def __setupHealth(self, marker):
        self._invokeMarker(marker.getMarkerID(), 'setHealth', marker.getHealth())

    def __setEntityName(self, vInfo, arenaDP):
        vehicleID = vInfo.vehicleID
        if vehicleID not in self._markers:
            return
        handle = self._markers[vehicleID].getMarkerID()
        self._invokeMarker(handle, 'setEntityName', arenaDP.getPlayerGuiProps(vehicleID, vInfo.team).name())

    def __onVehicleMarkerAdded(self, vProxy, vInfo, guiProps):
        vehicleID = vInfo.vehicleID
        accountDBID = vInfo.player.accountDBID
        if vehicleID in self._markers:
            marker = self._markers[vInfo.vehicleID]
            if marker.setActive(True):
                marker.attach(vProxy)
                self._setMarkerMatrix(marker.getMarkerID(), marker.getMatrixProvider())
                self._setMarkerActive(marker.getMarkerID(), True)
                self._setMarkerInitialState(marker, accountDBID=accountDBID)
        else:
            if vInfo.isObserver():
                return
            marker = self.__addMarkerToPool(vehicleID, vProxy)
            self.__setVehicleInfo(marker, vInfo, guiProps, self.sessionProvider.getCtx().getPlayerFullNameParts(vehicleID))
            self._setMarkerInitialState(marker, accountDBID=accountDBID)

    def __onVehicleMarkerRemoved(self, vehicleID):
        self._hideVehicleMarker(vehicleID)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if vehicleID not in self._markers:
            return
        else:
            handle = self._markers[vehicleID].getMarkerID()
            hitStates = MARKER_HIT_STATE
            if eventID in hitStates and self.__showDamageIcon:
                newState = 'hit'
                iconAnimation = ''
                stateText = ''
                stateData = hitStates.get(eventID)
                if stateData is not None:
                    newState = stateData[0]
                    iconAnimation = stateData[1]
                    stateText = i18n.makeString(stateData[2])
                self.__updateMarkerState(handle, newState, value, stateText, iconAnimation)
            elif eventID == _EVENT_ID.VEHICLE_DEAD:
                self.__updateMarkerState(handle, 'dead', value)
            elif eventID == _EVENT_ID.VEHICLE_SHOW_MARKER:
                self.__showActionMarker(handle, value)
            elif eventID == _EVENT_ID.VEHICLE_HEALTH:
                self.__updateVehicleHealth(handle, *value)
            elif eventID == _EVENT_ID.VEHICLE_STUN:
                self.__updateStunMarker(vehicleID, handle, value)
            elif eventID == _EVENT_ID.VEHICLE_INSPIRE:
                self.__updateInspireMarker(vehicleID, handle, **value)
            elif eventID == _EVENT_ID.VEHICLE_PASSIVE_ENGINEERING:
                self.__updatePassiveEngineeringMarker(vehicleID, handle, *value)
            return

    def __onVehicleModelChanged(self, markerID, matrixProvider):
        self._setMarkerMatrix(markerID, matrixProvider)

    def __onSettingsChanged(self, diff):
        if GAME.SHOW_DAMAGE_ICON in diff:
            self.__showDamageIcon = diff[GAME.SHOW_DAMAGE_ICON]

    def __updateMarkerState(self, handle, newState, isImmediate, text='', iconAnimation=''):
        self._invokeMarker(handle, 'updateState', newState, isImmediate, text, iconAnimation)

    def __showActionMarker(self, handle, newState):
        self._invokeMarker(handle, 'showActionMarker', newState)

    def __updateStunMarker(self, vehicleID, handle, stunDuration, animated=True):
        self.__updateStatusMarkerState(vehicleID, stunDuration > 0, handle, STUN_STATE, stunDuration, animated, False)

    def __updatePassiveEngineeringMarker(self, vehicleID, handle, isAttacker, enabled, animated=True):
        self.__updateStatusMarkerState(vehicleID, enabled, handle, ENGINEER_STATE, enabled, animated, isAttacker)

    def __statusCompareFunction(self, x, y):
        return x > y

    def __updateStatusMarkerState(self, vehicleID, isShown, handle, statusID, duration, animated, isSourceVehicle):
        currentStates = self._markersStates[vehicleID]
        if isShown and statusID not in currentStates:
            currentStates.append(statusID)
            self._markersStates[vehicleID] = currentStates
        elif not isShown and statusID in currentStates:
            self._markersStates[vehicleID].remove(statusID)
        if self._markersStates[vehicleID]:
            currentStates.sort(reverse=True)
            self._markersStates[vehicleID] = currentStates
        currentlyActiveStatusID = self._markersStates[vehicleID][0] if self._markersStates[vehicleID] else -1
        if isShown:
            self._invokeMarker(handle, 'showStatusMarker', statusID, isSourceVehicle, duration, currentlyActiveStatusID, animated)
        else:
            self._invokeMarker(handle, 'hideStatusMarker', statusID, currentlyActiveStatusID, animated)

    def __updateInspireMarker(self, vehicleID, handle, isSourceVehicle, isInactivation, endTime, duration, animated=True):
        statusID = INSPIRING_STATE if isSourceVehicle else INSPIRED_STATE
        if isInactivation is not None:
            hideStatusID = INSPIRED_STATE if isSourceVehicle else INSPIRING_STATE
            self.__updateStatusMarkerState(vehicleID, False, handle, hideStatusID, duration, animated, isSourceVehicle)
            self.__updateStatusMarkerState(vehicleID, True, handle, statusID, duration, animated, isSourceVehicle)
        else:
            self.__updateStatusMarkerState(vehicleID, False, handle, statusID, duration, animated, isSourceVehicle)
        return

    def __updateVehicleHealth(self, handle, newHealth, aInfo, attackReasonID):
        if newHealth < 0 and not constants.SPECIAL_VEHICLE_HEALTH.IS_AMMO_BAY_DESTROYED(newHealth):
            newHealth = 0
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
            self._invokeMarker(handle, 'setHealth', newHealth)
        else:
            self._invokeMarker(handle, 'updateHealth', newHealth, self.__getVehicleDamageType(aInfo), constants.ATTACK_REASONS[attackReasonID])

    def __onPlayerSpeaking(self, accountDBID, flag):
        vehicleID = self.sessionProvider.getCtx().getVehIDByAccDBID(accountDBID)
        if vehicleID in self._markers:
            marker = self._markers[vehicleID]
            if marker.setSpeaking(flag):
                self._invokeMarker(marker.getMarkerID(), 'setSpeaking', flag)

    def __onTeamChanged(self, teamID):
        self.invalidateArenaInfo()

    def __getVehicleDamageType(self, attackerInfo):
        if not attackerInfo:
            return settings.DAMAGE_TYPE.FROM_UNKNOWN
        attackerID = attackerInfo.vehicleID
        if attackerID == self.__playerVehicleID:
            return settings.DAMAGE_TYPE.FROM_PLAYER
        entityName = self.sessionProvider.getCtx().getPlayerGuiProps(attackerID, attackerInfo.team)
        if entityName == PLAYER_GUI_PROPS.squadman:
            return settings.DAMAGE_TYPE.FROM_SQUAD
        if entityName == PLAYER_GUI_PROPS.ally:
            return settings.DAMAGE_TYPE.FROM_ALLY
        return settings.DAMAGE_TYPE.FROM_ENEMY if entityName == PLAYER_GUI_PROPS.enemy else settings.DAMAGE_TYPE.FROM_UNKNOWN


class RespawnableVehicleMarkerPlugin(VehicleMarkerPlugin):

    def start(self):
        super(RespawnableVehicleMarkerPlugin, self).start()
        self._isSquadIndicatorEnabled = False

    def _hideVehicleMarker(self, vehicleID):
        self._destroyVehicleMarker(vehicleID)


_EQUIPMENT_DEFAULT_INTERVAL = 1.0
_EQUIPMENT_DELAY_FORMAT = '{0:.0f}'

class EquipmentsMarkerPlugin(MarkerPlugin):
    __slots__ = ('__callbackIDs', '__finishTime', '__defaultPostfix')

    def __init__(self, parentObj):
        super(EquipmentsMarkerPlugin, self).__init__(parentObj)
        self.__callbackIDs = {}
        self.__finishTime = {}
        self.__defaultPostfix = i18n.makeString(INGAME_GUI.FORTCONSUMABLES_TIMER_POSTFIX)

    def init(self):
        super(EquipmentsMarkerPlugin, self).init()
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentMarkerShown += self.__onEquipmentMarkerShown
        return

    def fini(self):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentMarkerShown -= self.__onEquipmentMarkerShown
        super(EquipmentsMarkerPlugin, self).fini()
        return

    def stop(self):
        while self.__callbackIDs:
            _, callbackID = self.__callbackIDs.popitem()
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        super(EquipmentsMarkerPlugin, self).stop()
        return

    def __onEquipmentMarkerShown(self, item, position, _, delay):
        markerID = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.EQUIPMENT_MARKER, position + settings.MARKER_POSITION_ADJUSTMENT)
        self._invokeMarker(markerID, 'init', item.getMarker(), _EQUIPMENT_DELAY_FORMAT.format(round(delay)), self.__defaultPostfix)
        self.__setCallback(markerID, round(BigWorld.serverTime() + delay))

    def __setCallback(self, markerID, finishTime, interval=_EQUIPMENT_DEFAULT_INTERVAL):
        self.__callbackIDs[markerID] = BigWorld.callback(interval, partial(self.__handleCallback, markerID, finishTime))

    def __clearCallback(self, markerID):
        callbackID = self.__callbackIDs.pop(markerID, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def __handleCallback(self, markerID, finishTime):
        self.__callbackIDs[markerID] = None
        delay = round(finishTime - BigWorld.serverTime())
        if delay <= 0:
            self._destroyMarker(markerID)
        else:
            self._invokeMarker(markerID, 'updateTimer', _EQUIPMENT_DELAY_FORMAT.format(abs(delay)))
            self.__setCallback(markerID, finishTime)
        return
