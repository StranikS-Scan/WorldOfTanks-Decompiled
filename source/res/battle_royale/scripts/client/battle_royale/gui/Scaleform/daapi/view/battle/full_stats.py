# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/full_stats.py
from helpers import dependency
from constants import ARENA_BONUS_TYPE
from gui.impl.gen.resources import R
from gui.impl import backport
from gui.Scaleform.daapi.view.meta.BattleRoyaleFullStatsMeta import BattleRoyaleFullStatsMeta
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES_REVERSED
from skeletons.gui.battle_session import IBattleSessionProvider
from battle_royale.gui.battle_control.controllers.vehicles_count_ctrl import IVehicleCountListener

class FullStatsComponent(BattleRoyaleFullStatsMeta, IVehicleCountListener):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FullStatsComponent, self).__init__()
        self.__vehicleTeams = {}
        self.__isSquadMode = False
        self.__teamsCount = 0

    @property
    def hasTabs(self):
        return False

    def onToggleVisibility(self, _):
        pass

    def setVehicles(self, count, vehicles, teams):
        vehiclesByType = []
        vehiclesSortedByType = sorted(vehicles.items(), key=lambda (classType, _): VEHICLE_TYPES_ORDER_INDICES_REVERSED[classType])
        self.__vehicleTeams = {}
        for classType, data in vehiclesSortedByType:
            sortedVehicles = sorted(data.items(), key=lambda (_, isDead): isDead)
            vehiclesByType.append({'classType': classType,
             'platoons': []})
            for vehInfo in sortedVehicles:
                vehicleID, (isDead, _, isEnemy, teamID, isRespawn) = vehInfo
                data = {'isEnemy': isEnemy,
                 'isDead': isDead and not isRespawn}
                if isEnemy or isDead and not isRespawn:
                    vehiclesByType[-1]['platoons'].append(data)
                else:
                    vehiclesByType[-1]['platoons'].insert(0, data)
                if not isDead or isRespawn:
                    self.__vehicleTeams[vehicleID] = teamID

        self.__teamsCount = len(set(self.__vehicleTeams.values()))
        self.as_updateVehiclesCounterS({'vehicles': vehiclesByType})
        self.__updateScore()

    def setFrags(self, frags, isPlayerVehicle):
        self.__updateScore(frags)

    def _populate(self):
        super(FullStatsComponent, self)._populate()
        self.__initPanel()

    def __initPanel(self):
        arenaDP = self.sessionProvider.getArenaDP()
        self.__initTeamsCount()
        bonusType = self.sessionProvider.arenaVisitor.getArenaBonusType()
        self.__isSquadMode = bonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD_RANGE
        squads = ''
        if self.__isSquadMode:
            squads = backport.text(R.strings.battle_royale.fragPanel.squadsCount(), squadsCount=str(self.__teamsCount))
        frags = arenaDP.getVehicleStats().frags
        playersCount = len(set(self.__vehicleTeams.keys()))
        data = {'header': {'title': backport.text(R.strings.battle_royale.fullStats.title()),
                    'subTitle': backport.text(R.strings.battle_royale.fullStats.subTitle()),
                    'battleType': arenaDP.getPersonalDescription().getFrameLabel(),
                    'description': backport.text(R.strings.battle_royale.fullStats.description())},
         'aliveBlock': self.__getScoreBlock('fullStatsAlive', playersCount, backport.text(R.strings.battle_royale.fullStats.alive()), squads),
         'destroyedBlock': self.__getScoreBlock('fullStatsDestroyed', frags, backport.text(R.strings.battle_royale.fullStats.destroyed())),
         'minimapItems': self.__getMinimapItems()}
        self.as_setDataS(data)

    def __getScoreBlock(self, icon, count, descr, squads=''):
        return {'icon': icon,
         'count': count,
         'description': descr,
         'squads': squads}

    def __getMinimapItems(self):
        fullStatsIcons = R.strings.battle_royale.fullStats.icons
        return [self.__getMinimapItem('tab_corpse_loot', backport.text(fullStatsIcons.corpseLoot.description()), 'add'),
         self.__getMinimapItem('tab_loot', backport.text(fullStatsIcons.defaultLoot.description()), 'add'),
         self.__getMinimapItem('tab_improved_loot', backport.text(fullStatsIcons.extendedLoot.description()), 'add'),
         self.__getMinimapItem('airdrop_loot', backport.text(fullStatsIcons.airDrop.description()), 'add'),
         self.__getMinimapItem('deathzone_info_warning', backport.text(R.strings.battle_royale.fullStats.deathZone.warning.description())),
         self.__getMinimapItem('deathzone_info_closed', backport.text(R.strings.battle_royale.fullStats.deathZone.closed.description()))]

    def __getMinimapItem(self, icon, description, blendMode='normal'):
        return {'icon': icon,
         'description': description,
         'blendMode': blendMode}

    def __updateScore(self, frags=None):
        arenaDP = self.sessionProvider.getArenaDP()
        playersCount = len(set(self.__vehicleTeams.keys()))
        if frags is None:
            vehicleID = arenaDP.getAttachedVehicleID()
            frags = arenaDP.getVehicleStats(vehicleID).frags
        squads = ''
        if self.__isSquadMode:
            squads = backport.text(R.strings.battle_royale.fragPanel.squadsCount(), squadsCount=str(self.__teamsCount))
        self.as_updateScoreS(playersCount, frags, squads)
        return

    def __initTeamsCount(self):
        arenaDP = self.sessionProvider.getArenaDP()
        for vInfoVO, _ in arenaDP.getVehiclesItemsGenerator():
            isAlive = vInfoVO.isAlive()
            isObserver = vInfoVO.isObserver()
            if not isObserver and isAlive:
                self.__vehicleTeams[vInfoVO.vehicleID] = vInfoVO.team

        self.__teamsCount = len(set(self.__vehicleTeams.values()))
