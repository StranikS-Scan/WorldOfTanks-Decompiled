# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/avatar_input_debug.py
import BigWorld
import constants
import pickle
import Input
import typing
import logging
from Input import TriggerEvent
from gui.battle_control import event_dispatcher as gui_event_dispatcher
if typing.TYPE_CHECKING:
    from Avatar import PlayerAvatar
_logger = logging.getLogger(__name__)

class AvatarInputDebug(object):

    def __init__(self):
        self._profile = 'DEBUG_PLAYER_INPUT_PROFILE'

    @property
    def _player(self):
        return BigWorld.player()

    def start(self):
        if not Input.inputSystem().hasProfile(self._profile):
            _logger.error('Input profile %s is not added.', self._profile)
            return
        self.__bindAction('ACTION_TOGGLE_GUI_VISIBILITY', self.__toggleGuiVisibility)
        self.__bindAction('ACTION_PLAYER_HEAL', self.__heal)
        self.__bindAction('ACTION_PLAYER_RELOAD_GUN', self.__reloadGun)
        self.__bindAction('ACTION_PLAYER_START_FIRE', self.__startFire)
        self.__bindAction('ACTION_PLAYER_EXPLODE', self.__explode)
        self.__bindAction('ACTION_PLAYER_BREAK_LEFT_TRACK', self.__breakLeftTrack)
        self.__bindAction('ACTION_PLAYER_BREAK_RIGHT_TRACK', self.__breakRightTrack)
        self.__bindAction('ACTION_PLAYER_DESTROY_SELF', self.__destroySelf)
        self.__bindAction('ACTION_PLAYER_KILL_ENGINE', self.__killEngine)
        self.__bindAction('ACTION_PLAYER_DAMAGE_DEVICE_AMMOBAYHEALTH', self.__damageDeviceAmmoBayHealth)
        self.__bindAction('ACTION_PLAYER_DAMAGE_DEVICE_FUELTANKHEALTH', self.__damageDeviceFuelTankHealth)
        self.__bindAction('ACTION_PLAYER_DAMAGE_DEVICE_ENGINEHEALTH', self.__damageDeviceEngineHealth)
        self.__bindAction('ACTION_PLAYER_DAMAGE_DEVICE_GUNHEALTH', self.__damageDeviceGunHealth)
        self.__bindAction('ACTION_TOGGLE_PIERCING_DEBUG_PANEL', self.__togglePiercingDebugPanel)
        self.__bindAction('ACTION_MAKE_SCREENSHOT', self.__makeScreenShot)
        self.__bindAction('ACTION_TOGGLE_CLIENT_FILTERS', self.__toggleClientFilters)
        self.__bindAction('ACTION_MOVE_VEHICLE', self.__moveVehicle)
        self.__bindAction('ACTION_PLAYER_PICKUP', self.__pickup)
        self.__bindAction('ACTION_PLAYER_HOT_RELOAD', self.__hotReload)
        self.__bindAction('ACTION_PLAYER_LOG_TKILL_RATINGS', self.__logTkillRatings)
        self.__bindAction('ACTION_TOGGLE_TELEPORT', self.__toggleTeleport)
        self.__bindAction('ACTION_PLAYER_RESPAWN_VEHICLE', self.__respawnVehicle)
        self.__bindAction('ACTION_PLAYER_PICKUP_ROLL', self.__pickupRoll)
        self.__bindAction('ACTION_PLAYER_CAPTURECLOSESTBASE', self.__captureClosestBase)
        self.__bindAction('ACTION_PLAYER_TELEPORTTOSHOTPOINT', self.__teleportToShotPoint)
        self.__bindAction('ACTION_PLAYER_SETSIGNAL', self.__setSignal)
        self.__bindAction('ACTION_PLAYER_NAVIGATETO', self.__navigateTo)
        self.__bindAction('ACTION_PLAYER_TOGGLEPAUSEAI', self.__togglePauseAI)
        self.__bindAction('ACTION_ADD_AREA_MARKER', self.__addAreaMarker)
        self.__bindAction('ACTION_REMOVE_ALL_MARKERS', self.__removeAllMarkers)
        self.__bindAction('ACTION_ADD_VEHICLE_MARKER', self.__addVehicleMarker)
        self.__bindAction('ACTION_PLAYER_KILLENEMYTEAM', self.__killEnemyTeam)
        self.__bindAction('ACTION_PLAYER_STUN', self.__stun)
        self.__bindAction('ACTION_PLAYER_KILL_TURRET', self.__killTurret)
        self.__bindAction('ACTION_PLAYER_KILL_TANKMAN', self.__killTankman)
        self.__bindAction('ACTION_PLAYER_SWITCH_SERVER_MARKER', self.__toggleShowServerMarker)
        Input.inputSystem().activateProfile(self._profile)

    def stop(self):
        if Input.inputSystem().hasProfile(self._profile):
            Input.inputSystem().deactivateProfile(self._profile, unbindAllReactions=True)

    def __bindAction(self, actionName, callback):
        action = Input.inputSystem().findAction(self._profile, actionName)
        if action:
            action.bindEventReaction(TriggerEvent.Triggered, callback)
            action.setPredicate(self.__predicate)

    def __predicate(self):
        return constants.HAS_DEV_RESOURCES and self._player.userSeesWorld()

    def __toggleGuiVisibility(self):
        gui_event_dispatcher.toggleGUIVisibility()

    def __heal(self):
        self._player.base.setDevelopmentFeature(0, 'heal', 0, '')

    def __reloadGun(self):
        self._player.base.setDevelopmentFeature(0, 'reload_gun', 0, '')

    def __startFire(self):
        self._player.base.setDevelopmentFeature(0, 'start_fire', 0, '')

    def __explode(self):
        self._player.base.setDevelopmentFeature(0, 'explode', 0, '')

    def __breakLeftTrack(self):
        self._player.base.setDevelopmentFeature(0, 'break_left_track', 0, '')

    def __breakRightTrack(self):
        self._player.base.setDevelopmentFeature(0, 'break_right_track', 0, '')

    def __destroySelf(self):
        self._player.base.setDevelopmentFeature(0, 'destroy_self', 0, '')

    def __killEngine(self):
        self._player.base.setDevelopmentFeature(0, 'kill_engine', 0, '')

    def __damageDeviceAmmoBayHealth(self):
        self._player.base.setDevelopmentFeature(0, 'damage_device', 500, 'ammoBayHealth')

    def __damageDeviceFuelTankHealth(self):
        self._player.base.setDevelopmentFeature(0, 'damage_device', 500, 'fuelTankHealth')

    def __damageDeviceEngineHealth(self):
        self._player.base.setDevelopmentFeature(0, 'damage_device', 500, 'engineHealth')

    def __damageDeviceGunHealth(self):
        self._player.base.setDevelopmentFeature(0, 'damage_device', 500, 'gunHealth')

    def __togglePiercingDebugPanel(self):
        gui_event_dispatcher.togglePiercingDebugPanel()

    def __makeScreenShot(self):

        def makeScreenShot(fileType, fileMask):
            BigWorld.screenShot(fileType, fileMask)

        makeScreenShot(fileType='jpg', fileMask='./../screenshots/')

    def __toggleClientFilters(self):
        vehicle = BigWorld.entity(self._player.playerVehicleID)
        vehicle.filter.enableClientFilters = not vehicle.filter.enableClientFilters

    def __moveVehicle(self):
        self._player.moveVehicle(1, True)

    def __pickup(self):
        self._player.base.setDevelopmentFeature(0, 'pickup', 0, 'straight')

    def __hotReload(self):
        if BigWorld.spaceReload(self._player.spaceID):
            self._player.base.setDevelopmentFeature(0, 'hot_reload', 0, '')

    def __logTkillRatings(self):
        self._player.base.setDevelopmentFeature(0, 'log_tkill_ratings', 0, '')

    def __toggleTeleport(self):
        self._player.isTeleport = not self._player.isTeleport

    def __respawnVehicle(self):
        self._player.base.setDevelopmentFeature(0, 'respawn_vehicle', 0, '')

    def __pickupRoll(self):
        self._player.base.setDevelopmentFeature(0, 'pickup', 0, 'roll')

    def __captureClosestBase(self):
        self._player.base.setDevelopmentFeature(0, 'captureClosestBase', 0, '')

    def __teleportToShotPoint(self):
        self._player.base.setDevelopmentFeature(0, 'teleportToShotPoint', 0, '')

    def __setSignal(self):
        self._player.base.setDevelopmentFeature(0, 'setSignal', 3, '')

    def __navigateTo(self):
        self._player.base.setDevelopmentFeature(0, 'navigateTo', 0, pickle.dumps((tuple(self._player.inputHandler.getDesiredShotPoint()),
         None,
         False,
         2.0), -1))
        return

    def __togglePauseAI(self):
        self._player.base.setDevelopmentFeature(0, 'togglePauseAI', 0, '')

    def __addAreaMarker(self):
        self._player.addOrRemoveMarkerTo(key=0)

    def __removeAllMarkers(self):
        self._player.addOrRemoveMarkerTo(key=1)

    def __addVehicleMarker(self):
        self._player.addOrRemoveMarkerTo(key=2)

    def __killEnemyTeam(self):
        self._player.base.setDevelopmentFeature(0, 'killEnemyTeam', 0, '')

    def __stun(self):
        self._player.base.setDevelopmentFeature(0, 'stun', 0, '')

    def __killTurret(self):
        self._player.base.setDevelopmentFeature(0, 'kill_turret', 0, '')

    def __killTankman(self):
        self._player.base.setDevelopmentFeature(0, 'kill_tankman', 0, 'loader')

    def __toggleShowServerMarker(self):
        self._player.gunRotator.showServerMarker = not self._player.gunRotator.showServerMarker
