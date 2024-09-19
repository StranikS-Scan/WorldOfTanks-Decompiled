# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/event.py
import typing
from constants import WT_TEAMS
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.postbattle.widget_model import WidgetModel
from gui.impl.lobby.wt_event.wt_quests_view import HUNTER_QUEST_CHAINS
from gui.server_events.event_items import WtQuest
from gui.server_events.events_constants import WT_BOSS_GROUP_ID
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.missions.packers.bonus import packMissionsBonusModelAndTooltipData, BonusUIPacker
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPackerMap
from helpers import dependency
from gui.server_events.bonuses import mergeBonuses
from skeletons.gui.game_control import IEventBattlesController, IQuestsController
from gui.wt_event.wt_event_helpers import BATTLE_QUEST_PREFIX
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_random_reward_item_model import FunRewardTypes
from gui.impl.gen.view_models.views.battle_royale.battle_results.personal.battle_reward_item_model import BattleRewardItemModel
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.widgets_model import WidgetsModel

def _getWtEventBonusPacker():
    mapping = getWtEventBonusPackerMap()
    return BonusUIPacker(mapping)


@dependency.replace_none_kwargs(gameEventCtrl=IEventBattlesController)
def _sortMap(gameEventCtrl=None):
    return {'stamp': 1,
     'wtevent_ticket': 2,
     gameEventCtrl.getConfig().ticketToken: 3,
     EventLootBoxes.WT_HUNTER: 4,
     EventLootBoxes.WT_BOSS: 5,
     FunRewardTypes.CRYSTALS.value: 6,
     FunRewardTypes.CREDITS.value: 7,
     'hunter_collection': 8,
     BattleRewardItemModel.BATTLE_PASS_POINTS: 9}


def setWidgets(model, tooltipData, reusable, _):
    isBoss = reusable.getPersonalTeam() == WT_TEAMS.BOSS_TEAM
    if isBoss:
        quests = _getQuests([WT_BOSS_GROUP_ID])
    else:
        quests = _getQuests(HUNTER_QUEST_CHAINS)
    progressData = reusable.progress.getQuestsProgress()
    completedQuests = []
    for qID, quest in quests:
        if qID not in progressData:
            continue
        _, pPrev, pCur = progressData[qID]
        isCompleted = pCur.get('bonusCount', 0) - pPrev.get('bonusCount', 0) > 0
        if isCompleted:
            completedQuests.append(quest)

    packer = _getWtEventBonusPacker()
    bonuses = []
    for quest in completedQuests:
        if isinstance(quest, WtQuest):
            bonuses.extend([ bonus for bonus in quest.getBonuses() if bonus.getName() in packer.getPackers() ])

    bonuses = mergeBonuses(bonuses)
    modelsArr = Array[WidgetModel]()
    tooltipDataQuests = {}
    packMissionsBonusModelAndTooltipData(bonuses, packer, modelsArr, tooltipDataQuests)
    if tooltipData is not None:
        tooltipData[BATTLE_QUEST_PREFIX] = tooltipDataQuests
    sortMap = _sortMap()
    widgetsArr = model.getWidgets()
    for bonusModel in sorted(modelsArr, key=lambda b: sortMap.get(b.getName(), len(sortMap))):
        widgetsArr.addViewModel(bonusModel)

    modelsArr.clear()
    return


def _getQuests(groupIDs):
    questController = dependency.instance(IQuestsController)

    def filterFunc(quest):
        return quest.isEventBattlesQuest() and quest.getGroupID() in groupIDs

    quests = questController.eventsCache.getAllQuests(filterFunc).items()
    return quests
