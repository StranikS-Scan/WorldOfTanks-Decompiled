# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/players_panel.py
import BigWorld
from constants import ARENA_PERIOD
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.Scaleform.daapi.view.meta.EventPlayersPanelMeta import EventPlayersPanelMeta
from gui.Scaleform.settings import ICONS_SIZES
from gui.shared.badges import buildBadge
from PlayerEvents import g_playerEvents

class EventPlayersPanel(EventPlayersPanelMeta, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EventPlayersPanel, self).__init__()
        self._points = dict()
        self.__arenaDP = self.sessionProvider.getArenaDP()

    def invalidateVehiclesInfo(self, _):
        self.__updateAllTeammates()

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(self.sessionProvider.getArenaDP())

    def addVehicleInfo(self, vInfo, _):
        self.__updateTeammate(vInfo, vInfo.vehicleType.maxHealth)

    def updateVehiclesInfo(self, updated, arenaDP):
        for _, vInfo in updated:
            self.__updateTeammate(vInfo, vInfo.vehicleType.maxHealth)

    def _populate(self):
        super(EventPlayersPanel, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        self.__updateAllTeammates()
        return

    def _dispose(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        self.sessionProvider.removeArenaCtrl(self)
        super(EventPlayersPanel, self)._dispose()
        return

    def __onVehicleStateUpdated(self, state, value):
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        vInfo = self.__arenaDP.getVehicleInfo(playerVehicleID)
        if state == VEHICLE_VIEW_STATE.HEALTH:
            self.__updateTeammate(vInfo, value)
        elif state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__updateTeammate(vInfo, 0)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == _EVENT_ID.VEHICLE_HEALTH:
            vInfo = self.__arenaDP.getVehicleInfo(vehicleID)
            newHealth, _, _ = value
            self.__updateTeammate(vInfo, newHealth)
        elif eventID == _EVENT_ID.VEHICLE_DEAD:
            vInfo = self.__arenaDP.getVehicleInfo(vehicleID)
            self.__updateTeammate(vInfo, 0)

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__updateAllTeammates()

    def __updateAllTeammates(self):
        for vInfo in self.__arenaDP.getVehiclesInfoIterator():
            vehicle = BigWorld.entity(vInfo.vehicleID)
            if vehicle:
                self.__updateTeammate(vInfo, vehicle.health)

    def __updateTeammate(self, vInfo, hpCurrent):
        if self.__arenaDP.isEnemyTeam(vInfo.team):
            return
        else:
            playerVehicleID = avatar_getter.getPlayerVehicleID()
            playerSquad = self.__arenaDP.getVehicleInfo(playerVehicleID).squadIndex
            isSquad = False
            if playerSquad > 0 and playerSquad == vInfo.squadIndex or playerSquad == 0 and vInfo.vehicleID == playerVehicleID:
                isSquad = True
            badgeID = vInfo.selectedBadge
            badge = buildBadge(badgeID, vInfo.getBadgeExtraInfo())
            badgeVO = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': True}, shortIconName=True) if badge else None
            suffixBadgeId = vInfo.selectedSuffixBadge
            self.as_setPlayerPanelInfoS({'vehID': vInfo.vehicleID,
             'name': vInfo.player.name,
             'badgeVO': badgeVO,
             'suffixBadgeIcon': 'badge_{}'.format(suffixBadgeId) if suffixBadgeId else '',
             'suffixBadgeStripIcon': 'strip_{}'.format(suffixBadgeId) if suffixBadgeId else '',
             'nameVehicle': vInfo.vehicleType.shortName,
             'typeVehicle': vInfo.vehicleType.classTag,
             'hpMax': vInfo.vehicleType.maxHealth,
             'hpCurrent': hpCurrent,
             'countPoints': self.getPoints(vInfo.vehicleID),
             'isSquad': isSquad})
            self.as_setPlayerPanelHpS(vInfo.vehicleID, vInfo.vehicleType.maxHealth, min(hpCurrent, vInfo.vehicleType.maxHealth))
            if hpCurrent <= 0:
                self.as_setPlayerDeadS(vInfo.vehicleID)
            return

    def setPoints(self, vehID, points):
        self._points[vehID] = points
        self.as_setPlayerPanelCountPointsS(vehID, points)

    def getPoints(self, vehID):
        return self._points.get(vehID, 0)
