# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/plugins.py
from functools import partial
import BattleReplay
import BigWorld
import constants
from Math import Matrix
from PlayerEvents import g_playerEvents
from account_helpers.settings_core.settings_constants import MARKERS, GRAPHICS
from battleground.StunAreaManager import STUN_AREA_STATIC_MARKER
from gui.Scaleform.daapi.view.battle.shared.markers2d import markers
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
from gui.battle_control.battle_constants import PLAYER_GUI_PROPS, MARKER_HIT_STATE, MARKER_HIT_STATE_BOOTCAMP
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

class IMarkersManager(object):
    """Plugins wait for specified manager's interface to manage markers."""

    def createMarker(self, symbol, matrixProvider=None, active=True):
        """Creates 2D marker.
        :param symbol: string containing name of symbol to create desired UI component in the Flash.
        :param matrixProvider: instance of Matrix or MatrixProvider.
        :param active: True if marker is active (visible), otherwise - False.
        :return: integer containing unique ID of marker.
        """
        raise NotImplementedError

    def invokeMarker(self, markerID, *signature):
        """Invokes desired method of marker in the Action Script.
        :param markerID: integer containing unique ID of marker.
        :param signature: tuple(<name of method in the Action Script>, *args)
        """
        raise NotImplementedError

    def setMarkerMatrix(self, markerID, matrix):
        """Sets new matrix to specified marker.
        :param markerID: integer containing unique ID of marker.
        :param matrix: instance of Matrix or MatrixProvider.
        """
        raise NotImplementedError

    def setMarkerActive(self, markerID, active):
        """Sets new activation flag to marker.
        :param markerID: integer containing unique ID of marker.
        :param active: True if marker is active (visible), otherwise - False.
        """
        raise NotImplementedError

    def destroyMarker(self, markerID):
        """Destroys 2D marker.
        :param markerID: integer containing unique ID of marker.
        """
        raise NotImplementedError

    def _createCanvas(self, arenaVisitor):
        """Creates cpp-side component to manage markers. It can be changed in some game modes.
        :param arenaVisitor: instance of _ClientArenaVisitor.
        :return: instance of object that extends FlashGUIComponent.
        """
        raise NotImplementedError

    def _setupPlugins(self, arenaVisitor):
        """Creates set of plugins to create.
        :param arenaVisitor: instance of _ClientArenaVisitor.
        :return: dict that contains classes of plugins.
        """
        raise NotImplementedError


class MarkerPlugin(IPlugin):
    """Base class of markers plugin."""
    __slots__ = ()
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def _createMarkerWithPosition(self, symbol, position, active=True):
        """Creates 2D marker that has static position on world.
        :param symbol: string containing name of symbol to create desired UI component in the Flash.
        :param position: Math.Vector3 containing world position.
        :param active: True if marker is visible, otherwise - False.
        :return: integer containing unique ID of marker.
        """
        matrixProvider = Matrix()
        matrixProvider.translation = position
        return self._parentObj.createMarker(symbol, matrixProvider, active)

    def _createMarkerWithMatrix(self, symbol, matrixProvider=None, active=True):
        """Creates 2D marker that has matrix provider to get world position each tick.
        :param symbol: string containing name of symbol to create desired UI component in the Flash.
        :param matrixProvider: instance of Matrix or MatrixProvider.
        :param active: True if marker is visible, otherwise - False.
        :return: integer containing unique ID of marker.
        """
        return self._parentObj.createMarker(symbol, matrixProvider=matrixProvider, active=active)

    def _invokeMarker(self, markerID, function, *args):
        """See comment in method IMarkersManager.invokeMarker."""
        self._parentObj.invokeMarker(markerID, function, *args)

    def _setMarkerPosition(self, markerID, position):
        """Sets position of marker.
        :param markerID: integer containing unique ID of marker.
        :param position: Math.Vector3 containing new position.
        :return:
        """
        matrix = Matrix()
        matrix.setTranslate(position)
        self._parentObj.setMarkerMatrix(markerID, matrix)

    def _setMarkerMatrix(self, markerID, matrix):
        """See comment in method IMarkersManager.setMarkerMatrix."""
        self._parentObj.setMarkerMatrix(markerID, matrix)

    def _setMarkerActive(self, markerID, active):
        """See comment in method IMarkersManager.setMarkerActive."""
        self._parentObj.setMarkerActive(markerID, active)

    def _destroyMarker(self, markerID):
        """See comment in method IMarkersManager.destroyMarker."""
        self._parentObj.destroyMarker(markerID)


class SettingsPlugin(MarkerPlugin):
    """Plugin listens changing of settings and transfers desired settings to Action Script."""

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
        self._parentObj.setMarkerSettings(dict(map(lambda name: (name, getter(name)), MARKERS.ALL())), notify=notify)

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
        """Listener for event ISettingsCore.onSettingsChanged.
        :param diff: dictionary containing changes in settings."""
        if GRAPHICS.COLOR_BLIND in diff:
            self._parentObj.setColorBlindFlag(diff[GRAPHICS.COLOR_BLIND])
        if set(MARKERS.ALL()) & set(diff):
            self.__setMarkerSettings(notify=True)

    def __onScaleChanged(self, scale):
        self._parentObj.setScale(scale)


class EventBusPlugin(MarkerPlugin):
    """Plugin listens events from event bus and invokes next actions:
        - toggle all markers visibility if player presses V (by default) to hide all GUI;
        - toggle all markers visibility only by key sequence CAPS + N (by default);
        - toggle extended mode if player presses ALT (by default).
    """

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
        """Special event toggles markers visibility only by key sequence CAPS + N (by default)
        and no any UI visible."""
        self._parentObj.setVisible(not self._parentObj.isVisible())


class AreaStaticMarkerPlugin(MarkerPlugin):
    """
    Plugin to create static area marker (marker over 3D scene terrain).
    """
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
        """
        Arguments:
        
            areaID: unique marker ID;
            position: Vertex Math.Vertex3 (coordinate on terrain);
            markerSymbolName: some string to map to flash object (MARKER_SYMBOL_NAME).
        
        """
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
    __slots__ = ('_markers', '_clazz', '__playerVehicleID', '_isSquadIndicatorEnabled')

    def __init__(self, parentObj, clazz=markers.VehicleMarker):
        super(VehicleMarkerPlugin, self).__init__(parentObj)
        self._markers = {}
        self._clazz = clazz
        self._isSquadIndicatorEnabled = False
        self.__playerVehicleID = 0

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def init(self, *args):
        super(VehicleMarkerPlugin, self).init()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded += self.__onVehicleMarkerAdded
            ctrl.onVehicleMarkerRemoved += self.__onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        g_messengerEvents.voip.onPlayerSpeaking += self.__onPlayerSpeaking
        g_playerEvents.onTeamChanged += self.__onTeamChanged
        return

    def fini(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded -= self.__onVehicleMarkerAdded
            ctrl.onVehicleMarkerRemoved -= self.__onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        g_messengerEvents.voip.onPlayerSpeaking -= self.__onPlayerSpeaking
        g_playerEvents.onTeamChanged -= self.__onTeamChanged
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
        """ Listener for event BattleFeedbackAdaptor.onVehicleMarkerAdded.
        :param vProxy: entity of vehicle.
        :param vInfo: instance of ArenaVehicleInfoVO.
        :param guiProps: instance of PLAYER_GUI_PROPS.
        """
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
        """ Listener for event BattleFeedbackAdaptor.onVehicleMarkerRemoved.
        :param vehicleID: long containing ID of vehicle.
        """
        self._hideVehicleMarker(vehicleID)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        """ Listener for event BattleFeedbackAdaptor.onVehicleFeedbackReceived.
        :param eventID: one of FEEDBACK_EVENT_ID.*.
        :param vehicleID: long containing ID of vehicle.
        :param value: new value for given event.
        """
        if vehicleID not in self._markers:
            return
        else:
            handle = self._markers[vehicleID].getMarkerID()
            hitStates = MARKER_HIT_STATE_BOOTCAMP if self.bootcamp.isInBootcamp() else MARKER_HIT_STATE
            if eventID in hitStates:
                newState = 'hit'
                stateText = ''
                stateData = hitStates.get(eventID)
                if stateData is not None:
                    newState = stateData[0]
                    stateText = i18n.makeString(stateData[1])
                self.__updateMarkerState(handle, newState, value, stateText)
            elif eventID == _EVENT_ID.VEHICLE_DEAD:
                self.__updateMarkerState(handle, 'dead', value, '')
            elif eventID == _EVENT_ID.VEHICLE_SHOW_MARKER:
                self.__showActionMarker(handle, value)
            elif eventID == _EVENT_ID.VEHICLE_HEALTH:
                self.__updateVehicleHealth(handle, *value)
            elif eventID == _EVENT_ID.VEHICLE_STUN:
                self.__updateStunMarker(handle, value)
            return

    def __onVehicleModelChanged(self, markerID, matrixProvider):
        self._setMarkerMatrix(markerID, matrixProvider)

    def __updateMarkerState(self, handle, newState, isImmediate, text):
        self._invokeMarker(handle, 'updateState', newState, isImmediate, text)

    def __showActionMarker(self, handle, newState):
        self._invokeMarker(handle, 'showActionMarker', newState)

    def __updateStunMarker(self, handle, stunDuration, animated=True):
        """
        Show/hide stun marker
        :param handle:
        :param stunDuration: stun time in sec
        :param animated: optional, showing with/without animation
        """
        if stunDuration > 0:
            self._invokeMarker(handle, 'showStunMarker', stunDuration, animated)
        else:
            self._invokeMarker(handle, 'hideStunMarker', animated)

    def __updateVehicleHealth(self, handle, newHealth, aInfo, attackReasonID):
        if newHealth < 0 and not constants.SPECIAL_VEHICLE_HEALTH.IS_AMMO_BAY_DESTROYED(newHealth):
            newHealth = 0
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
            self._invokeMarker(handle, 'setHealth', newHealth)
        else:
            self._invokeMarker(handle, 'updateHealth', newHealth, self.__getVehicleDamageType(aInfo), constants.ATTACK_REASONS[attackReasonID])

    def __onPlayerSpeaking(self, accountDBID, flag):
        """
        Listener for event g_messengerEvents.voip.onPlayerSpeaking.
        :param accountDBID: player db ID
        :param flag: isSpeaking (true or false)
        """
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
        self._isSquadIndicatorEnabled = self.sessionProvider.arenaVisitor.gui.isFalloutMultiTeam()

    def _hideVehicleMarker(self, vehicleID):
        self._destroyVehicleMarker(vehicleID)


_EQUIPMENT_DEFAULT_INTERVAL = 1.0
_EQUIPMENT_DELAY_FORMAT = '{0:.0f}'

class EquipmentsMarkerPlugin(MarkerPlugin):
    """Plugin to show 2D marker of equipment, updates time to activation of equipment
    and hides given marker when equipment is applied."""
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
            self._invokeMarker(markerID, 'updateTimer', _EQUIPMENT_DELAY_FORMAT.format(delay))
            self.__setCallback(markerID, finishTime)
        return
