# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/plugins.py
from constants import WtTeams
from gui.Scaleform.daapi.view.battle.shared.markers2d import markers
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
from gui.shared.gui_items.Vehicle import VEHICLE_EVENT_TYPE
from helpers import i18n, dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_POWER_UP_SHOW_TIME = 4

class EventVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin):
    __slots__ = ('__arenaDP',)
    sessionProvider = dependency.instance(IBattleSessionProvider)

    def __init__(self, parentObj, clazz=markers.VehicleMarker):
        super(EventVehicleMarkerPlugin, self).__init__(parentObj, clazz)
        self.__arenaDP = self.sessionProvider.getArenaDP()

    def init(self):
        super(EventVehicleMarkerPlugin, self).init()
        feedbackCtrl = self.sessionProvider.shared.feedback
        arenaInfoCtrl = self.sessionProvider.dynamic.arenaInfo
        if feedbackCtrl is not None:
            feedbackCtrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        if arenaInfoCtrl is not None:
            arenaInfoCtrl.onPowerPointsChanged += self.__onPowerPointsChanged
        return

    def fini(self):
        feedbackCtrl = self.sessionProvider.shared.feedback
        arenaInfoCtrl = self.sessionProvider.dynamic.arenaInfo
        if feedbackCtrl is not None:
            feedbackCtrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        if arenaInfoCtrl is not None:
            arenaInfoCtrl.onPowerPointsChanged -= self.__onPowerPointsChanged
        super(EventVehicleMarkerPlugin, self).fini()
        return

    def invalidateVehicleStatus(self, flags, vInfo, arenaDP):
        if vInfo.team == WtTeams.BOSS and not vInfo.isAlive():
            self._hideVehicleMarker(vInfo.vehicleID)

    def _setVehicleInfo(self, marker, vInfo, guiProps, nameParts):
        markerID = marker.getMarkerID()
        vType = vInfo.vehicleType
        if self._isSquadIndicatorEnabled and vInfo.squadIndex:
            squadIndex = vInfo.squadIndex
        else:
            squadIndex = 0
        hunting = VehicleActions.isHunting(vInfo.events)
        classTag = vType.classTag
        isTiger = VEHICLE_EVENT_TYPE.EVENT_BOSS in vType.tags
        if isTiger:
            classTag = 'WT'
        if vInfo.team == WtTeams.BOSS and not vInfo.isAlive():
            self._hideVehicleMarker(vInfo.vehicleID)
        else:
            self._invokeMarker(markerID, 'setVehicleInfo', classTag, vType.iconPath, nameParts.vehicleName, vType.level, nameParts.playerFullName, nameParts.playerName, nameParts.clanAbbrev, nameParts.regionCode, vType.maxHealth, guiProps.name(), hunting, squadIndex, i18n.makeString(INGAME_GUI.STUN_SECONDS), True)
            self._invokeMarker(markerID, 'update')

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if vehicleID in self._markers:
            if eventID == _EVENT_ID.VEHICLE_SHOW_MESSAGE:
                handle = self._markers[vehicleID].getMarkerID()
                self.__showActionMassage(handle, *value)

    def __showActionMassage(self, handle, massage, isAlly):
        self._invokeMarker(handle, 'showActionMessage', massage, isAlly)

    def __onPowerPointsChanged(self, value):
        if not value:
            return
        arenaDP = self.sessionProvider.getArenaDP()
        for vehicleID, marker in self._markers.iteritems():
            vehInfo = arenaDP.getVehicleInfo(vehicleID)
            if vehInfo.team == WtTeams.HUNTERS:
                self._updatePowerUpMarker(vehicleID, marker.getMarkerID(), _POWER_UP_SHOW_TIME)
