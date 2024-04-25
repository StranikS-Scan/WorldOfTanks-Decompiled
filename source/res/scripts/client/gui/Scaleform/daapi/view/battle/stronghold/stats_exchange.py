# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/stronghold/stats_exchange.py
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController
from gui.impl import backport
from gui.impl.gen import R

class StrongholdStatisticDataController(ClassicStatisticsDataController):

    def __init__(self):
        super(StrongholdStatisticDataController, self).__init__()
        self.__needToShowEnemyTeamName = False

    def invalidateVehiclesInfo(self, arenaDP):
        self._updatePersonalPrebattleID(arenaDP)
        self._updateSquadRestrictions()
        exchange = self._exchangeBroker.getVehiclesInfoExchange()
        from gui.battle_control.arena_info import vos_collections
        collection = vos_collections.VehiclesInfoCollection()
        for vInfoVO in collection.iterator(arenaDP):
            if vInfoVO.isObserver():
                continue
            isEnemy, overrides = self._getTeamOverrides(vInfoVO, arenaDP)
            if isEnemy:
                if self.__needToShowEnemyTeamName and self.sessionProvider.arenaVisitor.isArenaFogOfWarEnabled():
                    self._setArenaDescriptionWithEnemy()
                    self.__needToShowEnemyTeamName = False
            with exchange.getCollectedComponent(isEnemy) as item:
                item.addVehicleInfo(vInfoVO, overrides)

        exchange.addSortIDs(arenaDP, False, True)
        data = exchange.get()
        if data:
            self.as_setVehiclesDataS(data)

    def addVehicleInfo(self, vo, arenaDP):
        isEnemy, overrides = self._getTeamOverrides(vo, arenaDP)
        exchange = self._exchangeBroker.getVehiclesInfoExchange()
        with exchange.getCollectedComponent(isEnemy) as item:
            item.addVehicleInfo(vo, overrides)
        exchange.addSortIDs(arenaDP, isEnemy)
        if isEnemy:
            if self.sessionProvider.arenaVisitor.isArenaFogOfWarEnabled():
                self._setArenaDescriptionWithEnemy()
        data = exchange.get()
        if data:
            self.as_addVehiclesInfoS(data)

    def _setArenaDescription(self):
        battleCtx = self._battleCtx
        questProgress = self.sessionProvider.shared.questProgress
        enemyText = backport.text(R.strings.ingame_gui.statistics.tab.line_up.enemy())
        visitor = self.sessionProvider.arenaVisitor
        if visitor.isArenaFogOfWarEnabled():
            enemyTeamName = enemyText
            self.__needToShowEnemyTeamName = True
        else:
            enemyTeamName = battleCtx.getTeamName(enemy=True)
        arenaInfoData = {'mapName': battleCtx.getArenaTypeName(),
         'winText': battleCtx.getArenaWinString(),
         'winTextShort': self._getArenaWinTextShort(),
         'battleTypeLocaleStr': battleCtx.getArenaDescriptionString(isInBattle=False),
         'battleTypeIconPathBig': battleCtx.getBattleTypeIconPathBig(),
         'battleTypeIconPathSmall': battleCtx.getBattleTypeIconPathSmall(),
         'allyTeamName': battleCtx.getTeamName(enemy=False),
         'enemyTeamName': enemyTeamName}
        self.as_setArenaInfoS(arenaInfoData)
        selectedQuest = questProgress.getSelectedQuest()
        if selectedQuest:
            self.as_setQuestStatusS(self.__getStatusData(selectedQuest))

    def _setArenaDescriptionWithEnemy(self):
        battleCtx = self._battleCtx
        arenaInfoData = {'mapName': battleCtx.getArenaTypeName(),
         'winText': battleCtx.getArenaWinString(),
         'winTextShort': self._getArenaWinTextShort(),
         'battleTypeLocaleStr': battleCtx.getArenaDescriptionString(isInBattle=False),
         'battleTypeIconPathBig': battleCtx.getBattleTypeIconPathBig(),
         'battleTypeIconPathSmall': battleCtx.getBattleTypeIconPathSmall(),
         'allyTeamName': battleCtx.getTeamName(enemy=False),
         'enemyTeamName': battleCtx.getTeamName(enemy=True)}
        self.as_setArenaInfoS(arenaInfoData)
