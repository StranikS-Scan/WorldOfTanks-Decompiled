# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/players_panel.py
import BigWorld
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.meta.EventPlayersPanelMeta import EventPlayersPanelMeta
from gui.Scaleform.settings import ICONS_SIZES
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared.badges import buildBadge
from gui.shared.gui_items.Vehicle import VEHICLE_TABLE_TYPES_ORDER_INDICES as VEHICLE_ORDER
from game_event_getter import GameEventGetterMixin

class EventPlayersPanel(EventPlayersPanelMeta, IArenaVehiclesController, GameEventGetterMixin):

    def __init__(self):
        super(EventPlayersPanel, self).__init__()
        self.__arenaDP = self.sessionProvider.getArenaDP()

    def getControllerID(self):
        return BATTLE_CTRL_ID.GUI

    def getCtrlScope(self):
        return _SCOPE.VEHICLES

    def invalidateVehiclesInfo(self, _):
        self.__updateAllTeammates()

    def invalidateArenaInfo(self):
        self.__updateAllTeammates()

    def addVehicleInfo(self, vInfo, _):
        self.__updateAllTeammates()

    def updateVehiclesInfo(self, updated, arenaDP):
        self.__updateAllTeammates()

    def invalidateVehicleStatus(self, flags, vInfo, arenaDP):
        self.__updateAllTeammates()

    def _populate(self):
        super(EventPlayersPanel, self)._populate()
        if self.teammateVehicleHealth is not None:
            self.teammateVehicleHealth.onTeammateVehicleHealthUpdate += self.__onTeammateVehicleHealthUpdate
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        self.teammateLifecycle.onUpdated += self.__onRespawnLivesUpdated
        self.sessionProvider.addArenaCtrl(self)
        self.__updateAllTeammates()
        return

    def _dispose(self):
        if self.teammateVehicleHealth is not None:
            self.teammateVehicleHealth.onTeammateVehicleHealthUpdate -= self.__onTeammateVehicleHealthUpdate
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        self.teammateLifecycle.onUpdated -= self.__onRespawnLivesUpdated
        self.sessionProvider.removeArenaCtrl(self)
        super(EventPlayersPanel, self)._dispose()
        return

    def __onRespawnLivesUpdated(self):
        self.__updateAllTeammates()

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__updateAllTeammates()

    def __updateAllTeammates(self):
        vInfos = self.__arenaDP.getVehiclesInfoIterator()
        allyTeam = self.__arenaDP.getAllyTeams()[0]
        generalLevels = BigWorld.player().arena.extraData.get('playerAdditionalInfo', {})
        vInfos = sorted([ v for v in vInfos if v.player.accountDBID > 0 and v.team == allyTeam ], key=lambda x: (-generalLevels.get(x.player.accountDBID, -1), VEHICLE_ORDER[x.vehicleType.classTag], x.player.name))
        for vInfo in vInfos:
            self.__updateTeammate(vInfo)

    def __updateTeammate(self, vInfo):
        if self.teammateVehicleHealth is None:
            return
        else:
            hpCurrent = self.teammateVehicleHealth.getTeammateHealth(vInfo.vehicleID)
            playerVehicleID = avatar_getter.getPlayerVehicleID()
            playerSquad = self.__arenaDP.getVehicleInfo(playerVehicleID).squadIndex
            isSquad = False
            if playerSquad > 0 and playerSquad == vInfo.squadIndex or playerSquad == 0 and vInfo.vehicleID == playerVehicleID:
                isSquad = True
            teammateLifecycleData = self.teammateLifecycle.getParams()
            playerData = teammateLifecycleData.get(vInfo.vehicleID, {})
            badgeID = vInfo.selectedBadge
            suffixBadgeId = vInfo.selectedSuffixBadge
            badge = buildBadge(badgeID, vInfo.getBadgeExtraInfo())
            badgeVO = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': True}, shortIconName=True) if badge else None
            self.as_setPlayerPanelInfoS({'vehID': vInfo.vehicleID,
             'name': vInfo.player.name,
             'nameVehicle': vInfo.vehicleType.shortName,
             'typeVehicle': vInfo.vehicleType.classTag,
             'hpMax': vInfo.vehicleType.maxHealth,
             'hpCurrent': hpCurrent,
             'countLives': playerData.get('lives', 0),
             'isSquad': isSquad,
             'badgeVisualVO': badgeVO,
             'suffixBadgeIcon': 'badge_{}'.format(suffixBadgeId) if suffixBadgeId else '',
             'squadIndex': vInfo.squadIndex})
            return

    def __onTeammateVehicleHealthUpdate(self, diff):
        for vehID, newHealth in diff.iteritems():
            maxHealth = self.__arenaDP.getVehicleInfo(vehID).vehicleType.maxHealth
            self.as_setPlayerPanelHpS(vehID, maxHealth, min(newHealth, maxHealth))
            if newHealth <= 0:
                self.as_setPlayerDeadS(vehID)
