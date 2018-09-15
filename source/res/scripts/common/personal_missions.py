# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/personal_missions.py
import potapov_quests
g_cache = None
g_operationsCache = None
g_campaignsCache = None
PERSONAL_MISSIONS_XML_PATH = potapov_quests.POTAPOV_QUEST_XML_PATH

class PM_BRANCH(potapov_quests.PQ_BRANCH):
    pass


def isPersonalMissionsEnabled(gameParams, branch):
    return not potapov_quests.isPotapovQuestEnabled(gameParams, branch)


class PM_STATE(potapov_quests.PQ_STATE):
    pass


PM_REWARD_BY_DEMAND = potapov_quests.PQ_REWARD_BY_DEMAND

def init():
    global g_cache
    global g_campaignsCache
    global g_operationsCache
    potapov_quests.g_seasonCache = potapov_quests.SeasonCache()
    potapov_quests.g_tileCache = potapov_quests.TileCache()
    g_campaignsCache = CampaignsCache()
    g_operationsCache = OperationsCache()
    g_cache = PMCache()


class CampaignsCache(potapov_quests.SeasonCache):

    def getCampaignInfo(self, campaignID):
        return self.getSeasonInfo(campaignID)


class OperationsCache(potapov_quests.TileCache):

    def getOperationInfo(self, operationID):
        return self.getTileInfo(operationID)


class PMCache(potapov_quests.PQCache):

    def questByPersonalMissionID(self, missionID):
        return self.questByPotapovQuestID(missionID)

    def hasMission(self, missionID):
        return self.hasPotapovQuest(missionID)

    def isPersonalMission(self, uniqueQuestID):
        return self.isPotapovQuest(uniqueQuestID)

    def questListByOperationIDChainID(self, tileID, chainID):
        return self.questListByTileIDChainID(tileID, chainID)

    def finalMissionIDByOperationIDChainID(self, tileID, chainID):
        return self.finalPotapovQuestIDByTileIDChainID(tileID, chainID)

    def initialMissionQuestIDByOperationIDChainID(self, tileID, chainID):
        return self.initialPotapovQuestIDByTileIDChainID(tileID, chainID)

    def getPersonalMissionIDByUniqueID(self, uniqueQuestID):
        return self.getPotapovQuestIDByUniqueID(uniqueQuestID)

    def branchByMissionID(self, potapovQuestID):
        return self.branchByPotapovQuestID(potapovQuestID)


class PMStorage(potapov_quests.PQStorage):
    pass
