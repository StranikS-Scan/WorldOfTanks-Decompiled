# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/personal_missions.py
import pm_quests
g_cache = None
g_operationsCache = None
g_campaignsCache = None
PERSONAL_MISSIONS_XML_PATH = pm_quests.PM_QUEST_XML_PATH

class PM_BRANCH(pm_quests.PM_BRANCH):
    ACTIVE_BRANCHES = (pm_quests.PM_BRANCH.REGULAR, pm_quests.PM_BRANCH.PERSONAL_MISSION_2, pm_quests.PM_BRANCH.PERSONAL_MISSION_3)
    OLD_BRANCHES = (pm_quests.PM_BRANCH.REGULAR, pm_quests.PM_BRANCH.PERSONAL_MISSION_2)


def isPersonalMissionsEnabled(gameParams, branch):
    return not pm_quests.isPMQuestBranchEnabled(gameParams, branch)


class PM_STATE(pm_quests.PM_STATE):
    pass


class PM_FLAG(pm_quests.PM_FLAG):
    pass


PM_BRANCH_TO_FREE_TOKEN_NAME = pm_quests.PM_BRANCH_TO_FREE_TOKEN_NAME
PM_BRANCH_TO_FINAL_PAWN_COST = pm_quests.PM_BRANCH_TO_FINAL_PAWN_COST
PM_REWARD_BY_DEMAND = pm_quests.PM_REWARD_BY_DEMAND

def init():
    global g_cache
    global g_campaignsCache
    global g_operationsCache
    pm_quests.g_seasonCache = pm_quests.SeasonCache()
    pm_quests.g_tileCache = pm_quests.TileCache()
    g_campaignsCache = CampaignsCache()
    g_operationsCache = OperationsCache()
    g_cache = PMCache()


class CampaignsCache(pm_quests.SeasonCache):

    def getCampaignInfo(self, campaignID):
        return self.getSeasonInfo(campaignID)


class OperationsCache(pm_quests.TileCache):

    def getOperationInfo(self, operationID):
        return self.getTileInfo(operationID)


class PMCache(pm_quests.PMCache):

    def questByPersonalMissionID(self, missionID):
        return self.questByPMQuestID(missionID)

    def hasMission(self, missionID):
        return self.hasPMQuest(missionID)

    def isPersonalMission(self, uniqueQuestID):
        return self.isPMQuest(uniqueQuestID)

    def questListByOperationIDChainID(self, tileID, chainID):
        return self.questListByTileIDChainID(tileID, chainID)

    def finalMissionIDsByOperationIDChainID(self, tileID, chainID):
        return self.finalpmQuestsIDsByTileIDChainID(tileID, chainID)

    def initialMissionQuestIDsByOperationIDChainID(self, tileID, chainID):
        return self.initialpmQuestsIDsByTileIDChainID(tileID, chainID)

    def getPersonalMissionIDByUniqueID(self, uniqueQuestID):
        return self.getPMQuestIDByUniqueID(uniqueQuestID)

    def branchByMissionID(self, pmQuestID):
        return self.branchByPMQuestID(pmQuestID)


class PMStorage(pm_quests.PMStorage):
    pass
