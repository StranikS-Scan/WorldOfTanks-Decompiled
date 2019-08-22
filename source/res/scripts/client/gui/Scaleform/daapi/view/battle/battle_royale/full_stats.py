# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/full_stats.py
from helpers import dependency
from gui.impl.gen.resources import R
from gui.impl import backport
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.Scaleform.daapi.view.meta.BattleRoyaleFullStatsMeta import BattleRoyaleFullStatsMeta
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.classic.full_stats import IFullStatsComponent

class FullStatsComponent(BattleRoyaleFullStatsMeta, IArenaVehiclesController, IFullStatsComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FullStatsComponent, self).__init__()
        self.__vehicleTeams = {}
        self.__isSquadMode = False
        self.__teamsCount = 0

    @property
    def hasTabs(self):
        return False

    def setActiveTabIndex(self, index):
        pass

    def showQuestProgressAnimation(self):
        pass

    def invalidateVehicleStatus(self, flags, vInfoVO, arenaDP):
        if not vInfoVO.isAlive() and vInfoVO.vehicleID in self.__vehicleTeams:
            del self.__vehicleTeams[vInfoVO.vehicleID]
            self.__teamsCount = len(set(self.__vehicleTeams.values()))
            self.__updateScore()

    def updateVehiclesStats(self, updated, arenaDP):
        for _, vStatsVO in updated:
            vStatsVO.vehicleID == arenaDP.getPlayerVehicleID() and self.__updateScore()
            continue

    def addVehicleInfo(self, vInfoVO, arenaDP):
        if not vInfoVO.isObserver() and vInfoVO.isAlive():
            self.__vehicleTeams[vInfoVO.vehicleID] = vInfoVO.team
        self.__updateScore()

    def _populate(self):
        super(FullStatsComponent, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        self.__initPanel()

    def _dispose(self):
        self.sessionProvider.removeArenaCtrl(self)
        super(FullStatsComponent, self)._dispose()

    def __initPanel(self):
        arenaDP = self.sessionProvider.getArenaDP()
        self.__initTeamsCount()
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
         'minimapItems': self.__getMinimapItems(),
         'deathZones': self.__getDeathZones()}
        self.as_setDataS(data)

    def __getScoreBlock(self, icon, count, descr, squads=''):
        return {'icon': icon,
         'count': count,
         'description': descr,
         'squads': squads}

    def __getMinimapItems(self):
        fullStatsIcons = R.strings.battle_royale.fullStats.icons
        return [self.__getMinimapItem('tab_loot', backport.text(fullStatsIcons.defaultLoot())), self.__getMinimapItem('tab_improved_loot', backport.text(fullStatsIcons.extendedLoot())), self.__getMinimapItem('airdrop', backport.text(fullStatsIcons.airDrop()), False)]

    def __getMinimapItem(self, icon, title, useAdd=True):
        return {'icon': icon,
         'title': title,
         'useAdd': useAdd}

    def __getDeathZones(self):
        return [self.__getDeathZoneType('deathzone_warning', backport.text(R.strings.battle_royale.fullStats.deathZone.warning.title()), backport.text(R.strings.battle_royale.fullStats.deathZone.warning.description())), self.__getDeathZoneType('deathzone_closed', backport.text(R.strings.battle_royale.fullStats.deathZone.closed.title()), backport.text(R.strings.battle_royale.fullStats.deathZone.closed.description()))]

    def __getDeathZoneType(self, icon, title, description):
        return {'icon': icon,
         'title': title,
         'description': description}

    def __updateScore(self):
        arenaDP = self.sessionProvider.getArenaDP()
        playersCount = len(set(self.__vehicleTeams.keys()))
        frags = arenaDP.getVehicleStats().frags
        squads = ''
        if self.__isSquadMode:
            squads = backport.text(R.strings.battle_royale.fragPanel.squadsCount(), squadsCount=str(self.__teamsCount))
        self.as_updateScoreS(playersCount, frags, squads)

    def __initTeamsCount(self):
        arenaDP = self.sessionProvider.getArenaDP()
        for vInfoVO, _ in arenaDP.getVehiclesItemsGenerator():
            isAlive = vInfoVO.isAlive()
            isObserver = vInfoVO.isObserver()
            if not isObserver and isAlive:
                self.__vehicleTeams[vInfoVO.vehicleID] = vInfoVO.team
            if arenaDP.isAllyTeam(vInfoVO.team) and vInfoVO.vehicleID != arenaDP.getPlayerVehicleID():
                self.__isSquadMode = True

        self.__teamsCount = len(set(self.__vehicleTeams.values()))
