# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/events/event.py
import logging
import typing
from constants import WT_TEAMS
from gui.impl.gen.view_models.common.missions.event_model import EventStatus
from gui.impl.gen.view_models.views.lobby.postbattle.events.wt_event_quest_model import WtEventQuestModel
from gui.impl.lobby.wt_event.wt_quests_view import HUNTER_QUEST_CHAINS, MAX_VISIBLE_QUESTS
from gui.server_events.events_constants import WT_BOSS_GROUP_ID
from gui.wt_event.wt_event_quest_data_packer import WTEventBattleQuestUIDataPacker
from helpers import dependency
from skeletons.gui.game_control import IQuestsController
if typing.TYPE_CHECKING:
    from typing import Dict
    from gui.server_events.event_items import WtQuest
    from gui.battle_results.reusable import ReusableInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.events.base_event_model import BaseEventModel
_logger = logging.getLogger(__name__)

def shouldAddQuest(quest, battleResult):
    shouldAdd = True
    for vehicleID in battleResult['personal']:
        if isinstance(vehicleID, int):
            questsProgress = battleResult['personal'][vehicleID].get('questsProgress', {})
            if quest.isCompleted():
                shouldAdd = False
            if quest.getID() not in questsProgress:
                continue
            _, __, currentProgress = questsProgress[quest.getID()]
            isQuestCompleted = currentProgress.get('bonusCount', 0) > 0
            if isQuestCompleted:
                shouldAdd = True

    return shouldAdd


def getEvents(tooltipData, reusable, result):
    events = []
    isBoss = reusable.getPersonalTeam() == WT_TEAMS.BOSS_TEAM
    if isBoss:
        quests = _getQuests(WT_BOSS_GROUP_ID)
    else:
        quests = []
        for chainID in HUNTER_QUEST_CHAINS:
            harrierQuests = _getQuests(chainID, reverse=True)
            if not harrierQuests:
                harrierQuests = _getQuests(chainID, allowCompleted=True, reverse=True)
            if not harrierQuests:
                _logger.error("Can't find quests for group %s", chainID)
                continue
            quests.append(harrierQuests[0])

    for _, quest in quests[:MAX_VISIBLE_QUESTS]:
        if not shouldAddQuest(quest, result):
            continue
        packer = WTEventBattleQuestUIDataPacker(quest)
        model = WtEventQuestModel()
        events.append(packer.pack(model))
        tooltipData[quest.getID()] = packer.getTooltipData()
        if quest.isCompleted():
            model.setStatus(EventStatus.DONE)

    return events


def _getQuests(groupID, allowCompleted=False, reverse=False):
    questController = dependency.instance(IQuestsController)

    def filterFunc(quest):
        return quest.isEventBattlesQuest() and quest.getGroupID() == groupID and (quest.accountReqs.isAvailable() or allowCompleted and quest.isCompleted())

    quests = questController.eventsCache.getAllQuests(filterFunc).items()
    return sorted(quests, key=lambda item: item[1].getPriority(), reverse=reverse)
