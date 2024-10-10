# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/events/event.py
import copy
import logging
import typing
from constants import WT_TEAMS
from gui.impl.gen.view_models.common.missions.event_model import EventStatus
from gui.impl.gen.view_models.views.lobby.postbattle.events.wt_event_quest_model import WtEventQuestModel
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.server_events import IEventsCache
from white_tiger.gui.impl.lobby.wt_quests_view import HUNTER_QUEST_CHAINS, MAX_VISIBLE_QUESTS
from gui.server_events.events_constants import WT_BOSS_GROUP_ID
from white_tiger.gui.impl.lobby.packers.wt_event_quest_data_packer import WTEventBattleQuestUIDataPacker
from helpers import dependency
from skeletons.gui.game_control import IQuestsController
from white_tiger_common.wt_constants import ARENA_BONUS_TYPE
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import ReusableInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.events.base_event_model import BaseEventModel
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(battleResults=IBattleResultsService)
def getEvents(tooltipData, reusable, result, battleResults=None):
    events = []
    cachedSettings = battleResults.presenter.cachedSettings[reusable.arenaUniqueID]
    actualQuests = cachedSettings.get('wtQuests', [])
    if not actualQuests:
        isBoss = reusable.getPersonalTeam() == WT_TEAMS.BOSS_TEAM
        if isBoss:
            quests = _getQuests(WT_BOSS_GROUP_ID, allowCompleted=True)
        else:
            quests = []
            for chainID in HUNTER_QUEST_CHAINS:
                harrierQuests = _getQuests(chainID, reverse=True)
                if not harrierQuests:
                    harrierQuests = _getQuests(chainID, allowCompleted=True, reverse=True)
                if not harrierQuests:
                    continue
                quests.append(harrierQuests[0])

        cachedSettings['wtQuests'] = [ copy.deepcopy(quest) for quest in quests ]
        actualQuests = cachedSettings['wtQuests']
    for _, quest in actualQuests[:MAX_VISIBLE_QUESTS]:
        packer = WTEventBattleQuestUIDataPacker(quest)
        model = WtEventQuestModel()
        events.append(packer.pack(model))
        tooltipData[quest.getID()] = packer.getTooltipData()
        if quest.isCompleted():
            model.setStatus(EventStatus.DONE)
            _markQuestProgressAsViewed(quest.getID())
        model.setCompletedMissions(quest.getBonusCount())
        model.setMaxMissions(quest.bonusCond.getBonusLimit())

    return events


def _getQuests(groupID, allowCompleted=False, reverse=False):
    questController = dependency.instance(IQuestsController)

    def isWhiteTigerQuest(quest):
        arenaTypes = quest.getArenaTypes()
        return set(arenaTypes) == {ARENA_BONUS_TYPE.WHITE_TIGER, ARENA_BONUS_TYPE.WHITE_TIGER_2} if arenaTypes else False

    def hasQuestProgressed(quest):
        return questController.eventsCache.questsProgress.hasQuestProgressed(quest.getID())

    def filterFunc(quest):
        return isWhiteTigerQuest(quest) and quest.getGroupID() == groupID and (quest.accountReqs.isAvailable() or allowCompleted and quest.isCompleted() and hasQuestProgressed(quest))

    quests = questController.eventsCache.getAllQuests(filterFunc).items()
    return sorted(quests, key=lambda item: item[1].getPriority(), reverse=reverse)


def _markQuestProgressAsViewed(questID):
    eventsCache = dependency.instance(IEventsCache)
    eventsCache.questsProgress.markQuestProgressAsViewed(questID)
